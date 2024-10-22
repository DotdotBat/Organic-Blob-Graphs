import math

import pygame
from chain import Chain
from typing import Set, List
from blob import Blob
from point import Point

width = 720
height = 480
chains: Set[Chain] = set()
blobs: List[Blob] = list()
lesser_dimention = min(width, height)
resolution = lesser_dimention/100
link_length = resolution
min_thinkness=lesser_dimention/10
goal_blobs_num = 10
expected_blob_area = width * height/goal_blobs_num
square_cirumference =  math.sqrt(expected_blob_area)*4
goal_blob_circumference = square_cirumference * 1.5
goal_blob_point_number = math.ceil(goal_blob_circumference/link_length)

frame_count = 0

point_of_interest:Point = None

def get_movable_chains():
    return [chain for chain in chains if not chain.is_unmoving]

def draw_callback()->None:
    raise RuntimeError("Forgot to set the draw callback in main_file")

screen = pygame.display.get_surface()
