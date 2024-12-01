import warnings
import pygame
import math
from typing import List
import state
from chain import Chain
from point import Point
from blob import Blob
def setup():
    first_blob = create_frame_blob(state.width, state.height, state.link_length)
    if type(first_blob) != Blob:
            raise RuntimeError("this isn't a Blob", first_blob)
    state.blobs.append(first_blob)
    state.chains.update(first_blob.chain_loop)
    state.point_of_interest = Point(x=state.width/2, y=state.height/2)
    
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
    
    # minimal_thickness
    for blob in state.blobs:
        blob.enforce_minimal_width(state.min_thinkness)
    
    # circumference equalization
    # should be handled by sliding the endpoint along 
    for chain in movable_chains:
        if chain.blob_left.point_number * chain.blob_right.point_number < state.goal_blob_point_number*state.goal_blob_point_number:
            blob.find_biggest_gap_indexes
            point_i = math.floor((chain.point_number-1)/2)
            chain.create_midpoint(point_index=point_i, next_index=point_i+1)    
    
    # clamp offsets
    for chain in state.chains:
        for point in chain.points:
            point.clamp_offset(state.resolution)

    for chain in state.chains:
        chain.apply_accumulated_offsets()

def add_area_equalization_offset(blobs:list[Blob], resolution:float, movable_chains: List[Chain]):
    for blob in blobs:
        blob.recalculate_area()
    for chain in movable_chains:
        max_offset = resolution*2
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


def create_frame_blob(width:float, height:float, link_length:float, margin=5)->Blob:
    m = margin
    tl, tr, br, bl = Point(m, m), Point(width-m, m), Point(width-m,height-m), Point(m, height-m)
    top =    Chain.from_end_points(tl, tr, link_length=state.resolution)
    bottom = Chain.from_end_points(bl, br, link_length=state.resolution)
    left =   Chain.from_end_points(tl, bl, link_length=state.resolution)
    right =  Chain.from_end_points(tr, br, link_length=state.resolution)
    chain_loop = [top, left, bottom, right]
    blob =  Blob.from_chain_loop(chain_loop)
    # blob.is_unmoving_override = True 
    # - that is not a good idea, The spawned blobs wouldn't be able to move
    # From the outside they have None as a blob (hence unmoving)
    # From the inside they will have the frame blob, (hence unmoving)
    #So only between two spawned blobs a chain will be able to move. But why, would it?
    blob.link_length = link_length
    return blob

def find_all_endpoints(chains:list[Chain]):
    endpoints = set()
    for chain in chains:
        if chain.point_number>0:
            endpoints.add(chain.point_start)
            endpoints.add(chain.point_end)
    return endpoints

def enforce_minimal_width(blobs:list[Blob], minimal_width):
    for blob in blobs:
        blob.enforce_minimal_width(minimal_width)

def enforce_link_length(chains:list[Chain], link_length:float):
    for chain in chains:
        chain.enforce_link_length(link_length)

def apply_offsets(chains:list[Chain]):
    for chain in chains:
        chain.apply_accumulated_offsets()

def smooth_out_shapes(blobs:list[Blob]):
    for blob in blobs:
        if not blob.is_unmoving_override == True:
            #blob.smooth_out()
            warnings.warn("Smoothing is not implemented")
            #todo: implement smoothing function


def slide_joints(joints:list[Point]):
    for joint in joints:
        neighbors = joint.get_connected_points_via_chains()
        movable_neighbors = [point for point in neighbors if not point.is_unmoving]
        if len(movable_neighbors) == 0:
            continue
        #find the movable neighbor that wants to leave the most
        greatest_need_to_leave = 0
        most_desparate_candidate = None
        their_target = None
        for departure_candidate in movable_neighbors:
            possible_targets = neighbors.copy()
            possible_targets.remove(departure_candidate)
            target = departure_candidate.closest_of_points(possible_targets)
            #todo: figure out
            #should I filter out candidates whose target is further from the joint then themselves?
            #I think not. But this can be changed later. 
            need = departure_candidate.co.distance_to(joint.co) - departure_candidate.co.distance_to(target.co)
            if need > greatest_need_to_leave:
                most_desparate_candidate = departure_candidate
                their_target = target
                greatest_need_to_leave = need
        if most_desparate_candidate is None:
            continue
        
        further_neighbor = most_desparate_candidate
        closer_neighbor = their_target
        further_chain:Chain = joint.get_common_chain(further_neighbor)
        further_chain.switch_endpoint_to(endpoint=joint, target= closer_neighbor)

        
def dissolve_2_chain_joints(joints:list[Point]):
    for joint in joints:
        if joint.chains_number != 2:
            continue
        joint.dissolve_endpoint()

def simulation_step(blobs:list[Blob], resolution:float, minimal_width:float):
    chains = state.get_chains_list(blobs)
    movable_chains = state.get_movable_chains(chains)
    add_area_equalization_offset(blobs=blobs, resolution=resolution, movable_chains=movable_chains)
    enforce_minimal_width(blobs, minimal_width)
    enforce_link_length(chains=movable_chains, link_length=resolution)
    smooth_out_shapes(blobs=blobs)
    apply_offsets(movable_chains)
    movable_joints = state.get_wandering_joints(movable_chains)
    slide_joints(movable_joints)
    dissolve_2_chain_joints(movable_joints)

    
    