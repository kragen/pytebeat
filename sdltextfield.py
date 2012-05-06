#!/usr/bin/python
"""Text editor class for PyGame.

This is for my bytebeat livecoding performance software.

"""

import pygame
import time

class KeyRepeater(object):
    def __init__(self, target):
        self.last_keydown = None
        self.next_keyrepeat = None
        self.initial_autorepeat_delay = 0.25
        self.autorepeat_delay = 0.05

    def handle_keyevent(self, event, target):
        if event.type == pygame.KEYDOWN:
            self.last_keydown = event
            target.handle_key(event)
            self.next_keyrepeat = time.time() + self.initial_autorepeat_delay
        else:
            if self.last_keydown and event.key == self.last_keydown.key:
                self.last_keydown = None
                self.next_keyrepeat = None

    def poll(self, target):
        if self.last_keydown:
            now = time.time()
            while now > self.next_keyrepeat:
                target.handle_key(self.last_keydown)
                self.next_keyrepeat += self.autorepeat_delay


class TextField(object):
    def __init__(self, pos, text='hello, world', focused=True, font=None, background=0, foreground=(255, 255, 255)):
        self.pos = pos
        self.text = text
        self.font = font or pygame.font.Font(None, 48)
        self.point = len(text)
        self.focused = focused
        self.background = background
        self.foreground = foreground
        self.repeater = KeyRepeater(self)

    def draw(self, surface):
        x, y = self.pos
        pygame.draw.rect(surface, self.background,
                         (x, y,
                          surface.get_width()-x, self.font.get_linesize()))
        surface.blit(self.font.render(self.text, 1, self.foreground), self.pos)
        if self.focused:
            initial = self.text[:self.point]
            width, height = self.font.size(initial)
            pygame.draw.rect(surface, self.foreground, (x + width, y, 1, height))

    def handle_key(self, event):
        inc = 4 if event.mod & pygame.KMOD_ALT else 1
        if event.key == pygame.K_BACKSPACE:
            if self.point > 0:
                delstart = max(self.point - inc, 0)
                self.text = self.text[:delstart] + self.text[self.point:]
                self.point = delstart
        elif event.key == pygame.K_LEFT:
            self.point = max(self.point - inc, 0)
        elif event.key == pygame.K_RIGHT:
            self.point = min(self.point + inc, len(self.text))
        elif event.unicode:
            self.text = self.text[:self.point] + event.unicode + self.text[self.point:]
            self.point += 1
        print event, event.unicode, event.scancode

    def handle_keyevent(self, event):
        self.repeater.handle_keyevent(event, self)

    def poll(self):
        self.repeater.poll(self)

if __name__ == '__main__': 
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    field = TextField((100, 200), foreground=(255, 0, 0))
    while True:
        event = pygame.event.poll()
        if event.type in [pygame.QUIT, pygame.MOUSEBUTTONDOWN]:
            break
        elif event.type in [pygame.KEYUP, pygame.KEYDOWN]:
            field.handle_keyevent(event)
        elif event.type == pygame.NOEVENT:
            field.poll()
            field.draw(screen)
            pygame.display.flip()
        else:
            print event
