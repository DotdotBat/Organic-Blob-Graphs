import pygame.draw as pd
from point import Point
from state import chains
from blob import Blob
from chain import Chain
import state
import pygame

screen = pygame.display.get_surface()

def draw_chain(chain:Chain):
    pd.lines(screen,chain.color, closed=False, points=chain.get_co_tuples())

def highlight_point(point:Point):
    x = point.co.x
    y = point.co.y
    pd.circle(screen, "green", (x, y), radius=5)

# font = pygame.font.Font(size=15)#todo: get a valid font name

def draw_state():
    screen.lock()
    screen.fill(0)
    pygame.display.set_caption(state.frame_count.__str__())
    for chain in chains:
        draw_chain(chain)
    if state.point_of_interest is not None:
        highlight_point(point=state.point_of_interest)
    screen.unlock()

def draw_blob(blob:Blob):
    for chain in blob.chain_loop:
        draw_chain(chain)

def draw_line_between_points(p1:Point, p2:Point, color = "white"):
    pd.line(screen, color, start_pos=p1.co.xy, end_pos=p2.co.xy)