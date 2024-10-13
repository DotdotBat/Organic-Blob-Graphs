import pygame
import math
from typing import List
import state
from state import chains
from chain import Chain
from point import Point
from blob import Blob
def setup():
    first_blob = create_frame_blob(state.width, state.height)
    if type(first_blob) != Blob:
            raise RuntimeError("this isn't a Blob", first_blob)
    state.blobs.append(first_blob)
    
hero_point = Point(0, 0)
def simulate(dt:float):
    state.frame_count+=1
    #blob spawning
    if state.frame_count%50 == 0 and len(state.blobs) < state.goal_blobs_num:
        spawn_blob_in_largest_blob()

    movable_chains = state.get_movable_chains()

    #link_length and curve
    for chain in movable_chains:
        chain.enforce_link_length(link_length=state.link_length)
        chain.enforce_minimum_secondary_joint_distance(distance=state.link_length*4, link_length=state.link_length)
    
    #area equalization
    add_area_equalization_offset(movable_chains)
    
    # circumference equalization
    for chain in movable_chains:
        if chain.blob_left.point_number * chain.blob_right.point_number < state.goal_blob_point_number*state.goal_blob_point_number:
            point_i = math.floor((chain.point_number-1)/2)
            chain.create_midpoint(point_index=point_i, next_index=point_i+1)    
    
    # clamp offsets
    for chain in state.chains:
        for point in chain.points:
            point.clamp_offset(state.resolution)

    for chain in state.chains:
        chain.apply_accumulated_offsets()

def add_area_equalization_offset(movable_chains: List[Chain]):
    for blob in state.blobs:
        blob.recalculate_area()
    for chain in movable_chains:
        max_offset = state.resolution*2
        left_area, right_area = chain.blob_left.cashed_area, chain.blob_right.cashed_area
        scale = 1 - (min(left_area, right_area) / max(left_area, right_area))

        offset_magnitude = scale * max_offset
        if right_area < left_area:
            chain.add_right_offset(-offset_magnitude)
        if left_area < right_area:
            chain.add_right_offset(offset_magnitude)
        chain.color = (255, (1-scale) * 225,  (1-scale) * 225)
        

def spawn_blob_in_largest_blob():
    big_blob = find_largest_blob()
    new_blob, chains_to_register = big_blob.spawn_small_blob()
    state.chains.update(chains_to_register)
    state.blobs.append(new_blob)
    
def find_largest_blob():
    largest_blob_so_far = state.blobs[0]
    for blob in state.blobs:
        blob:Blob
        if blob.point_number > largest_blob_so_far.point_number:
            largest_blob_so_far = blob
    return largest_blob_so_far    


def create_frame_blob(width:float, height:float, margin=5)->Blob:
    m = margin
    tl, tr, br, bl = Point(m, m), Point(width-m, m), Point(width-m,height-m), Point(m, height-m)
    top =    Chain.from_end_points(tl, tr, link_length=state.resolution)
    bottom = Chain.from_end_points(bl, br, link_length=state.resolution)
    left =   Chain.from_end_points(tl, bl, link_length=state.resolution)
    right =  Chain.from_end_points(tr, br, link_length=state.resolution)
    chain_loop = [top, left, bottom, right]
    return Blob.from_chain_loop(chain_loop)