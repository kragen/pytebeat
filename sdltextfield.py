#!/usr/bin/python

import pygame

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
font = pygame.font.Font(None, 96)
hello = font.render('hello, world', 1, (255, 255, 255))
screen.blit(hello, (100, 200))
pygame.display.flip()
pygame.time.delay(2000)
