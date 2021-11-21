import mimetypes
import aiohttp
import ast
import asyncio

if __name__ == '__main__':
    import exceptions
else:
    from . import exceptions

# TODO: Deal with global flags.
# TODO: Deal with user-defined flags.

class visitNode(ast.NodeVisitor):
    def __init__(self):
        self.nodesCalled = []
        self.foundFor = False
        self.foundWhile = False
        self.foundTry = False
        self.foundSlice = False
        pass

    def visit_Call(self, node: ast.Call):
        self.nodesCalled.append(node)
        # return super().visit_Call(node)

    def visit_For(self, node: ast.For):
        self.foundFor = True
    
    def visit_While(self, node: ast.While):
        self.foundWhile = True

    def visit_Try(self, node: ast.Try):
        self.foundTry = True

    def visit_Subscript(self, node: ast.Subscript):
        if isinstance(node.slice, ast.Slice):
            self.foundSlice = True

class Autograder(object):
    def __init__(self, url: str, flags: list):
        self.url = url
        self.globalFlags = flags
        self.functionCode = {}
        self.functionNames = []

    # Deal's with fetching and running basic tests on the python file.
    # Not in __init__ due to needing async capabilities.
    async def fetch(self):
        # Check if file mime is text/application
        if mimetypes.guess_type(self.url)[0] != 'text/x-python':
            raise exceptions.invalidPython('Invalid file type passed.')
        
        # Check if file contains proper Python
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as response:
                self.file = await response.text()
                try:
                    self.parsed = ast.parse(self.file)
                except SyntaxError:
                    raise exceptions.invalidPython('Invalid python file passed.')
        # Run some default checks.
        self.defaultChecks()
        self.functionDefinitions()

    def functionDefinitions(self):
        for statement in self.parsed.body:
            if isinstance(statement, ast.FunctionDef):
                self.functionCode[statement.name] = statement
                self.functionNames.append(statement.name)

    def getFunctionCalls(self, function):
        for func in self.functionCode:
            funcStatement = self.functionCode[func]
            if funcStatement.name == function:
                a = visitNode()
                a.visit(funcStatement)
                return a.nodesCalled
    
    def getSelfFunctionCalls(self, function):
        functions = self.getFunctionCalls(function)
        funcs = []
        for func in functions:
            if isinstance(func.func, ast.Name) and func.func.id in self.functionNames:
                funcs.append(func)
        return funcs

    ## DETECTION FUNCTIONS ##

    # Default checks.
    def defaultChecks(self):
        allowedStatements = ['math']
        for statement in self.parsed.body:
            # Checks if any __x__ functions are being called.
            if isinstance(statement, ast.Expr) and isinstance(statement.value, ast.Call): 
                funcCall = statement.value.func.id
                if funcCall[:2] == '__' and funcCall[-2:] == '__':
                    raise exceptions.illegalImport(f'Use of {funcCall} not allowed.')

    def checkImports(self, illegalImports: list):
        for statement in self.parsed.body:
            if isinstance(statement, ast.Import):
                for importt in statement.names:
                    if importt.name in illegalImports:
                        raise exceptions.illegalImport(f'Import of module {importt.name} not allowed.')
            break

    def checkFlags(self, function, flags):
        metFlags = [True]
        if 'recursive' in flags and not self.detectRecursion(function):
            metFlags.append('recursive')
            metFlags[0] = False
        if 'noLoops' in flags and not self.detectLoops(function):
            metFlags.append('noLoops')
            metFlags[0] = False
        if 'tryExcept' in flags and not self.detectTryExcept(function):
            metFlags.append('tryExcept')
            metFlags[0] = False
        if 'stringIndexing' in flags and not self.detect(function):
            pass

    def detectRecursion(self, function, running=[]):
        funcs = self.getSelfFunctionCalls(function)

        if len(running) > 10:
            lastThree = running[-3:]
            if lastThree == lastThree[::-1]:
                return True
            else:
                return False

        for func in funcs:
            name = func.func.id
            running.append(name)
            if not self.detectRecursion(name, running):
                continue
            else:
                return True
        else:
            return False


    def detectLoops(self, function, seenFuncs=set()):
        # Checks if while/for loops are used witin main function.
        mainFunc = visitNode()
        mainFunc.visit(self.functionCode[function])
        
        if function in seenFuncs:
            return mainFunc.foundWhile or mainFunc.foundFor
        seenFuncs.add(function)

        if mainFunc.foundWhile or mainFunc.foundFor:
            return True
        else:
            # Checks if any helper function use while/for loops.
            funcs = self.getSelfFunctionCalls(function)
            for func in funcs:
                a = visitNode()
                a.visit(self.functionCode[func.func.id])
                if a.foundWhile or a.foundFor:
                    return True
                else:
                    # Only recurse if current function is calling other helper functions.
                    if self.getSelfFunctionCalls(func.func.id) != []:
                        return self.detectLoops(func.func.id, seenFuncs)
            return False

    def detectTryExcept(self, function, seenFuncs=set()):
        # Checks if main function has try/except
        mainFunc = visitNode()
        mainFunc.visit(self.functionCode[function])
        # If it uses try/except, we are done.
        if mainFunc.foundTry: return True

        # Otherwise, loop through all the helper functions.
        if function in seenFuncs:
            return mainFunc.foundTry
        seenFuncs.add(function)

        funcs = self.getFunctionCalls(function)
        for func in funcs:
            a = visitNode()
            a.visit(self.functionCode[func.func.id])
            if a.foundTry: return True
            if self.getFunctionCalls(func.func.id) != []: return self.detectTryExcept(function, seenFuncs)
        return False

    def detectSlice(self, function, seenFuncs=set()):
        mainFunc = visitNode()
        mainFunc.visit(self.functionCode[function])
        if mainFunc.foundSlice: return True

        if function in seenFuncs:
            return mainFunc.foundSlice
        seenFuncs.add(function)

        funcs = self.getFunctionCalls(function)
        for func in funcs:
            a = visitNode()
            a.visit(self.functionCode[func.func.id])
            if a.foundSlice: return True
            if self.getFunctionCalls(func.func.id) != []: return self.detectSlice(function, seenFuncs)
        return False

    ## TEST CASE FUNCTIONS ##

    # Deals with running the right command for the specific type of function.
    def injectTestCase(self, tests, function, retType):
        if function not in self.functionNames:
            raise exceptions.missingFunction(f'{function} not defined.')
        
        if retType == 'return':
            return self.attachReturnTestCases(tests, function)
        elif retType == 'print':
            return self.attachPrintTestCases(tests, function)
        elif retType == 'destructive':
            return self.attachNDestructive(tests, function, True)
        elif retType == 'notDestrucitve':
            return self.attachNDestructive(tests, function, False)
        elif retType == 'oop':
            return self.attachOOPTestCases(tests, function)
        

    def attachReturnTestCases(self, tests, function):
        file = self.file
        print(tests)
        for test in tests:
            #{function}({json.dumps(str(test))})
            file += f'''
if locals()['autograder'].get('{function}', None) == None:
    locals()['autograder']['{function}'] = []
try:
    locals()['autograder']['{function}'].append( (None, {function}({test}) == {tests[test]}, {tests[test]}, {function}({test})) )
except Exception as err:
    locals()['autograder']['{function}'].append( (None, None, {tests[test]}, type(err).__name__ + ': ' + str(err)) )
            '''
        return file

