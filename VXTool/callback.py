from typing import Callable
from multiprocessing import Process, Queue
import re
from queue import Empty as QueueEmpty

from pygame import KEYDOWN, KEYUP
from pygame.key import name as key_name

from VXTool.render import RENDER_MSG
from VXTool.core import Buffer
from VXTool.app import PickableEvent


class CallbackProcess(Process):
    _event_handler_pattern: re.Pattern = re.compile(
        pattern = r"^on_(?P<name>[a-z0-9]+)(?:_{1}(?P<attr>\w+))*$",
        flags = re.IGNORECASE
    )
    def __init__(self, widgets_info: dict, user_settings: dict, event_frame_q: Queue):
        super().__init__()
        self.widgets_info: dict = widgets_info
        self.user_settings: dict = user_settings
        self.event_frame_q: Queue[list[PickableEvent]] = event_frame_q
        self.updates_count: int = 0

        self._event_handlers: dict[str, Callable] = dict()
        self._prepare_event_handlers()

        print(f"\nCallback setup: {self.widgets_info} {self.user_settings} {self._event_handlers.keys()}")

        self.running = False
        self.setup()

    def run(self):
        # _callback(self.design, self.user_settings)
        self.running = True
        while self.running:
            try:
                self._dispatch_events(block = True, timeout=1.0)
                self.update()
                self.updates_count += 1
            except QueueEmpty:
                self.running = False

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

    def _dispatch_events(self, block = True, timeout = None):
        events = self.event_frame_q.get(block, timeout)
        print("DISPATCH EVENTS: ", [(event.type_name, event.attrs) for event in events])
        for event in events:
            handler = None
            name = event.type_name.upper()
            if event.type in (KEYUP, KEYDOWN):
                attr = key_name(event.attrs['key']).replace(' ', '_').upper()
                event.attrs['key_name'] = attr
                handler = self._event_handlers.get((name, attr), None)
            if not handler:
                handler = self._event_handlers.get((name, ''), None)
            if handler:
                handler(event.attrs)
    
    def send(self, widget_name: str, buffer: Buffer, flags: RENDER_MSG = RENDER_MSG.DEFAULT, *args):
        if widget_name in self.widgets_info:
            entry = [flags, *args]
            if not flags & RENDER_MSG.NO_CHANGE:
                if not buffer:
                    raise ValueError('add RENDER_MSG.NO_CHANGE flag to send without the buffer.')                   
                entry.append(buffer)
            print(f'CALLBACK ENTRY: {(flags, *args)}')
            self.widgets_info[widget_name]['render_q'].put(tuple(entry), block=False)

    def setup(self):
        pass

    def update(self):
        pass
