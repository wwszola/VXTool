from typing import Callable
from multiprocessing import Process, Queue
import re
from queue import Empty as QueueEmpty

from pygame import KEYDOWN, KEYUP
from pygame import MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION
from pygame.key import name as key_name

from VXTool.render import RENDER_MSG
from VXTool.core import Dot, Buffer
from VXTool.app import PickableEvent


class CallbackProcess(Process):
    _event_handler_pattern: re.Pattern = re.compile(
        pattern = r"^on_(?P<name>[a-z0-9]+)(?:_{1}(?P<attr>\w+))*$",
        flags = re.IGNORECASE
    )
    def __init__(self, widgets_info: dict, fonts_info: dict, user_settings: dict, event_frame_q: Queue):
        super().__init__()
        self.widgets_info: dict = widgets_info
        self.fonts_info: dict = fonts_info
        self.user_settings: dict = user_settings
        self.event_frame_q: Queue[list[PickableEvent]] = event_frame_q
        self.updates_count: int = 0

        self._event_handlers: dict[str, Callable] = dict()
        self._prepare_event_handlers()

        self._hash_to_dot: dict[int, Dot] = dict()

        print(f"\nCallback setup: {self.widgets_info} {self.fonts_info} {self.user_settings} {self._event_handlers.keys()} ")

        self.running = False

    def run(self):
        self.setup()
        self.running = True
        while self.running:
            try:
                self._dispatch_events(block = True, timeout=1.0)
                self.update()
                self.updates_count += 1
                # print(f"CALLBACK FRAMES NO. {self.updates_count} {str(self.running)}")
            except QueueEmpty:
                self.running = False

        # try:
        #     self.event_frame_q.get_nowait()
        # except QueueEmpty:
        #     pass
        
        for info in self.widgets_info.values():
            # info['render_q'].close()
            info['render_q'].cancel_join_thread()

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

    def screen_to_grid(self, widget_name: str, screen_pos: tuple[int, int]):
        x, y = screen_pos
        x -= self.widgets_info[widget_name]['inv_translation'][0]
        x *= self.widgets_info[widget_name]['inv_scale'][0]
        y -= self.widgets_info[widget_name]['inv_translation'][1]
        y *= self.widgets_info[widget_name]['inv_scale'][1]
        return x, y

    def _buffer_to_data(self, buffer: Buffer):
        data = []
        new_dots = []
        for pos, dots in buffer._container.items():
            data.append(pos)
            data.append(len(dots))
            for dot in dots:
                _hash = hash(dot)
                if _hash not in self._hash_to_dot:
                    real_dot = dot.variant(Dot) if dot.__class__ != Dot else dot
                    self._hash_to_dot[_hash] = real_dot
                    new_dots.append((_hash, real_dot))
                data.append(_hash)
        return data, new_dots

    def send(self, widget_name: str, buffer: Buffer, flags: RENDER_MSG = RENDER_MSG.DEFAULT, *args):
        if widget_name in self.widgets_info:
            entry = [flags, *args]
            if not flags & RENDER_MSG.NO_CHANGE:
                if not buffer:
                    raise ValueError('add RENDER_MSG.NO_CHANGE flag to send without the buffer.')                   
                if flags & RENDER_MSG.REGISTER_DOTS:
                    raise ValueError('add RENDER_MSG.NO_CHANGE to register dots with RENDER_MSG.REGISTER_DOTS')

                data, new_dots = self._buffer_to_data(buffer)
                if new_dots:
                    entry[0] = entry[0] | RENDER_MSG.REGISTER_DOTS
                    entry.append(new_dots)
                entry.append(data)

            # print(f'CALLBACK ENTRY: {entry}')
            self.widgets_info[widget_name]['render_q'].put(tuple(entry), block=False)

    def setup(self):
        pass

    def update(self):
        pass
