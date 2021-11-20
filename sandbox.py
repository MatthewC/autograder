import multiprocessing as mp
import copy
import json

from src import autograder

def evalCode(file):
    x = copy.copy(globals())
    x['__name__'] = 'sandbox'
    # Stores the result of each test case.
    x['autograder'] = {}
    x['autograder_points'] = {}
    exec(file, x)
    for element in x['autograder']:
        y = x['autograder'][element]
        z = x['autograder_points'][element]
        if y[0] == False:
            print(f'Expected: {y[1]}\nGot: {y[2]}\nLost Points: {z}')
    # q.put('a')

# if __name__ == '__main__':
#     testCases = json.load(open('testCases.json', 'r'))
#     # Load file
#     myAuto = ag('https://s.matc.io/hw3.py')
#     for test in testCases:
#         file = myAuto.attachTestCases(testCases[test])
#     # myAuto.file += '\nprint(__name__)'
#     # print(myAuto.file)

#     # Runs evalCode as a seperate process.
#     ctx = mp.get_context('spawn')
#     q = ctx.Queue()
#     p = ctx.Process(target=evalCode, args=(myAuto.file,))
#     p.start()
#     p.join()
#     # print('a hello')
#     # print('b hello')
#     # p.join()

#     # print('hello')


if __name__ == '__main__':
    from src import Autograder as ag
    testCases = json.load(open('testCases.json', 'r'))
    # Load file
    myAuto = ag('https://s.matc.io/hw3.py')
    workers = []
    for test in testCases:
        file = myAuto.attachTestCases(testCases[test], test)
        p = mp.Process(target=evalCode, args=(file, ))
        workers.append(p)
        p.start()
    
    # 1 means fail
    # 0 means pass
    # None meins continuing