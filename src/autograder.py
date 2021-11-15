import mimetypes
import urllib.request
import json
import ast

from . import exceptions

# TODO: Deal with global flags.
# TODO: Deal with user-defined flags.

class Autograder(object):
    def __init__(self, url):
        # Check if file mim is text/application
        if mimetypes.guess_type(url)[0] != 'text/x-python':
            raise exceptions.invalidPython('Invalid file type passed.')
        self.url = url
        # Check if file contains proper Python
        with urllib.request.urlopen(self.url) as file:
            self.file = file.read().decode('utf-8')
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
            # Checks if any weird __x__ functions are being called.
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
        
        

if __name__ == "__main__":
    # myAuto = Autograder('https://s.matc.io/hw3.py')
    # myAuto.checkImports(['math'])
    # myAuto = Autograder('https://s.matc.io/index.htm')


    # Maybe fix.

    # myAuto = Autograder('https://s.matc.io/sample.py')
    # print(ast.dump(myAuto.parsed))

    testCases = json.load(open('testCases.json', 'r'))
    testCases["decodeList"]

    myAuto = Autograder('https://s.matc.io/hw3.py')
    myAuto.attachTestCases(testCases)
    print(myAuto.file)