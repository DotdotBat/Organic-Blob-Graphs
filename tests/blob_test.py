from typing import List
from point import Point
from chain import Chain
from blob import Blob
from pygame.math import Vector2
import pytest
from blob import rotate_list

def test_blob_initialization():
    blob = Blob()
    assert blob.chain_loop == []


def test_from_chain_loop():
    p1 = Point(0, 0)
    p2 = Point(1, 0)
    p3 = Point(1, 1)
    chain1 = Chain.from_point_list([p1, p2])
    chain2 = Chain.from_point_list([p2, p3])
    
    blob = Blob.from_chain_loop([chain1, chain2])
    assert blob.chain_loop == [chain1, chain2]
    
    # Check blob reference in chains
    assert chain1.blob_right == blob or chain1.blob_left == blob
    assert chain2.blob_right == blob or chain2.blob_left == blob

def test_points_num():
    p1 = Point(0, 0)
    p2 = Point(1, 0)
    p3 = Point(1, 1)
    chain1 = Chain.from_point_list([p1, p2])
    chain2 = Chain.from_point_list([p2, p3, p1])
    
    blob = Blob.from_chain_loop([chain1, chain2])
    assert blob.points_num == 3  # 3 unique points

def test_get_point():
    p1 = Point(0, 0)
    p2 = Point(1, 0)
    p3 = Point(1, 1)
    p4 = Point(0, 1)
    chain = Chain.from_point_list([p1, p2, p3])
    chain2 = Chain.from_point_list([p3, p4, p1])
    blob = Blob.from_chain_loop([chain, chain2])
    assert blob.get_point(0) == p1
    assert blob.get_point(1) == p2
    assert blob.get_point(2) == p3
    assert blob.get_point(3) == p4

def test_demo_get_chain_and_on_chain_point_index_at():
    blob = create_valid_blob()
    for i in range(blob.points_num):
        demo_chain, demo_chain_point_i = blob.get_chain_and_on_chain_point_index_at(i)
        demo_point = demo_chain.points[demo_chain_point_i]
        chain, chain_point_i = blob.get_chain_and_on_chain_point_index_at(i)
        point = chain.points[chain_point_i]
        assert demo_point == point
        assert demo_chain == chain
        assert demo_chain_point_i == chain_point_i
   
def test_is_clockwise():
    p1 = Point(0, 0)
    p2 = Point(0, 1)
    p3 = Point(1, 1)
    p4 = Point(1, 0)
    chain1 = Chain.from_point_list([p1, p2])
    chain2 = Chain.from_point_list([p2, p3])
    chain3 = Chain.from_point_list([p3, p4])
    chain4 = Chain.from_point_list([p4, p1])
    
    blob_cw = Blob.from_chain_loop([chain1, chain2, chain3, chain4])
    assert blob_cw.is_clockwise() is False

    blob_ccw = Blob.from_chain_loop([chain4, chain3, chain2, chain1])
    assert blob_ccw.is_clockwise() is True

    #ultimately what matters is that
    assert blob_ccw.is_clockwise() != blob_cw.is_clockwise()

def test_get_inner_direction():
    p1 = Point(0, 0)
    p2 = Point(0, 1)
    p3 = Point(1, 1)
    p4 = Point(1, 0)
    chain1 = Chain.from_point_list([p1, p2])
    chain2 = Chain.from_point_list([p2, p3])
    chain3 = Chain.from_point_list([p3, p4])
    chain4 = Chain.from_point_list([p4, p1])
    
    blob = Blob.from_chain_loop([chain1, chain2, chain3, chain4])
    
    direction = blob.get_inner_direction(1)
    assert isinstance(direction, Vector2)
    p = blob.get_point(1)
    assert p == p2
    assert direction == Vector2(0.5, -0.5)



