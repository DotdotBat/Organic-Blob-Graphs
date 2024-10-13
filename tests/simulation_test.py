import math

from pygame import Vector2
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
        assert big_blob.is_valid(raise_errors=True)
        assert small_blob.is_valid(raise_errors=True)
        all_chains = set(big_blob.chain_loop + small_blob.chain_loop)
        assert len(all_chains) > 0
        big_blob.recalculate_area()
        small_blob.recalculate_area()
        start_big_area = big_blob.cashed_area
        start_small_area = small_blob.cashed_area
        assert big_blob.cashed_area > small_blob.cashed_area

        movable_chains = [chain for chain in all_chains if not chain.is_unmoving]
        assert len(movable_chains) > 0

        simulation.add_area_equalization_offset(movable_chains)
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
    # Create a uniform square blob with 4 points on each side
    p1 = Point(0, 0)
    p2 = Point(0, 100)
    p3 = Point(100, 100)
    p4 = Point(100, 0)
    chain1 = Chain.from_end_points(p1, p2, point_num=4)
    chain2 = Chain.from_end_points(p2, p3, point_num=4)
    chain3 = Chain.from_end_points(p3, p4, point_num=4)
    chain4 = Chain.from_end_points(p4, p1, point_num=4)
    blob = Blob.from_chain_loop([chain1, chain2, chain3, chain4])
    for point_index in range(blob.point_number):
        # Remove a point
        point_to_remove = blob.get_point(point_index)
        blob.remove_point(point_index)
        
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
        assert blob.is_valid(raise_errors=True)

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
        blob.is_valid()
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
            assert blob.is_valid(raise_errors=True)

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


    # Scenario 1: No correction needed
    result = blob.find_local_minimum_width_pair(
        qualifying_width=minimal_width_small, max_indexes_difference=1,
        link_length=100, steps_number=10
    )
    assert result == (-1, -1)
    blob.enforce_minimal_width(minimal_width_small, link_length=100)
    for chain in blob.chain_loop:
        for point in chain.points:
            assert point.offset.x == 0 and point.offset.y == 0, "No offset should be applied."

  
    # Scenario 2: Correct specific points
    
    # Move top and bottom points closer together
    top_point = top.create_midpoint(0, 1)
    top_index = 7
    assert blob.get_point(top_index) == top_point
    bottom_point = bottom.create_midpoint(0,1)
    bottom_index = 3
    assert blob.get_point(bottom_index) == bottom_point
    top_point.co.y = 40
    bottom_point.co.y = 60


    result = blob.find_local_minimum_width_pair(
        qualifying_width=minimal_width_large, link_length=70,
        max_indexes_difference=1, steps_number=10
    )
    assert top_index in result
    assert bottom_index in result
    blob.enforce_minimal_width(minimal_width_large, 70)
    for p in [tl, bl, tr, br]:
        assert p.offset.length_squared() == 0
    assert bottom_point.offset.length_squared() != 0, "Offset should be applied to p2."
    assert top_point.offset.length_squared() != 0, "Offset should be applied to p4."
    bottom_point.apply_accumulated_offset()
    top_point.apply_accumulated_offset()
    assert bottom_point.co.distance_to(top_point.co) == pytest.approx(minimal_width_large)

    #define the test when you are sure of the desired behavior
    blob.enforce_minimal_width(minimal_width_too_big, 50)
    for chain in blob.chain_loop:
        for point in chain.points:
            assert point.offset.magnitude_squared() > 0


