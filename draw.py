import pygame.draw as pd
from state import chains
from chain import Chain
import state
import pygame

screen = pygame.display.get_surface()

def draw_chain(chain:Chain):
    pd.lines(screen,chain.color, closed=False, points=chain.get_co_tuples())

def highlight_hero_point():
    x = state.point_of_interest.co.x
    y = state.point_of_interest.co.y
    pd.circle(screen, "green", (x, y), radius=5)

# font = pygame.font.Font(size=15)#todo: get a valid font name

def draw():
    screen.lock()
    screen.fill(0)
    pygame.display.set_caption(state.frame_count.__str__())
    for chain in chains:
        draw_chain(chain)
    if state.show_hero_point:
        highlight_hero_point()
    screen.unlock()