#https://www.kite.com/python/answers/how-to-redirect-print-output-to-a-variable-in-python
    def attachPrintTestCases(self, tests, function):
        overwritePrint = '''import io
import sys
newOutput = io.StringIO()
sys.stdout = newOutput
'''
        file = overwritePrint + self.file
        for test in tests:
            file += f'''
if locals()['autograder'].get('{function}', None) == None:
    locals()['autograder']['{function}'] = []
try:
    {function}({test})
    locals()['autograder']['{function}'].append( (None, newOutput.getvalue()[:-1] == {tests[test]}, {tests[test]}, newOutput.getvalue()[:-1]) )
    newOutput = io.StringIO()
    sys.stdout = newOutput
except Exception as err:
    locals()['autograder']['{function}'].append( (None, None, {tests[test]}, type(err).__name__ + ': ' + str(err)) )
            '''
        return file
    
    def attachOOPTestCases(self, tests, function):
        pass

    def attachNDestructive(self, tests, function, destructive):
        pass

async def main():
    myAuto = Autograder('https://s.matc.io/recursive.py', [])
    # myAuto = Autograder('https://s.matc.io/hw6.py', [])
    await myAuto.fetch()
    # print(myAuto.functionNames)
    # x = myAuto.getFunctionCalls('capitalizeWords')
    # x = myAuto.detectRecursion('capitalizeWords')
    # x = myAuto.detectRecursion('fF')
    # x = myAuto.detectLoops('withBoth')
    # x = myAuto.detectTryExcept('divideByZero')
    x = myAuto.detectSlice('stringSlice')
    # print(ast.dump(myAuto.parsed))
    # print(myA)
    print(x)

if __name__ == "__main__":
    # testCases = json.load(open('testCases.json', 'r'))
    # testCases["decodeList"]

    # myAuto = Autograder('https://s.matc.io/hw3.py')
    # myAuto.run()
    # myAuto.attachTestCases(testCases)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())