import multiprocessing as mp
import multiprocessing.queues as mpq
import copy
import json
import asyncio

class Sandbox(object):
    def __init__(self):
        pass

    def runTest(self, q, file):
        x = copy.copy(globals())
        x['__name__'] = 'sandbox'
        # Stores the result of each test case.
        x['autograder'] = {}
        exec(file, x)
        q.put(x['autograder'])

    def run(self, file):
        # print(self.cmd)
        q = mp.Queue()
        p = mp.Process(target=self.runTest, args=(q, file))
        p.start()
        try:
            x = q.get(timeout=30)
            p.join()
            if not isinstance(x, Exception):
                return x
        except mpq.Empty:
            p.terminate()
            print('oh')


async def main():
    from autograder import Autograder as ag

    # testCases = json.load(open('testCases.json', 'r'))
    # Load file
    myAuto = ag('https://s.matc.io/hw3.py', [])
    # myAuto = ag('https://s.matc.io/timeoutTest.py', [])
    await myAuto.fetch()
    sand = Sandbox()
    print(sand.run(myAuto.file))
    # workers = []
    # for test in testCases:
    #     file = myAuto.attachTestCases(testCases[test], test)
    #     p = mp.Process(target=Sandbox, args=(file, ))
    #     workers.append(p)
    #     p.start()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())