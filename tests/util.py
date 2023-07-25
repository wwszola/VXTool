import time


class Timer:
    def __init__(self, number, func):
        self.number = number
        self.func = func
        self.start_time = 0.0
        self.delta = 0.0
        self.average = 0.0

    def run(self):
        self.start_time = time.time()
        for i in range(self.number):
            (self.func)()
        self.delta = time.time() - self.start_time
        self.average = self.delta/self.number

        return self
    
    @property
    def stats(self) -> str:
        return f"(delta: {self.delta:.2}s average: {self.average:.2}s)"