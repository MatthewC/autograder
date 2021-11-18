import mimetypes
import aiohttp
import json
import ast

import asyncio

# from . import exceptions
import exceptions

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
    def __init__(self, url):
        self.url = url

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

    # Default checks.
    def defaultChecks(self):
        allowedStatements = ['math']
        for statement in self.parsed.body:
            # Checks if any __x__ functions are being called.
            if isinstance(statement, ast.Expr) and isinstance(statement.value, ast.Call): 
                funcCall = statement.value.func.id
                if funcCall[:2] == '__' and funcCall[-2:] == '__':
                    raise exceptions.illegalImport(f'Use of {funcCall} not allowed.')

    def checkImports(self, illegalImports):
        for statement in self.parsed.body:
            if isinstance(statement, ast.Import):
                for importt in statement.names:
                    if importt.name in illegalImports:
                        raise exceptions.illegalImport(f'Import of module {importt.name} not allowed.')
            break
    
    def attachTestCases(self, tests, function):
        counter = 0
        file = self.file
        for test in tests[1]:
            file += f'''
locals()['autograder_points']["{function}_{counter}"] = {tests[0]}
locals()['autograder']["{function}_{counter}"] = ({function}({test}) == {tests[1][test]}, {tests[1][test]}, {function}({test}))
            '''
            counter += 1
        return file
        
    def getFunctionalCalls(self, function):
        for statement in self.parsed.body:
            if isinstance(statement, ast.FunctionDef):
                if statement.name == function:
                    a = visitNode(statement)
                    a.visit(statement)
                    return a.nodesCalled
    
    def detectRecursion(self, function, running=[]):
        funcs = self.getFunctionalCalls(function)
        if funcs == []:
            return False

        if len(running) > 10:
            print(running)
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

async def main():
    myAuto = Autograder('https://s.matc.io/recursive.py')
    await myAuto.fetch()
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