def test_cut_at():
    blob = create_valid_blob()
    for cut_location in range(blob.points_num):
        blob = create_valid_blob()
        expected_chains_amount = len(blob.chain_loop)
        if not blob.is_intersection_at(cut_location):
            expected_chains_amount += 1
        prev_chain, next_chain = blob.cut_at(cut_location)
        assert blob.is_intersection_at(cut_location)
        cut_point = blob.get_point(cut_location)
        assert prev_chain.common_endpoint(next_chain) == cut_point
        before_chain, after_chain = blob.get_chains_at_intersection(cut_location)
        # for b, p in zip(before_chain.points, prev_chain.points):
        #     assert b == p
        # for b, p in zip(after_chain.points, next_chain.points):
        #     assert b == p
        assert before_chain.points == prev_chain.points
        assert after_chain.points == next_chain.points
        assert blob.is_valid()


def test_spawn_small_blob():
    number_of_points = 3 + 4 + 5 + 6 - 4
    for spawn_location in range(number_of_points):
        p1 = Point(0, 0)
        p2 = Point(0, 100)
        p3 = Point(100, 100)
        p4 = Point(100, 0)
        chain1 = Chain.from_end_points(p1, p2, point_num= 3)
        chain2 = Chain.from_end_points(p2, p3, point_num= 4)
        chain3 = Chain.from_end_points(p3, p4, point_num= 5)
        chain4 = Chain.from_end_points(p4, p1, point_num= 6)
        
        blob = Blob.from_chain_loop([chain1, chain2, chain3, chain4])
        assert blob.is_valid(raise_errors=True)
        new_blob, chains_to_update = blob.spawn_small_blob(spawn_location)
        assert isinstance(new_blob, Blob)
        assert all(isinstance(c, Chain) for c in chains_to_update)
        assert blob.is_valid()
        assert new_blob.is_valid()

standard_valid_blob_point_number = 3+4+5+6 -4
def create_valid_blob(point_density:int = 1):
    # Helper function to create a valid blob with connected chains
    p1 = Point(0, 0)
    p2 = Point(0, 100)
    p3 = Point(100, 100)
    p4 = Point(100, 0)
    chain1 = Chain.from_end_points(p1, p2, point_num= 3 * point_density)
    chain2 = Chain.from_end_points(p2, p3, point_num= 4 * point_density)
    chain3 = Chain.from_end_points(p4, p3, point_num= 5 * point_density)
    chain4 = Chain.from_end_points(p4, p1, point_num= 6 * point_density)
    blob = Blob.from_chain_loop([chain1, chain2, chain3, chain4])
    blob.is_valid(raise_errors=True)
    return blob


def test_get_chains_between_intersections():
    blob = create_valid_blob()
    intersections = blob.intersection_indexes
    for length in range(1, len(intersections)-1):
        for i in range(len(intersections)-1):
            intersection = intersections[i]
            j = (i + length)%len(intersections)
            next_intersection = intersections[j]
            chains = blob.get_chains_between_intersections(intersection, next_intersection)
            assert len(chains) == length
            _, start_chain = blob.get_chains_at_intersection(intersection)
            end_chain, _ = blob.get_chains_at_intersection(next_intersection)
            assert chains[0] == start_chain
            assert chains[-1] == end_chain
            unique_chains = set(chains)
            assert len(chains) == len(unique_chains)



def test_is_intersection_at():
    blob = create_valid_blob()
    intersections = [0] + blob.intersection_indexes
    for i in range(blob.points_num):
        if i in intersections:
            assert blob.is_intersection_at(i) is True
        else:
            assert blob.is_intersection_at(i) is False



def test_get_chains_index_at_intersection():
    blob = create_valid_blob()
    for i, intersection in enumerate(blob.intersection_indexes):
        prev_chain_i, next_chain_i = blob.get_chains_indexes_at_intersection(intersection)
        expected_prev_i = i
        expected_next_i = (i+1)%len(blob.chain_loop)
        assert prev_chain_i == expected_prev_i
        assert next_chain_i == expected_next_i
        

