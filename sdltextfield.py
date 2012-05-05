#!/usr/bin/python

import pygame

class TextField(object):
    def __init__(self, pos):
        self.text = 'hello, world'
        self.font = pygame.font.Font(None, 96)
        self.pos = pos

    def draw(self, surface):
        width, height = self.font.size(self.text)
        surface.blit(self.font.render(self.text, 1, (255, 255, 255)), self.pos)
        x, y = self.pos
        pygame.draw.rect(surface, (255, 255, 255), (x + width, y, 1, height))

    def handle_key(self, event):
        if event.key == pygame.K_BACKSPACE:
            self.text = self.text[:-1]
        elif event.unicode:
            self.text += event.unicode
        print event, event.unicode, event.scancode

if __name__ == '__main__': 
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    field = TextField((100, 200))
    while True:
        event = pygame.event.poll()
        if event.type in [pygame.QUIT, pygame.MOUSEBUTTONDOWN]:
            break
        elif event.type == pygame.KEYDOWN:
            field.handle_key(event)
        elif event.type == pygame.NOEVENT:
            screen.fill(0)
            field.draw(screen)
            pygame.display.flip()
