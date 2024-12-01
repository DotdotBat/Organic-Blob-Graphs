import math

from pygame import Vector2
from pygame.math import lerp
from math import sin, cos
from blob import Blob
from chain import Chain
from point import Point
import pytest
from blob_test import create_valid_blob, standard_valid_blob_point_number

import simulation
def test_apply_blob_area_equalization_force():
    blob_point_num = 5 + 6 + 7 + 8 - 4
    for spawn_location in range(blob_point_num * 2): #this test failes in about a third of the runs. I don't want to rely on chance
        p1 = Point(0, 0)
        p2 = Point(0, 100)
        p3 = Point(100, 100)
        p4 = Point(100, 0)
        chain1 = Chain.from_end_points(p1, p2, point_num= 5)
        chain2 = Chain.from_end_points(p2, p3, point_num= 6)
        chain3 = Chain.from_end_points(p4, p3, point_num= 7)
        chain4 = Chain.from_end_points(p4, p1, point_num= 8)
        big_blob = Blob.from_chain_loop([chain1, chain2, chain3, chain4])
        if spawn_location > blob_point_num:
            spawn_location = None
        small_blob, all_chains = big_blob.spawn_small_blob(spawn_location)
        assert big_blob.assert_is_valid(raise_errors=True)
        assert small_blob.assert_is_valid(raise_errors=True)
        all_chains = set(big_blob.chain_loop + small_blob.chain_loop)
        assert len(all_chains) > 0
        big_blob.recalculate_area()
        small_blob.recalculate_area()
        start_big_area = big_blob.cashed_area
        start_small_area = small_blob.cashed_area
        assert big_blob.cashed_area > small_blob.cashed_area

        movable_chains = [chain for chain in all_chains if not chain.is_unmoving]
        assert len(movable_chains) > 0

        simulation.add_area_equalization_offset(blobs=[big_blob, small_blob], resolution=10, movable_chains=movable_chains)
        for chain in movable_chains:
            chain.apply_accumulated_offsets()
        
        big_blob.recalculate_area()
        small_blob.recalculate_area()
        if not(big_blob.cashed_area < start_big_area and small_blob.cashed_area > start_small_area):
            print(big_blob.cashed_area < start_big_area)
            pass
        assert big_blob.cashed_area < start_big_area
        assert small_blob.cashed_area > start_small_area


from blob_test import assert_references
def test_remove_and_insert_midpoint():
    # Create a uniform square blob with 5 points on each side
    p1 = Point(0, 0)
    p2 = Point(0, 100)
    p3 = Point(100, 100)
    p4 = Point(100, 0)
    chain1 = Chain.from_end_points(p1, p2, point_num=5)
    chain2 = Chain.from_end_points(p2, p3, point_num=5)
    chain3 = Chain.from_end_points(p3, p4, point_num=5)
    chain4 = Chain.from_end_points(p4, p1, point_num=5)
    blob = Blob.from_chain_loop([chain1, chain2, chain3, chain4])
    assert blob.assert_is_valid(raise_errors=True)
    for point_index in range(0,blob.point_number):
        # Remove a point
        point_to_remove = blob.get_point(point_index)
        blob.remove_point(point_index)
        assert blob.assert_is_valid(raise_errors=True)
        # Test that the point is removed
        assert point_to_remove not in [point for chain in blob.chain_loop for point in chain.points]
        
        # Find the biggest gap
        index1, index2 = blob.find_biggest_gap_indexes(only_movable_chains=False)
        point1 = blob.get_point(index1)
        point2 = blob.get_point(index2)
        
        # Insert a midpoint between these indexes
        midpoint = blob.create_midpoint(index1, index2)
        
        # Test that the midpoint is indeed inserted
        expected_midpoint_co = (point1.co + point2.co) / 2
        assert midpoint.co.x == pytest.approx(expected_midpoint_co.x)
        assert midpoint.co.y == pytest.approx(expected_midpoint_co.y)
        assert midpoint in [point for chain in blob.chain_loop for point in chain.points]


        # Ensure the blob is still valid
        assert blob.assert_is_valid(raise_errors=True)

        #insert another point after the inserted midpoint
        _, next_index = blob.neighboring_indexes(point_index)
        midpoint = blob.create_midpoint(point_index, next_index)

        # find the most crowded point 
        crowded_index = blob.find_most_crowded_point_index()
        crowded_point = blob.get_point(crowded_index)
        #check that it is the point we planted
        assert crowded_point is midpoint

        #remove it 
        blob.remove_point(crowded_index)
        #check that everything is still valid after all our manipulations
        blob.assert_is_valid()
        assert_references(blobs=[blob])