def test_get_chains_at_intersection():
    blob = create_valid_blob()
    for i, intersection in enumerate(blob.intersection_indexes):
        expected_prev = blob.chain_loop[i]
        expected_next = blob.chain_loop[(i+1)%len(blob.chain_loop)]
        point = blob.get_point(intersection)
        prev_chain, next_chain = blob.get_chains_at_intersection(intersection)
        assert prev_chain.is_connected_to(next_chain)
        common_point = prev_chain.common_endpoint(next_chain)
        assert common_point == point
        assert prev_chain == expected_prev
        assert next_chain == expected_next

def test_is_chain_backwards():
    blob = create_valid_blob()
    assert blob.is_chain_backwards(0) is False
    assert blob.is_chain_backwards(2) is True
    normal_chain = blob.chain_loop[1]
    backwards_chain = blob.chain_loop[2]
    assert blob.is_chain_backwards(normal_chain) is False
    assert blob.is_chain_backwards(backwards_chain) is True

    p1 = Point(0,0)
    p2 = Point(0,1)
    p3 = Point(1,0)
    chain1 = Chain.from_point_list([p2, p1, p3])
    chain2 = Chain.from_point_list([p3, p2])
    mini_blob = Blob.from_chain_loop([chain1,chain2])
    assert mini_blob.is_valid(raise_errors=True)
    assert mini_blob.is_chain_backwards(chain1) is False
    assert mini_blob.is_chain_backwards(chain2) is False

    chain3 = Chain.from_point_list([p2, p3])
    small_blob = Blob.from_chain_loop([chain1, chain3])
    assert small_blob.is_chain_backwards(chain1) is False
    assert small_blob.is_chain_backwards(chain3) is True

    tiny_blob = Blob.from_chain_loop([chain3, chain1])
    assert tiny_blob.is_chain_backwards(chain3) is False
    assert tiny_blob.is_chain_backwards(chain1) is True


def test_swap_chains():
    p1 = Point(0, 0)
    p2 = Point(0, 100)
    p3 = Point(100, 100)
    p4 = Point(100, 0)
    chain1 = Chain.from_end_points(p1, p2, point_num= 3)
    chain2 = Chain.from_end_points(p2, p3, point_num= 4)
    chain3 = Chain.from_end_points(p3, p4, point_num= 5)
    chain4 = Chain.from_end_points(p4, p1, point_num= 6)
    
    blob = Blob.from_chain_loop([chain1, chain2, chain3, chain4])
    
    new_chain = Chain.from_end_points(p2, p4, point_num= 7)
    blob.swap_chains(chains_to_remove=[chain2, chain3], chains_to_insert=[new_chain])
    assert len(blob.chain_loop) == 3
    assert blob.chain_loop == [chain1, new_chain, chain4]

    blob.swap_chains(
        chains_to_insert=[chain2, chain3],
        chains_to_remove=[new_chain]
    )
    assert len(blob.chain_loop) == 4
    assert blob.chain_loop == [chain1, chain2, chain3, chain4]

    blob.swap_chains(
        chains_to_remove=[chain4, chain1],
        chains_to_insert=[new_chain]
    )
    assert len(blob.chain_loop) == 3
    assert blob.chain_loop == [chain2 ,chain3, new_chain]



