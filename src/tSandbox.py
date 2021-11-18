import multiprocessing as mp
import copy
import json

class Sandbox(object):
    def __init__(self, cmd):
        self.cmd = cmd
        pass

    def runTest(self, q, i):
        q.put(f'Hello {i}')

    def run(self):
        # print(self.cmd)
        q = mp.Queue()
        p = mp.Process(target=self.runTest, args=(q, self.cmd))
        p.start()
        x = q.get()
        p.join()
        return x


if __name__ == '__main__':
    import autograder as ag

    testCases = json.load(open('testCases.json', 'r'))
    # Load file
    myAuto = ag('https://s.matc.io/hw3.py')
    myAuto.fetch()
    workers = []
    for test in testCases:
        file = myAuto.attachTestCases(testCases[test], test)
        p = mp.Process(target=Sandbox, args=(file, ))
        workers.append(p)
        p.start()