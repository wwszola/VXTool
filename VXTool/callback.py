from typing import Callable
from multiprocessing import Process, Queue
import re
from queue import Empty as QueueEmpty

from pygame import KEYDOWN, KEYUP
from pygame import MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION
from pygame.key import name as key_name

from VXTool.render import RenderStoreProxy
from VXTool.core import Dot, Buffer
from VXTool.app import PickableEvent, ACTION_MSG


class CallbackProcess(Process):
    _event_handler_pattern: re.Pattern = re.compile(
        pattern = r"^on_(?P<name>[a-z0-9]+)(?:_{1}(?P<attr>\w+))*$",
        flags = re.IGNORECASE
    )
    def __init__(self, msg_q: Queue, render_q: Queue, event_q: Queue, render_store_proxy: RenderStoreProxy):
        super().__init__()
        self._msg_q: Queue = msg_q
        self._render_q: Queue = render_q
        self._event_q: Queue = event_q
        self._render_store_proxy: RenderStoreProxy = render_store_proxy
        self.updates_count: int = 0

        self._event_handlers: dict[str, Callable] = dict()
        self._prepare_event_handlers()

        self._hash_to_dot: dict[int, Dot] = dict()

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

        self._render_q.cancel_join_thread()

    def _prepare_event_handlers(self):
        for key in dir(self):
            name_match: re.Match = re.match(CallbackProcess._event_handler_pattern, key)
            if not name_match:
                continue
            value = getattr(self, key)
            if not callable(value):
                continue
            name = name_match.group('name').upper()
            attr = name_match.groupdict().get('attr')
            attr = '' if attr is None else attr
            attr = attr.upper()
            self._event_handlers[(name, attr)] = value
        print(self._event_handlers.keys())

    def _dispatch_events(self, block = True, timeout = None):
        events: list[PickableEvent] = self._event_q.get(block, timeout)
        # print("DISPATCH EVENTS: ", [(event.type_name, event.attrs) for event in events])
        for event in events:
            handler = None
            name = event.type_name.upper()
            attr = ''
            if event.type in (KEYDOWN, KEYUP):
                attr = key_name(event.attrs['key']).replace(' ', '_').upper()
                event.attrs['key_name'] = attr
            elif event.type in (MOUSEBUTTONDOWN, MOUSEBUTTONUP):
                attr = str(event.attrs['button'])
            elif event.type == MOUSEMOTION:
                attr = ''
            handler = self._event_handlers.get((name, attr), None)
            if handler:
                handler(event.attrs)
    
    def send(self, buffer: Buffer, clear: bool = True, quit: bool = False):
        entry = []
        for pos, dots in buffer._container.items():
            entry.append(pos)
            entry.append(len(dots))
            for dot in dots:
                hash_value = hash(dot)
                if not self._render_store_proxy.is_registered(hash_value):
                    self._render_store_proxy.register(hash_value, dot)
                entry.append(hash_value)

        self._msg_q.put(ACTION_MSG.CLEAR)
        self._msg_q.put(ACTION_MSG.RENDER)
        self._render_q.put(entry)
        self._msg_q.put(ACTION_MSG.UPDATE)

    def setup(self):
        pass

    def update(self):
        pass
