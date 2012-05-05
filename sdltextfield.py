#!/usr/bin/python
"""Text editor class for PyGame.

This is for my bytebeat livecoding performance software.

"""

import pygame
import time

class TextField(object):
    def __init__(self, pos, text='hello, world', focused=True, font=None, background=0, foreground=(255, 255, 255)):
        self.pos = pos
        self.text = text
        self.font = font or pygame.font.Font(None, 48)
        self.point = len(text)
        self.focused = focused
        self.background = background
        self.foreground = foreground
        self.last_keydown = None
        self.initial_autorepeat_delay = 0.25
        self.autorepeat_delay = 0.05
        self.next_keyrepeat = None

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
        if event.key == pygame.K_BACKSPACE:
            if self.point > 0:
                self.text = self.text[:self.point-1] + self.text[self.point:]
                self.point -= 1
        elif event.key == pygame.K_LEFT:
            if self.point > 0:
                self.point -= 1
        elif event.key == pygame.K_RIGHT:
            if self.point < len(self.text):
                self.point += 1
        elif event.unicode:
            self.text = self.text[:self.point] + event.unicode + self.text[self.point:]
            self.point += 1
        print event, event.unicode, event.scancode

    def handle_keyevent(self, event):
        if event.type == pygame.KEYDOWN:
            self.last_keydown = event
            self.handle_key(event)
            self.next_keyrepeat = time.time() + self.initial_autorepeat_delay
        else:
            if self.last_keydown and event.key == self.last_keydown.key:
                self.last_keydown = None
                self.next_keyrepeat = None

    def poll(self):
        if self.last_keydown:
            now = time.time()
            while now > self.next_keyrepeat:
                self.handle_key(self.last_keydown)
                self.next_keyrepeat += self.autorepeat_delay

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
