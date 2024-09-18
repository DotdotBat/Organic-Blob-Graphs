from blob import Blob
from chain import Chain
from point import Point
import random

import simulation
def test_apply_blob_area_equalization_force():
    blob_point_num = 30 + 40 + 50 + 60 - 4
    for spawn_location in range(blob_point_num * 2): #this test failes in about a third of the runs. I don't want to rely on chance
        p1 = Point(0, 0)
        p2 = Point(0, 100)
        p3 = Point(100, 100)
        p4 = Point(100, 0)
        chain1 = Chain.from_end_points(p1, p2, point_num= 30)
        chain2 = Chain.from_end_points(p2, p3, point_num= 40)
        chain3 = Chain.from_end_points(p4, p3, point_num= 50)
        chain4 = Chain.from_end_points(p4, p1, point_num= 60)
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

