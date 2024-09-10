import pygame
from pygame.sprite import _Group

def CreateSmokeParticle():
    class Smoke(pygame.sprite.Sprite):
        def __init__(part):
            super().__init__()
            part.image = pygame.image.load()