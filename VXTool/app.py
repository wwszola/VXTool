from typing import Generator

import pygame
from pygame.font import Font
from pygame.time import Clock
from pygame.image import save
from pygame import QUIT, KEYDOWN, KEYUP, MOUSEBUTTONDOWN, MOUSEBUTTONUP
from pygame import KMOD_CTRL

from .render import TextRender

def _app(_SETTINGS: dict):
    project_dir = _SETTINGS['USER']['project_dir']
    out_dir = _SETTINGS['USER']['out_dir']

    pygame.init()
    render_size = _SETTINGS['APP']['render_size']
    screen = pygame.display.set_mode(render_size)

    pygame.font.init()
    for name, data in _SETTINGS['APP']['preload_fonts'].items():
        path = data[0]
        family = _SETTINGS['USER']['fonts'][name] = {}
        try: 
            for size in data[1:]:
                font = Font(project_dir / path, size)
                family[size] = font            
        except FileNotFoundError as e:
            print(e.msg)

    record = _SETTINGS['APP'].get('record', None)
    quit = _SETTINGS['APP'].get('quit', None)

    design = TextRender(**_SETTINGS['TEXT_RENDER'])
    
    action: Generator = _SETTINGS['APP']['_callback'](design, _SETTINGS['USER'])
    running = next(action, False)
    clock = Clock()
    frame = 0
    while running:
        running = not pygame.event.peek(QUIT)
        
        keydowns = pygame.event.get(KEYDOWN)
        captured = filter(lambda event: bool(event.mod & KMOD_CTRL), keydowns)
        for event in captured:
            match (event.key):
                case pygame.K_q:
                    running = False
                case pygame.K_s:
                    save(screen, out_dir / f'frame_{frame:0>5}.png')
                case pygame.K_r:
                    record = (frame, 999999)

        result = action.send(keydowns)
        if not result:
            running = False

        render = design.img()
        
        screen.fill(_SETTINGS['APP']['backcolor'])
        screen.blit(
            render,
            render.get_rect(center = screen.get_rect().center))

        pygame.display.update()

        if record and record[0] <= frame < record[1]:
            save(screen, out_dir / f'frame_{frame:0>5}.png')

        if quit and frame >= quit:
            running = False
            
        frame += 1
        real_fps = 1000/clock.tick(_SETTINGS['APP']['FPS'])
        pygame.display.set_caption(f'{real_fps:.2}')

    pygame.quit()