def test_from_ivalid_chain_loop():
    p1 = Point(0, 0)
    p2 = Point(1, 0)
    p3 = Point(1, 1)
    chain1 = Chain.from_point_list([p1, p2])
    chain2 = Chain.from_point_list([p2, p3])
    
    invalid_blob = Blob.from_chain_loop([chain1, chain2])
    assert invalid_blob.chain_loop == [chain1, chain2]
    
    # Check blob reference in chains
    assert chain1.blob_right == invalid_blob or chain1.blob_left == invalid_blob
    assert chain2.blob_right == invalid_blob or chain2.blob_left == invalid_blob
    assert invalid_blob.is_valid() is not True
    
    chain3 = Chain.from_point_list([p1, p3])
    valid_blob = Blob.from_chain_loop([chain1, chain2, chain3])
    assert valid_blob.is_valid() is True

    
    valid_blob.chain_loop[0].blob_left, valid_blob.chain_loop[0].blob_right = valid_blob.chain_loop[0].blob_right, valid_blob.chain_loop[0].blob_left
    assert valid_blob.is_valid() is False
    valid_blob.chain_loop[0].blob_left = None
    valid_blob.chain_loop[0].blob_right = invalid_blob
    assert valid_blob.is_valid() is False
    valid_blob.chain_loop[0].blob_right = invalid_blob



def test_area_is_independent_of_blob_orientation():
    p1 = Point(0, 0)
    p2 = Point(0, 1)
    p3 = Point(1, 1)
    p4 = Point(1, 0)
    chain1 = Chain.from_point_list([p1, p2])
    chain2 = Chain.from_point_list([p2, p3])
    chain3 = Chain.from_point_list([p3, p4])
    chain4 = Chain.from_point_list([p4, p1])
    
    blob_cw = Blob.from_chain_loop([chain1, chain2, chain3, chain4])
    assert blob_cw.is_clockwise() is False

    blob_ccw = Blob.from_chain_loop([chain4, chain3, chain2, chain1])
    assert blob_ccw.is_clockwise() is True
    blob_cw.recalculate_area()
    blob_ccw.recalculate_area()
    assert blob_cw.area == 1.0 
    assert blob_ccw.area == 1.0 

    blob = create_valid_blob()
    blob.recalculate_area()
    assert blob.area == pytest.approx(100*100)

def test_calculate_area_single_chain():
    p1 = Point(0, 0)
    p2 = Point(1, 0)
    chain = Chain.from_point_list([p1, p2])
    niahc = Chain.from_point_list([p2, p1])
    
    blob = Blob.from_chain_loop([chain,niahc])
    blob.recalculate_area()
    blob.area== 0.0  # No area for a line




def test_set_blob_references_on_chains():
    blob = create_valid_blob()
    is_blob_on_the_left = [bool(chain.blob_left) for chain in blob.chain_loop]
    for chain in blob.chain_loop:
        chain.set_blobs(None, None)

    blob.set_blob_reference_on_chains()
    assert all(c.blob_left == blob or c.blob_right == blob for c in blob.chain_loop)
    for i, chain in enumerate(blob.chain_loop):
        if is_blob_on_the_left[i]:
            assert chain.blob_left == blob
            assert chain.blob_right == None
        else:
            assert chain.blob_left == None
            assert chain.blob_right == blob

def test_get_intersections():
    blob = create_valid_blob()
    intersections = blob.intersection_indexes
    assert len(intersections) == 4
    print(intersections)
    assert intersections == [2, 5, 9, 14]
    assert blob.points_num == intersections[-1]

def test_create_point_between_indexes():
    valid_blob_point_number = standard_valid_blob_point_number
    for point_index in range(valid_blob_point_number):
        blob = create_valid_blob()
        _, next_index = blob.neighboring_indexes(point_index)
        point1 = blob.get_point(point_index)
        point2 = blob.get_point(next_index)
        
        new_point = blob.create_midpoint(point_index, next_index)
        
        # Check that the number of points increased by one
        assert blob.points_num == valid_blob_point_number + 1
        
        # Check that the new point is approximately in the middle
        expected_midpoint_co = (point1.co + point2.co) / 2
        
        assert new_point.co.x == pytest.approx(expected_midpoint_co.x)
        assert new_point.co.y == pytest.approx(expected_midpoint_co.y)
        
        # Check that the new point is accessible by the i+1 index
        assert blob.get_point(point_index) == point1
        _, next_index = blob.neighboring_indexes(point_index)
        assert blob.get_point(next_index) == new_point

        assert blob.is_valid(raise_errors=True)

