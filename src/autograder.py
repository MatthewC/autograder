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
    def __init__(self, code):
        self.nodesCalled = []
        pass

    def visit_Call(self, node: ast.Call):
        self.nodesCalled.append(node)
        # return super().visit_Call(node)

class Autograder(object):
    def __init__(self, url: str, flags: list):
        self.url = url
        self.globalFlags = flags
        self.functions = []
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
                self.functions.append(statement)
                self.functionNames.append(statement.name)

    def getFunctionCalls(self, function):
        for func in self.functions:
            if func.name == function:
                a = visitNode('')
                a.visit(func)
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
    x = myAuto.detectRecursion('fF')
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

