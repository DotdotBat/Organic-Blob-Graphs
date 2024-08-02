import pygame.draw as pd
from state import chains
from chain import Chain

import pygame

screen = pygame.display.get_surface()


def draw_chain(chain:Chain):
    
    pd.lines(screen,chain.color, closed=False, points=chain.get_co_tuples())


def draw():
    screen.lock()
    screen.fill(0)
    for chain in chains:
        draw_chain(chain)
    screen.unlock()