def test_modify_blob_circumference():
    initial_point_count = standard_valid_blob_point_number
    modification_values = [3, -2, 0, -(initial_point_count - 2)]

    for modification in modification_values:
        blob = create_valid_blob()
        blobs = [blob]
        # Spawn additional blobs to create a multiblob scenario.
        for i in range(3):
            step = math.floor(initial_point_count/3)
            new_blob, _ = blob.spawn_small_blob(i*step)
            blobs.append(new_blob)
        point_number_before = blob.point_number

        blob.modify_point_number(modification)

        expected_points_num = max(3, point_number_before + modification)
        assert blob.point_number == expected_points_num
        for b in blobs:
            assert blob.assert_is_valid(raise_errors=True)

        # Check references between blobs, chains, and points.
        assert_references(blobs=blobs)



        
def test_enforce_minimal_width():
    # Minimal width setup
    minimal_width_small = 0.5
    minimal_width_large = 50
    minimal_width_too_big = 150  # Approximation for a 100x100 square diagonal

    # Create a square blob
    tl = Point(0, 0)
    bl = Point(0, 100)
    br = Point(100, 100)
    tr = Point(100, 0)
    left = Chain.from_end_points(tl, bl, point_num=3)
    bottom = Chain.from_end_points(bl, br, point_num=3)
    right = Chain.from_end_points(br, tr, point_num=3)
    top = Chain.from_end_points(tr, tl, point_num=3)
    blob = Blob.from_chain_loop([left, bottom, right, top])
    for chain in blob.chain_loop:
        chain.is_unmoving_override = False


    # Scenario 1: No correction needed
    *closest_pair, width = blob.find_local_minimum_width_pair_under_target_width(
        target_width=minimal_width_small, index_berth=1, sample_number=10
    )
    assert closest_pair == [-1, -1]
    blob.enforce_minimal_width(minimal_width_small)
    for chain in blob.chain_loop:
        for point in chain.points:
            assert point.offset.x == 0 and point.offset.y == 0, "No offset should be applied."

  
    # Scenario 2: Correct specific points
    
    # Move top and bottom points closer together
    top_point = top.create_midpoint(0, 1)
    bottom_point = bottom.create_midpoint(0,1)
    top_index = 8
    assert blob.get_point(top_index) == top_point
    bottom_index = 3
    assert blob.get_point(bottom_index) == bottom_point
    top_point.co.y = 50
    top_point.co.x = 50
    bottom_point.co.x = 50
    
    bottom_point.co.y = 65
    assert top_point.co.distance_to(bottom_point.co) < minimal_width_large


    *closest_pair, _ = blob.find_local_minimum_width_pair_under_target_width(
        sample_number=10, index_berth=3, target_width=minimal_width_large
    )
    assert top_index in closest_pair
    assert bottom_index in closest_pair
    blob.enforce_minimal_width(minimal_width=minimal_width_large)
    for p in [tl, bl, tr, br]:
        assert p.offset.length_squared() == 0
    assert bottom_point.offset.length_squared() != 0, "Offset should be applied to p2."
    assert top_point.offset.length_squared() != 0, "Offset should be applied to p4."
    bottom_point.apply_accumulated_offset(ignore_unmoving=True)
    top_point.apply_accumulated_offset(ignore_unmoving=True)
    assert bottom_point.co.distance_to(top_point.co) == pytest.approx(minimal_width_large)


    #SCENARIO 3 more than 2 points need to be corrected
    #create a smooth dumbell shaped blob, where the bottleneck is 215 units across, so lets enforce 300

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
    dumbell_blob = Blob.from_chain_loop([chain])

    *bottleneck_indexes_pair, bottleneck_width = dumbell_blob.find_local_minimum_width_pair_under_target_width(
        sample_number=3, index_berth=6, target_width=215
    )
    assert 18 in bottleneck_indexes_pair and 9 in bottleneck_indexes_pair
    assert bottleneck_width == pytest.approx(210.9557686)
    max_width = dumbell_blob.points_distance(1,11)/2 
    dumbell_blob.enforce_minimal_width(
        minimal_width= (max_width + bottleneck_width)/2
    )

    # #last scenario, the whole blob is smaller than the specified min_width, so it is expected to grow with each iteration
    blob.enforce_minimal_width(minimal_width_too_big)
    blob.recalculate_area()
    area_before = blob.cashed_area

    assert any(point.offset.magnitude_squared() > 0 for point in blob.points_list)
    #lets repeat this a few times and the blob should be big:
    for i in range(100):
        blob.apply_accumulated_offsets(ignore_unmoving_status=True)
        assert all(point.offset.x==0 and point.offset.y ==0 for point in blob.points_list)
        link_length = lerp(100, 300, i/100)
        for chain in blob.chain_loop:
            chain.enforce_link_length(link_length,ignore_umoving_status=True)
        blob.enforce_minimal_width(minimal_width_too_big+10, ignore_umoving_status=True)
    blob.recalculate_area()
    assert blob.cashed_area > area_before
    for point_index in range(blob.point_number):
        opposite_index = blob.opposite_index(point_index)
        distance = blob.points_distance(point_index, opposite_index)
        assert distance >= minimal_width_too_big


