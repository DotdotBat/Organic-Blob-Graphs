from typing import List
import state
from state import chains
import math
from chain import Chain
import random
from point import Point
from blob import Blob

test_chain = Chain()


from tests.blob_test import create_valid_blob

def setup():
    blob_point_num = 3 + 4 + 5 + 6 - 4
    p1 = Point(0, 0)
    p2 = Point(0, 100)
    p3 = Point(100, 100)
    p4 = Point(100, 0)
    chain1 = Chain.from_end_points(p1, p2, point_num= 3)
    chain2 = Chain.from_end_points(p2, p3, point_num= 4)
    chain3 = Chain.from_end_points(p4, p3, point_num= 5)
    chain4 = Chain.from_end_points(p4, p1, point_num= 6)
    big_blob = Blob.from_chain_loop([chain1, chain2, chain3, chain4])
    small_blob, all_chains = big_blob.spawn_small_blob(0)
    all_chains = set(big_blob.chain_loop + small_blob.chain_loop)
    state.areas.append(big_blob)
    state.areas.append(small_blob)
    state.chains.update(all_chains)

    

link_length = state.resolution

angle_enforcing_distance = state.min_thinkness

hero_point = Point(0, 0)
frame_count = 0
def simulate(dt:float):
    # if len(state.areas) < state.blobs_num:
    #     spawn_blob_in_largest_blob()
    
    # for blob in state.areas:
    #     blob.recalculate_area()
    
            
    # for chain in chains:
    #     chain.enforce_link_length(link_length=state.resolution)
    # for chain in chains:
    #     chain.enforce_minimum_secondary_joint_distance(angle_enforcing_distance, link_length=state.resolution)
    # for chain in chains:
    #     chain.apply_accumulated_offsets()

    state.frame_count+=1
    point_index = math.floor(state.frame_count/5)
    blob = state.areas[0]
    blob:Blob
    on_blob_point = blob.get_point(point_index)
    inner_direction = blob.get_inner_direction(point_index)
    inner_direction.scale_to_length(10)
    state.inner_point.co = on_blob_point.co + inner_direction
        

def spawn_blob_in_largest_blob():
    big_blob = find_largest_blob()
    new_blob, chains_to_register = big_blob.spawn_small_blob()
    state.ensure_chains_registered(chains_to_register)
    
    state.areas.append(new_blob)
    return new_blob
    
def find_largest_blob():
    largest_blob_so_far = state.areas[0]
    for blob in state.areas:
        blob:Blob
        if blob.points_num > largest_blob_so_far.points_num:
            largest_blob_so_far = blob
    return largest_blob_so_far

def spawn_first_and_outer_blob():
    margin = 10
    link_length = state.resolution
    m = margin
    w = state.width
    h = state.height
    top_left = Point(m,m)
    top_right = Point(w-m, m)
    bottom_left = Point(m, h - m)
    bottom_right = Point(w - m, h - m)
    top = Chain.from_end_points(
        start = top_left, end = top_right,
        link_length = link_length, color= "gray"
    )
    left = Chain.from_end_points(
        start = bottom_left, end = top_left,
        link_length = link_length, color= "gray"
    )
    bottom = Chain.from_end_points(
        start = bottom_right, end = bottom_left,
        link_length = link_length, color= "gray"
    )
    right = Chain.from_end_points(
        start = top_right, end = bottom_right,
        link_length = link_length, color= "gray"
    )
    first_blob = Blob.from_chain_loop(
        ccw_chain_loop= [top, left, bottom, right]
    )
    outer_blob = Blob.from_chain_loop(
        ccw_chain_loop= [right, bottom, left, top], is_outer=True
    )
    state.chains.update([top, left, bottom, right])
    state.areas.append(first_blob)
    state.outer_blob = outer_blob
    
    
    outer_blob.is_unmoving = True
    return first_blob, outer_blob

def add_blob_area_equalization_offset(chains:List[Chain]):
    for chain in chains:
        if not chain.is_unmoving:
            offset = 10 if chain.blob_left.area<chain.blob_right.area else -10
            chain.add_right_offset(offset)