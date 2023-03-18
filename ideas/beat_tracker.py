from itertools import pairwise

from pygame.time import get_ticks, set_timer
from pygame import USEREVENT

PRIMARY_BEAT = USEREVENT + 1
class BeatTracker():
    def __init__(self, counting: int = 4, duration: int = 1000):
        """duration in miliseconds
        """
        self._counting: int = counting
        self._triggers: list[int] = list()
        self._beats: list[int] = list()
        self._duration: int = duration
        self._forcing: bool = False

    @property
    def duration(self):
        length = len(self._triggers)
        if length >= 2:
            average = sum(map(
                lambda x: x[1] - x[0], 
                pairwise(self._triggers)
            )) / (length - 1)
            self._duration = int(average)
        return self._duration

    def _is_trigger_onbeat(self, t):
        if self._beats:
            prev = self._beats[-1]
            diff = t - prev
            return diff > -self.duration * 0.5 and diff < self.duration * 0.5
        else:
            prev = self._triggers[-1]
            diff = t - prev
            return diff > 0 and diff < self.duration * 4

    def trigger(self, t: int):
        length = len(self._triggers)

        if length < 2:
            self._triggers.append(t)
            return
        
        if not self._is_trigger_onbeat(t):
            self._triggers.clear()
            self._triggers.append(t)
            return
        
        self._triggers.append(t)
        length += 1

        if length == self._counting:
            self.beat(t)
        
        if length > self._counting:
            self._triggers.pop(0)

    def beat(self, prev):
        now = get_ticks()
        next = prev + self.duration
        dt = next - now
        set_timer(PRIMARY_BEAT, dt, 1)
        self._beats.append(next)
        if len(self._beats) > self._counting:
            self._beats.pop(0)
        return next

    def stop(self):
        set_timer(PRIMARY_BEAT, 0)
        self._triggers.clear()
        self._beats.clear()