def test_get_chain_and_indexes_of_neighbors():
    blob = create_valid_blob()
    
    for point_index in range(blob.points_num):
        next_index = (point_index + 1) % blob.points_num
        chain, index1, index2 = blob.get_chain_and_indexes_of_neighbors(point_index, next_index)
        assert index1 >= 0
        assert index2 >= 0
        assert index1 < chain.points_number
        assert index2 < chain.points_number
        point1_blob = blob.get_point(point_index)
        point2_blob = blob.get_point(next_index)
        point1_chain = chain.points[index1]
        point2_chain = chain.points[index2]

        assert point1_blob == point1_chain
        assert point2_blob == point2_chain

def test_get_points_common_chain():
    blob = create_valid_blob()
    for point_index in range(blob.points_num):
        next_index = (point_index + 1) % blob.points_num     
        common_chain = blob.get_points_common_chain(point_index, next_index)
        point1 = blob.get_point(point_index)
        point2 = blob.get_point(next_index)
        assert point1 in common_chain.points
        assert point2 in common_chain.points
        assert common_chain in blob.chain_loop

def test_get_chains_at_point():
    blob = create_valid_blob()
    intersections = [0] + blob.intersection_indexes
    for point_index in range(blob.points_num):
        chains_at_point = blob.get_chains_at_point(point_index)
        if point_index in intersections:
            assert len(chains_at_point) == 2
        else:
            assert len(chains_at_point) == 1
        point = blob.get_point(point_index)
        for chain in chains_at_point:
            assert point in chain.points
        for chain in chains_at_point:
            assert chain in blob.chain_loop

def test_remove_point_between_indexes():
    valid_blob_point_number = standard_valid_blob_point_number
    for point_index in range(valid_blob_point_number):
        blob = create_valid_blob()
        second_blob, chains = blob.spawn_small_blob(0)
        _, next_index = blob.neighboring_indexes(point_index)
        _, next_next_index = blob.neighboring_indexes(next_index)
        point1 = blob.get_point(point_index)
        point2 = blob.get_point(next_index)
        point3 = blob.get_point(next_next_index)
        
        removed_point = blob.remove_point(next_index)

        assert blob.points_num == valid_blob_point_number - 1
        assert blob.get_point(point_index) == point1
        assert               removed_point == point2
        assert  blob.get_point(next_index) == point3

        #it actually can be point1 or point3, depending on the implementaion,
        #so if this is getting flagged, try chainging it. 
        #Though you really should know with which option you went.
        assert all(chain in point1.chains for chain in removed_point.chains)
        assert blob.is_valid(raise_errors=True)
        assert second_blob.is_valid(raise_errors=True)
        assert_references(blobs=[blob, second_blob])


def assert_references(blobs:List[Blob] = [], chains: List[Chain] = [], points:List[Point] = []):
    for blob in blobs:
        for chain in blob.chain_loop:
            cbr, cbl = chain.blob_right, chain.blob_left
            assert cbr == blob or cbl == blob
            #at least one of them is our blob.
            assert not cbr == cbl, f'both sides cannot be the same blob!' 
        
    if blobs != [] and chains == []:
        chains = {chain for blob in blobs for chain in blob.chain_loop}

    for chain in chains:
        if chain.blob_right:
            assert chain in chain.blob_right.chain_loop
        if chain.blob_left:
            assert chain in chain.blob_left.chain_loop
        if chain.blob_left and chain.blob_right:
            assert chain.blob_right != chain.blob_left

    for chain in chains:
        for point in chain.points:
            assert chain in point.chains, f"Chain not found in point's chains set for point {point}"
    
    # Create a set of all unique points
    if chains != [] and points == []:
        points = {point for chain in chains for point in chain.points}
    
    # Check each point
    for point in points:
        for chain in point.chains:
            assert point in chain.points, f"Point {point} not found in chain's points"

    if points == []:
        raise RuntimeError()
