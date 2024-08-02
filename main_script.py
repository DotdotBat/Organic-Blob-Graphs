import pygame
import state
from state import chains, intersections
import chain
import draw as draw_module
from draw import draw
from chain import Chain
from math import cos, sin, pi
from intersection import Intersection


test_chain_points = chain.construct_random_chain(10)
test_chain = Chain(test_chain_points, link_length=state.resolution, color = "red")
second_chain_points = chain.construct_random_chain(40)
second_chain = Chain(second_chain_points, link_length=state.resolution, color = "green")
chains.append(second_chain)
chains.append(test_chain)
intersections.append(Intersection([test_chain, second_chain]))



link_length = state.resolution

angle_enforcing_distance = state.min_thinkness
 
def simulate(dt:float):
    x, y =  pygame.mouse.get_pos()
    test_chain.last_point.co.update(x, y)
    for chain in chains:
        chain.enforce_link_length()
    for chain in chains:
        chain.enforce_minimum_secondary_joint_distance(angle_enforcing_distance)
    for chain in chains:
        chain.applyAccumulatedOffsets()
    for intersection in intersections:
        intersection.keep_chains_connected()

    



# pygame setup
pygame.init()
draw_module.screen = pygame.display.set_mode((state.width, state.height))
clock = pygame.time.Clock()
running = True
dt = 0

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    simulate(dt)
    draw()
    #wrap up
    pygame.display.flip()
    dt = clock.tick(60) / 1000

pygame.quit()