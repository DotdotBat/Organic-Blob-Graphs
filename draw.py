import pygame.draw as pd
from state import chains
from chain import Chain
import state

import pygame

screen = pygame.display.get_surface()


def draw_chain(chain:Chain):
    
    pd.lines(screen,chain.color, closed=False, points=chain.get_co_tuples())

def highlight_hero_point():
    x = state.inner_point.co.x
    y = state.inner_point.co.y
    pd.circle(screen, "green", (x, y), radius=5)




def draw():
    screen.lock()
    screen.fill(0)
    for chain in chains:
        draw_chain(chain)
    highlight_hero_point()
    
    screen.unlock()