from blob import Blob
from chain import Chain
from point import Point
import pytest

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
        start_big_area = big_blob.area
        start_small_area = small_blob.area
        assert big_blob.area > small_blob.area

        movable_chains = [chain for chain in all_chains if not chain.is_unmoving]
        assert len(movable_chains) > 0

        simulation.add_blob_area_equalization_offset(movable_chains)
        for chain in movable_chains:
            chain.apply_accumulated_offsets()
        
        big_blob.recalculate_area()
        small_blob.recalculate_area()
        if not(big_blob.area < start_big_area and small_blob.area > start_small_area):
            print(big_blob.area < start_big_area)
            pass
        assert big_blob.area < start_big_area
        assert small_blob.area > start_small_area


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
    for point_index in range(blob.points_num):
        # Remove a point
        point_to_remove = blob.get_point(point_index)
        blob.remove_point(point_index)
        
        # Test that the point is removed
        assert point_to_remove not in [point for chain in blob.chain_loop for point in chain.points]
        
        # Find the biggest gap
        index1, index2 = blob.find_biggest_gap_indexes()
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

