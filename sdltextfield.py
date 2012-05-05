#!/usr/bin/python

import pygame

class TextField(object):
    def __init__(self, pos):
        self.text = 'hello, world'
        self.font = pygame.font.Font(None, 96)
        self.pos = pos
    def draw(self, surface):
        surface.blit(self.font.render(self.text, 1, (255, 255, 255)), self.pos)

if __name__ == '__main__': 
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    TextField((100, 200)).draw(screen)
    pygame.display.flip()
    pygame.time.delay(2000)