def test_joint_sliding():
    # Construct the tube
    # 1 --------------- 2
    # |\                |
    # | |               |
    # |/                |
    # 4 --------------- 3

    width = 100
    height = 20
    p1 = Point(0, 0)
    p2 = Point(width, 0)
    p3 = Point(width, height)
    p4 = Point(0, height)
    center_coordinates = p1.co.lerp(p3.co, 0.5)
    
    # Create chains with a link length of 10
    chain1 = Chain.from_end_points(p1, p2, link_length=10)
    chain2 = Chain.from_end_points(p2, p3, link_length=10)
    chain3 = Chain.from_end_points(p3, p4, link_length=10)
    left_chain = Chain.from_end_points(p4, p1, link_length=10)

    # Create the membrane chain
    membrane_chain = Chain.from_end_points(p1, p4, point_num=5)
    membrane_chain.name = "Membrane"
    membrane_chain.points[1].co.x += 5
    membrane_chain.points[2].co.x += 5

    chains = [chain1, chain2, chain3, left_chain, membrane_chain]
    

    # Create blobs
    small_blob = Blob.from_chain_loop([left_chain, membrane_chain])
    small_blob.name = "Small growing"
    big_blob = Blob.from_chain_loop([chain1, chain2, chain3, membrane_chain])
    big_blob.name = "Big shrinking"
    link_length = 10
    small_blob.link_length, big_blob.link_length = link_length,link_length
    for chain in chains:
        expected_number_of_blobs = 2 if chain is membrane_chain else 1
        assert len(chain.blobs) == expected_number_of_blobs
        expected_unmoving_status = True if expected_number_of_blobs ==1 else False
        assert chain.is_unmoving == expected_unmoving_status
    

    #remember state before simulation for comparison during testing
    past_membrane_coordinates = membrane_chain.get_co_tuples()
    past_blob_circum_diff = abs(big_blob.actual_circumference - small_blob.actual_circumference)
    big_blob.recalculate_area()
    small_blob.recalculate_area()
    past_blob_area_diff = abs(big_blob.cashed_area - small_blob.cashed_area)

    # Apply simulation
    for _ in range(5):
        simulation.simulation_step(blobs = [small_blob, big_blob], resolution=link_length,  minimal_width = link_length *2)

    #check that the membrane moved at all
    membrane_coordinates = membrane_chain.get_co_tuples()
    assert membrane_coordinates != past_membrane_coordinates, f"Membrane did not move: {membrane_coordinates}"

    #check that the membrane moved closer to the center
    for i, xy in enumerate(membrane_coordinates):
        now = Vector2(xy)
        then = Vector2(past_membrane_coordinates[i])
        point = membrane_chain.points[i]
        assert now.distance_to(center_coordinates) < then.distance_to(center_coordinates), f"{point} of membrane did not move towards the center. Here are the current membrane coordinates: {membrane_coordinates}"

    #check that all the points are still inside the tube of on its sides
    def is_within_tube(point:Point):
        x, y = point.co.xy
        if x<0 or x>width:
            return False
        if y<0 or y>height:
            return False
        return True
    
    for i, point in enumerate(membrane_chain.points):
        assert is_within_tube(point), f"{point} number {i} from membrane chain is outside the frame"
    

    #check that the difference in areas of the blobs has decreased 
    big_blob.recalculate_area()
    small_blob.recalculate_area()
    blob_area_diff = abs(big_blob.cashed_area - small_blob.cashed_area)
    assert blob_area_diff < past_blob_area_diff, "Blob area equalization failed"

    #check that the difference in circumference of the blobs has decreased
    blob_circum_diff = abs(big_blob.actual_circumference - small_blob.actual_circumference)
    assert blob_circum_diff < past_blob_circum_diff, "Blob circumference equalization failed"
    


