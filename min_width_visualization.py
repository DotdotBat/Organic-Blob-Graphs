import pygame_widgets
import pygame
from blob import Blob
from chain import Chain
import state
import draw
from draw import draw_blob, draw_line_between_points
from math import sin, cos
import math
from pygame.math import lerp
from random import randint

from pygame_widgets.textbox import TextBox

pygame.init()
screen = pygame.display.set_mode((1000, 600))
draw.screen = screen


coords = []
point_number = 20
for i in range(point_number):
    t = lerp(0, math.tau, i/point_number)
    x = 3*sin(t) + cos(t)
    y = 2*cos(t) + sin(3*t)
    x = lerp(0, 1000, x/8 + 0.5)
    y = lerp(0, 600, y/6 + 0.5)
    coords.append((x, y))

chain = Chain.from_coord_list(coords=coords)
chain.close()
blob = Blob.from_chain_loop([chain])

*bottleneck_indexes_pair, bottleneck_width = blob.find_local_minimum_width_pair_under_target_width(
    sample_number=3, index_berth=6, target_width=215
)
max_width = blob.points_distance(1,11)/2 

clock = pygame.time.Clock()

previous = 0
def draw():
    screen.fill((0, 0, 0))
    draw_blob(blob)
    draw_line_between_points(blob.get_point(p1), blob.get_point(p2))
    pygame_widgets.update(events)
    pygame.display.update()

p1 = 5
p2 = 15

def find_local_minimum_width_pair(blob, sample_number:int, index_berth:int, target_width:float):
    smallest_width_so_far = math.inf
    initial_guesses = initial_pairs(blob, number_of_pairs=sample_number)
    closest_pair=(-3, -3)
    for pair in initial_guesses:
        found_local_minimum = False
        closer_pair = pair
        while not found_local_minimum:
            closer_pair, distance = try_finding_closer_pair(blob, closer_pair,index_berth=index_berth, target_distance=target_width)
            found_local_minimum = closer_pair == (-1, -1)
            if distance<smallest_width_so_far:
                smallest_width_so_far = distance
                closest_pair = closer_pair
    index_a, index_b = closest_pair
    smallest_width = smallest_width_so_far
    if smallest_width > target_width:
        return -1, -1, smallest_width
    return index_a, index_b, smallest_width

def initial_pairs(blob:Blob, number_of_pairs:int):
    pairs = []
    for i in range(number_of_pairs):
        a = math.floor(0.5 *blob.point_number*i/number_of_pairs)
        b = (blob.point_number//2 + a)%blob.point_number
        pairs.append((a,b))
    return pairs

def try_finding_closer_pair(blob:Blob, initial_pair:tuple[int,int],index_berth:int, target_distance:float):
    """will search in the vacinity, but if the given pair looks like the closest pair seems to be the initial one, it will return the initial one"""
    step:int
    initial_distance = blob.points_distance(*initial_pair)
    if target_distance>initial_distance:
        step = 1
    else:
        step = math.ceil((initial_distance - target_distance)/blob.link_length)
    candidate_pairs = create_candidate_pairs_list(blob= blob, base_pair=initial_pair, step=step, index_berth=index_berth)
    closest_pair = initial_pair
    smallest_distance = initial_distance
    for candidate in candidate_pairs:
        candidate_distance = blob.points_distance(*candidate)
        if candidate_distance<smallest_distance:
            smallest_distance = candidate_distance
            closest_pair = candidate
    if closest_pair == initial_pair:
        closest_pair = (-1,-1) #a code that we have reached the local minimum
    return closest_pair, smallest_distance



def create_candidate_pairs_list(blob:Blob, base_pair:tuple[int, int], step:int, index_berth:int):
    index_a, index_b = base_pair
    a_indexes = [index_a, (index_a-step)%blob.point_number, (index_a+step)%blob.point_number]
    b_indexes = [index_b, (index_b-step)%blob.point_number, (index_b+step)%blob.point_number]
    candidate_pairs = [(a, b) for a in a_indexes for b in b_indexes]
    candidate_pairs.remove(base_pair)
    valid_pairs = [pair for pair in candidate_pairs if blob.index_distance(*pair)>index_berth]
    return valid_pairs




run = True
while run:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            run = False
            quit()
        if event.type == pygame.MOUSEBUTTONUP:
            p1 = (previous+1)%blob.point_number
            previous = p1
            p2 = (p1 - blob.point_number//2)%blob.point_number
            print(p1, p2)
            p1, p2, distance = find_local_minimum_width_pair(blob,sample_number=6, index_berth=4, target_width=215)
            print(p1, p2, distance)
            blob.enforce_minimal_width(
                minimal_width= 350 + p1*10,#(max_width + bottleneck_width)/2,
                ignore_umoving_status= True
            )
            blob.apply_accumulated_offsets(ignore_unmoving_status=True)


    draw()
    clock.tick(20)



#todo: move this cumbersome function into a separate file











