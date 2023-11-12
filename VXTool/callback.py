import re
from multiprocessing import Process, Queue
from queue import Empty as QueueEmpty
from typing import Callable

from pygame import KEYDOWN, KEYUP, MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION
from pygame.key import name as key_name

from VXTool.app import ACTION_MSG, PickableEvent
from VXTool.core import Buffer, Dot


class CallbackProcess(Process):
    _event_handler_pattern: re.Pattern = re.compile(
        pattern=r"^on_(?P<name>[a-z0-9]+)(?:_{1}(?P<attr>\w+))*$", flags=re.IGNORECASE
    )

    def __init__(self, msg_q: Queue, data_q: Queue, event_q: Queue):
        super().__init__()
        self._msg_q: Queue = msg_q
        self._data_q: Queue = data_q
        self._event_q: Queue = event_q
        self.updates_count: int = 0

        self._event_handlers: dict[str, Callable] = dict()
        self._prepare_event_handlers()

        self._registered_hashes: set[int] = set()

        self.running = False

    def run(self):
        self.setup()
        self.running = True
        while self.running:
            try:
                self._dispatch_events(True, 1.0)
                self.update()
                self.updates_count += 1
            except QueueEmpty:
                break

    def _prepare_event_handlers(self):
        for key in dir(self):
            name_match: re.Match = re.match(CallbackProcess._event_handler_pattern, key)
            if not name_match:
                continue
            value = getattr(self, key)
            if not callable(value):
                continue
            name = name_match.group("name").upper()
            attr = name_match.groupdict().get("attr")
            attr = "" if attr is None else attr
            attr = attr.upper()
            self._event_handlers[(name, attr)] = value
        print(self._event_handlers.keys())

    def _dispatch_events(self, block=True, timeout=None):
        events: list[PickableEvent] = self._event_q.get(block, timeout)
        for event in events:
            handler = None
            name = event.type_name.upper()
            attr = ""
            if event.type in (KEYDOWN, KEYUP):
                attr = key_name(event.attrs["key"]).replace(" ", "_").upper()
                event.attrs["key_name"] = attr
            elif event.type in (MOUSEBUTTONDOWN, MOUSEBUTTONUP):
                attr = str(event.attrs["button"])
            elif event.type == MOUSEMOTION:
                attr = ""
            handler = self._event_handlers.get((name, attr), None)
            if handler is None:
                handler = self._event_handlers.get((name, ""), None)
            if handler is not None:
                handler(event.attrs)

    def draw(self, buffer: Buffer):
        entry = []
        new_dots = []
        for pos, dots in buffer._container.items():
            entry.append(pos)
            entry.append(len(dots))
            for dot in dots:
                hash_value = hash(dot)
                if hash_value not in self._registered_hashes:
                    plain_dot = dot.variant(Dot) if dot.__class__ != Dot else dot
                    new_dots.append((hash_value, plain_dot))
                    self._registered_hashes.add(hash_value)
                entry.append(hash_value)

        if len(new_dots) > 0:
            self._msg_q.put(ACTION_MSG.REGISTER_DOTS)
            self._data_q.put(new_dots)

        self._msg_q.put(ACTION_MSG.RENDER)
        self._data_q.put(entry)

    def clear(self):
        self._msg_q.put(ACTION_MSG.CLEAR)

    def present(self):
        self._msg_q.put(ACTION_MSG.UPDATE)

    def quit(self):
        self._msg_q.put(ACTION_MSG.QUIT)
        self.running = False

    def setup(self):
        pass

    def update(self):
        pass
