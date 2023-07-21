import multiprocessing as mp
from queue import Empty as QueueEmpty

from VXTool.core import Dot, Buffer, Color

class Producer(mp.Process):
    def __init__(self, queue):
        super().__init__()
        self._queue: mp.Queue = queue

    def run(self):
        for i in range(5):
            self._queue.put(Dot(pos=(i,i*2), color=Color(125, 195, 215)))

class Consumer(mp.Process):
    def __init__(self, queue):
        super().__init__()
        self._queue: mp.Queue = queue

    def run(self):
        while True:
            try:
                dot: Dot = self._queue.get(timeout = 1)
                print(dot)
            except QueueEmpty:
                break

if __name__ == "__main__":
    queue = mp.Queue()
    p = Producer(queue)
    c = Consumer(queue)
    p.start()
    c.start()
    p.join()
    c.join()