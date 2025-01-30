

from pygame import Vector2
import pytest
from blob import Blob
from chain import Chain
from point import Point


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
    blob.assert_is_valid()
    return blob

def test_from_chain_loop():
    p1 = Point(0, 0)
    p2 = Point(1, 0)
    p3 = Point(1, 1)
    chain1 = Chain.from_point_list([p1, p2])
    chain2 = Chain.from_point_list([p2, p3])
    
    with pytest.raises(AssertionError):
        blob = Blob.from_chain_loop([chain1, chain2])
        blob.assert_is_valid()
        #loop is not cicular in nature
    chain2.switch_endpoint_to(p3, p1)
    blob = Blob.from_chain_loop([chain1, chain2])
    assert blob.chain_loop == [chain1, chain2]
    blob.assert_is_valid()

def test_points_num():
    p1 = Point(0, 0)
    p2 = Point(1, 0)
    p3 = Point(1, 1)
    chain1 = Chain.from_point_list([p1, p2])
    chain2 = Chain.from_point_list([p2, p3, p1])
    
    blob = Blob.from_chain_loop([chain1, chain2])
    assert blob.point_number == 3  # 3 unique points

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
    for i in range(blob.point_number):
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

standard_valid_blob_point_number = 3+4+5+6 -4

def test_cut_at():
    for cut_location in range(standard_valid_blob_point_number):
        blob = create_valid_blob()
        expected_chains_amount = len(blob.chain_loop)
        if not blob.is_intersection_at(cut_location):
            expected_chains_amount += 1
        prev_chain, next_chain = blob.cut_at(cut_location)
        assert len(blob.chain_loop) == expected_chains_amount
        assert blob.point_number == standard_valid_blob_point_number, "the cut operation should not change point number"
        assert blob.is_intersection_at(cut_location)
        cut_point = blob.get_point(cut_location)
        assert prev_chain.common_endpoint(next_chain) == cut_point
        before_chain, after_chain = blob.get_chains_at_intersection(cut_location)
        assert before_chain in [prev_chain, next_chain]
        assert after_chain in [next_chain, prev_chain]
        assert before_chain != after_chain
        blob.assert_is_valid()

def test_blob_comparison():
    blob = create_valid_blob()
    same_blob_chain_loop = []
    for chain in blob.chain_loop:
        c = Chain.from_point_list(chain.points)
        same_blob_chain_loop.append(c)
    same_blob = Blob.from_chain_loop(same_blob_chain_loop)
    assert blob == same_blob
    same_blob.chain_loop.reverse()
    assert blob == same_blob
    assert not same_blob.is_intersection_at(4) 
    c1, _ = same_blob.cut_at(4)
    assert blob == same_blob
    assert c1.point_number>2
    c1.remove_point(1)
    assert blob != same_blob

    one_chain = Chain.from_point_list(blob.points_list)
    one_chain.append_endpoint(one_chain.point_start, append_to_start=False)
    identical_blob = Blob.from_chain_loop([one_chain])
    start = one_chain.remove_point(one_chain.point_start)
    assert blob != identical_blob
    assert one_chain.point_end == start
    assert one_chain.point_start != start
    one_chain.append_endpoint(one_chain.point_start, append_to_start=False)
    assert blob == identical_blob
    one_chain.points.reverse()
    assert blob == identical_blob



def test_is_intersection_at():
    blob = create_valid_blob()
    intersections = [0] + blob.intersection_indexes
    for i in range(blob.point_number):
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
    mini_blob.assert_is_valid()
    assert mini_blob.is_chain_backwards(chain1) is False
    assert mini_blob.is_chain_backwards(chain2) is False

    chain3 = Chain.from_point_list([p2, p3])
    small_blob = Blob.from_chain_loop([chain1, chain3])
    assert small_blob.is_chain_backwards(chain1) is False
    assert small_blob.is_chain_backwards(chain3) is True

    tiny_blob = Blob.from_chain_loop([chain3, chain1])
    assert tiny_blob.is_chain_backwards(chain3) is False
    assert tiny_blob.is_chain_backwards(chain1) is True

from point import connect_point_list
def create_valid_blob_collection():
    xs = [1,2,3,1,2,3,0,1,3,4,0,4,0,4]
    ys = [3,3,3,2,2,2,1,1,1,1,0,0,4,4]
    result_points = [Point.from_coordinates(xs[i], ys[i]) for i in range(14)]
        # 10-----11
        # |       |
        # 6-7---8-9
        # | |   | |
        # | 3-4-5 |
        # | | | | |
        # | 0-1-2 |
        # |       |
        # 12-----13
    c2,c3,c4=[6,7],[7,8],[8,9]
    c5,c6 = [7,3], [8,5]
    c7,c8 = [3,4], [4,5]
    c9,c0,c1= [3,0,1],[4,1],[5,2,1]
    c10 = [6,10,11,9]
    c11 = [6,12,13,9]
    indices_list = [c0,c1,c2,c3,c4,c5,c6,c7,c8,c9,c10,c11]
    result_chains:list[Chain] = []
    for indices in indices_list:
        points = [result_points[i] for i in indices]
        chain = Chain.from_point_list(points)
        result_chains.append(chain)
    # o--10---o
    # |       |
    # o2o-3-o4o
    # | 5   6 |
    # | o7o8o |
    # | | 0 | |
    # | 9-o-1 |
    # |       |
    # o--11---o  
    chain_loops_indices =[ [10,2,3,4], [5,3,6,8,7], [7,0,9], [8,1,0], [2,5,9,1,6,4,11]]
    result_blobs:list[Blob] = []
    for chain_loop_indices in chain_loops_indices:
        chain_loop = [result_chains[i] for i in chain_loop_indices]
        result_blobs.append(Blob.from_chain_loop(chain_loop))
    return result_points, result_chains, result_blobs

def assert_no_doubles_in_list(l:list):
    for i, a in enumerate(l):
        for j, b in enumerate(l):
            if j!=i:
                assert b!=a
            
def test_create_valid_blob_collection():
    points, chains, blobs = create_valid_blob_collection()
    assert len(points)==14
    for point in points:
        point.assert_is_valid() 
    assert len(points) == len(set(points)), "points uniqueness check failed"

    assert len(chains)==12
    for chain in chains:
        chain.assert_is_valid()
    assert len(chains) == len(set(chains))

    assert len(blobs)==5
    for blob in blobs:
        blob.assert_is_valid()
    assert_no_doubles_in_list(blobs) 