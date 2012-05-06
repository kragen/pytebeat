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
    def __init__(self, pos, text='hello, world', focused=True, font=None, background=0, foreground=(255, 255, 255), selected_background=(64,64,64)):
        self.pos = pos
        self.text = text
        self.font = font or pygame.font.Font(None, 48)
        self.mark = self.point = len(text)
        self.focused = focused
        self.background = background
        self.foreground = foreground
        self.selected_background = selected_background
        self.repeater = KeyRepeater(self)

    def draw(self, surface):
        x, y = self.pos
        pygame.draw.rect(surface, self.background,
                         (x, y,
                          surface.get_width()-x, self.font.get_linesize()))

        if self.selection():
            a, _ = self.font.size(self.text[:self.mark])
            b, height = self.font.size(self.text[:self.point])
            if b < a:
                b, a = a, b
            pygame.draw.rect(surface, self.selected_background,
                             (x + a, y, b - a, height))

        surface.blit(self.font.render(self.text, 1, self.foreground), self.pos)
        if self.focused:
            initial = self.text[:self.point]
            width, height = self.font.size(initial)
            pygame.draw.rect(surface, self.foreground, (x + width, y, 1, height))

    def selection(self):
        return self.mark != self.point

    def unselect(self):
        self.mark = self.point

    def goto(self, where, event):
        self.point = where
        if not event.mod & pygame.KMOD_SHIFT:
            self.unselect()

    def delete(self, a, b):
        if a > b:
            a, b = b, a
        self.text = self.text[:a] + self.text[b:]
        self.point = a
        self.unselect()

    def number_at_point(self):
        start, end = self.point, self.point
        while start > 0 and self.text[start-1].isdigit():
            start -= 1
        while end < len(self.text) and self.text[end].isdigit():
            end += 1
        return start, end

    def increment_number_at_point(self, by_what):
        start, end = self.number_at_point()
        if start == end:
            return
        n = int(self.text[start:end])
        n += by_what
        self.delete(start, end)
        self.insert(str(n))

    def handle_key(self, event):
        inc = 4 if event.mod & pygame.KMOD_ALT else 1
        if event.key == pygame.K_BACKSPACE:
            if self.selection():
                self.delete(self.mark, self.point)
            else:
                self.delete(max(self.point - inc, 0), self.point)

        elif event.key == pygame.K_LEFT:
            self.goto(max(self.point - inc, 0), event)
        elif event.key == pygame.K_RIGHT:
            self.goto(min(self.point + inc, len(self.text)), event)
        elif event.key == pygame.K_UP:
            self.increment_number_at_point(1)
        elif event.key == pygame.K_DOWN:
            self.increment_number_at_point(-1)
        elif event.key == pygame.K_HOME:
            self.goto(0, event)
        elif event.key == pygame.K_END:
            self.goto(len(self.text), event)
        elif event.unicode:
            if self.selection():
                self.delete(self.mark, self.point)
            self.insert(event.unicode)
        print event, event.unicode, event.scancode

    def insert(self, text):
        self.text = self.text[:self.point] + text + self.text[self.point:]
        self.point += len(text)
        self.unselect()

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
