


def test_common_endpoint():
    p1 = Point(0, 0)
    p2 = Point(1, 1)
    c1 = Chain.from_point_list([p1, p2])
    c2 = Chain.from_point_list([p2, Point(2, 2)])
    assert c1.common_endpoint(c2) == p2

def are_collinear(v1:Vector2, v2:Vector2):
    scalar = v1.cross(v2)
    return scalar == pytest.approx(0)

def test_are_collinear():
    v1 = Vector2(1, 2)
    v2 = Vector2(2, 4)
    v3 = Vector2(2, 0)
    v4 = Vector2(0, 3)
    
    assert are_collinear(v1, v2) is True
    assert are_collinear(v1, v3) is False
    assert are_collinear(v3, v4) is False


def test_right_direction():
    p1 = Point(2,4)
    p2 = Point(1,3)
    p3 = Point(1,2)
    p4 = Point(0,2)
    p5 = Point(0,1)
    p6 = Point(0,0)
    chain = Chain.from_point_list([p1, p2, p3, p4, p5, p6])
    #I have doodled in my notebook. And here are the expected right side normals:
    expected_normals = [
        Vector2(1,-1),
        Vector2(2,-1),
        Vector2(1,-1),
        Vector2(1,-1),
        Vector2(1, 0),
        Vector2(1, 0)
    ]
    for i, point in enumerate(chain.points):
        n = chain.right_normal_at(i)
        assert isinstance(n, Vector2)
        expected_n = expected_normals[i]
        assert are_collinear(n, expected_n)

def test_add_right_offset():
    p1 = Point(2, 4)
    p2 = Point(1, 3)
    p3 = Point(1, 2)
    p4 = Point(0, 2)
    p5 = Point(0, 1)
    p6 = Point(0, 0)
    chain = Chain.from_point_list([p1, p2, p3, p4, p5, p6])
    
    # Defined expected normals (not normalized)
    expected_normals = [
        Vector2(1,-1),
        Vector2(2,-1),
        Vector2(1,-1),
        Vector2(1,-1),
        Vector2(1, 0),
        Vector2(1, 0)
    ]
    
    # Normalize expected normals
    expected_normals = [n.normalize() for n in expected_normals]
    
    # Apply positive offset
    offset_magnitude = 1.0
    original_positions = [p.co.copy() for p in chain.points]
    
    chain.add_right_offset(offset_magnitude, ignore_umoving_status=True)
    chain.apply_accumulated_offsets(ignore_unmoving_status=True)
    chain.assert_is_valid()
    
    # Check new positions for positive offset
    for i, point in enumerate(chain.points):
        expected_position = original_positions[i] + expected_normals[i] * offset_magnitude
        assert point.co.x == pytest.approx(expected_position.x)
        assert point.co.y == pytest.approx(expected_position.y)
    
    chain.add_right_offset(3.4,ignore_umoving_status=True)
    chain.add_right_offset(-3.4,ignore_umoving_status=True)
    for point in chain.points:
        assert point.offset.x == pytest.approx(0)
        assert point.offset.y == pytest.approx(0)
    

from blob_test import create_valid_blob
def test_get_on_blob_point_index():
    blob = create_valid_blob()
    for chain in blob.chain_loop:
        for i in range(chain.point_number):
            blob_point_index = chain.get_on_blob_point_index(blob, i)
            chain_point = chain.points[i]
            blob_point = blob.get_point(blob_point_index)
            assert chain_point == blob_point


def test_insert_midpoint():
    # Create a chain with three points
    p1 = Point(0, 0)
    p2 = Point(5, 0)
    chain_points_number = 5
    for i in range(chain_points_number - 1):
        chain = Chain.from_end_points(p1, p2, point_num=chain_points_number)
        point1 = chain.points[i]
        next_i = i+1
        point2 = chain.points[next_i]
        midpoint = chain.create_midpoint(i, next_i)
        assert chain.point_number == chain_points_number + 1
        expected_midpoint_co = (point1.co + point2.co) / 2
        
        #vectors and approx don't work together. compare x and y seperately
        assert midpoint.co.x == pytest.approx(expected_midpoint_co.x)
        assert midpoint.co.y == pytest.approx(expected_midpoint_co.y)
        assert chain.points[i]     == point1
        assert chain.points[i + 1] == midpoint
        next_i = (i+2)% chain.point_number
        assert chain.points[next_i] == point2
        chain.assert_is_valid()
        
import pytest
from point import Point
from chain import Chain

from blob_test import assert_references
def test_point_chains_references_management():
    # Step 1: Create some points
    p1 = Point(0, 0)
    p2 = Point(1, 0)
    p3 = Point(2, 0)
    p4 = Point(3, 0)
    p5 = Point(4, 0)
    p6 = Point(5, 0)
    points = [p1,p2,p3,p4,p5,p6]
    assert_references(points=points)
    
    # Step 2: Create some chains from them
    chain1 = Chain.from_point_list([p1, p2])
    chain2 = Chain.from_coord_list([(10,40), (30, 20)])
    chain3 = Chain.from_end_points(p3, p4, point_num=3)
    chains = [chain1,chain2,chain3]
    assert_references(chains=chains, points=points)
    
    # Step 3: Add a point to a chain
    chain1.append_endpoint(p5, append_to_start=False)
    assert_references(chains=chains)
    
    # Step 4: Remove a point from a chain
    chain1.remove_point(p2)
    chain3.remove_point(1)
    assert_references(chains=chains)
    assert_references(points=points)
    
    # Step 5: Add a point from one chain to another chain
    chain1.append_endpoint(p3, append_to_start=True)
    assert_references(chains=chains)
    assert_references(points=points)
    
    # Step 6: Swap a point on a chain for another point that wasn't on that chain
    chain1.swap_point(p1, p6)
    assert_references(chains=chains)
    assert_references(points=points)

    
    # Step 7: create middle point
    midpoint = chain2.create_midpoint(0, 1)
    assert_references(chains=chains)
    points.append(midpoint)
    assert_references(points= points)

    #Step 8: cut chain into two
    chain2a, chain2b = chain2.cut(1)
    chains.append(chain2b)
    assert chain2a in chains
    assert_references(chains=chains)
    assert_references(points= points)
    for chain in chains:
        chain.assert_is_valid()


def test_find_biggest_gap_basic_case():
    p1 = Point(0, 0)
    p2 = Point(1, 0)
    p3 = Point(3, 0)  # Biggest gap between p2 and p3
    p4 = Point(4, 0)
    chain = Chain.from_point_list([p1, p2, p3, p4])
    
    index_a, index_b, gap_length = chain.find_biggest_gap()
    assert (index_a, index_b) == (1, 2)
    assert gap_length == pytest.approx(2.0)

def test_find_biggest_gap_single_pair():
    p1 = Point(0, 0)
    p2 = Point(1, 0)
    chain = Chain.from_point_list([p1, p2])
    
    index_a, index_b, gap_length = chain.find_biggest_gap()
    assert (index_a, index_b) == (0, 1)
    assert gap_length == pytest.approx(1.0)

def test_find_biggest_gap_multiple_same_gaps():
    p1 = Point(0, 0)
    p2 = Point(2, 0)
    p3 = Point(4, 0)
    chain = Chain.from_point_list([p1, p2, p3])
    
    index_a, index_b, gap_length = chain.find_biggest_gap()
    assert (index_a, index_b) in [(0, 1), (1, 2)]
    assert gap_length == pytest.approx(2.0)

def test_find_biggest_gap_on_too_short_chains():
    p1 = Point(0, 0)
    chain1 = Chain.from_point_list([p1])
    
    with pytest.raises(ValueError):
        chain1.find_biggest_gap()

    chain0 = Chain()
    
    with pytest.raises(ValueError):
        chain0.find_biggest_gap()

from simulation import find_all_endpoints


def test_find_all_endpoints_basic_case():
    p1 = Point(0, 0)
    p2 = Point(1, 1)
    p3 = Point(2, 2)
    p4 = Point(3, 3)
    p5 = Point(4, 4)

    chain1 = Chain.from_point_list([p1, p2, p3])  # Endpoints are p1, p3
    chain2 = Chain.from_end_points(p4, p5, point_num=3)  # Endpoints are p4, p5
    chains = [chain1, chain2]

    endpoints = find_all_endpoints(chains)
    expected_endpoints = {p1, p3, p4, p5}
    assert endpoints == expected_endpoints

def test_find_all_endpoints_shared_endpoints():
    p1 = Point(0, 0)
    p2 = Point(1, 1)
    p3 = Point(2, 2)
    p4 = Point(3, 3)

    chain1 = Chain.from_point_list([p1, p2, p3])  # Endpoints are p1, p3
    chain2 = Chain.from_point_list([p3, p4])      # Endpoints are p3, p4
    chains = [chain1, chain2]

    endpoints = find_all_endpoints(chains)
    expected_endpoints = {p1, p3, p4}
    assert endpoints == expected_endpoints

def test_find_all_endpoints_no_chains():
    chains = []
    endpoints = find_all_endpoints(chains)
    expected_endpoints = set()
    assert endpoints == expected_endpoints

def test_find_all_endpoints_single_chain():
    p1 = Point(0, 0)
    p2 = Point(1, 1)
    p3 = Point(2, 2)

    chain = Chain.from_end_points(p1, p3, point_num=3)  # Endpoints are p1, p3
    chains = [chain]

    endpoints = find_all_endpoints(chains)
    expected_endpoints = {p1, p3}
    assert endpoints == expected_endpoints

def test_find_all_endpoints_identical_endpoints():
    p1 = Point(0, 0)
    p2 = Point(1, 1)

    chain1 = Chain.from_end_points(p1, p2, point_num=3)  # Endpoints are p1, p2
    chain2 = Chain.from_end_points(p1, p2, point_num=3)  # Endpoints are p1, p2
    chains = [chain1, chain2]

    endpoints = find_all_endpoints(chains)
    expected_endpoints = {p1, p2}
    assert endpoints == expected_endpoints

def test_find_all_endpoints_chain_with_no_points():
    chain = Chain()
    chains = [chain]

    endpoints = find_all_endpoints(chains)
    expected_endpoints = set()
    assert endpoints == expected_endpoints

def test_find_all_endpoints_chain_with_one_point():
    p1 = Point(0, 0)
    chain = Chain.from_point_list([p1])
    chains = [chain]

    endpoints = find_all_endpoints(chains)
    expected_endpoints = {p1}
    assert endpoints == expected_endpoints

def test_neighboring_point_of_endpoint_basic_case():
    p1 = Point(0, 0)
    p2 = Point(1, 1)
    p3 = Point(2, 2)

    chain = Chain.from_point_list([p1, p2, p3])  # Endpoints are p1, p3

    neighbor = chain.endpoint_neighbor(p1)
    assert neighbor == p2

    neighbor = chain.endpoint_neighbor(p3)
    assert neighbor == p2

def test_neighboring_point_of_endpoint_single_point_chain():
    p1 = Point(0, 0)
    chain = Chain.from_point_list([p1])

    non_existant_neigbor = chain.endpoint_neighbor(p1)
    assert non_existant_neigbor is None

def test_neighboring_point_of_endpoint_two_point_chain():
    p1 = Point(0, 0)
    p2 = Point(1, 1)

    chain = Chain.from_point_list([p1, p2])

    neighbor = chain.endpoint_neighbor(p1)
    assert neighbor == p2

    neighbor = chain.endpoint_neighbor(p2)
    assert neighbor == p1

def test_neighboring_point_of_invalid_endpoint():
    p1 = Point(0, 0)
    p2 = Point(1, 1)
    p3 = Point(2, 2)
    p4 = Point(3, 3)

    chain = Chain.from_point_list([p1, p2, p3])

    with pytest.raises(ValueError):  # Assuming it raises an error
        chain.endpoint_neighbor(p4)



def test_dissolve_endpoint_basic_merge():
    p1 = Point(0, 0)
    p2 = Point(1, 1)
    p3 = Point(2, 2)
    p4 = Point(3, 3)

    chain1 = Chain.from_point_list([p1, p2])
    chain2 = Chain.from_point_list([p2, p3, p4])
    chain1.assert_is_valid()
    chain2.assert_is_valid()

    # Dissolve endpoint p2 which connects both chains
    p2.dissolve_endpoint()

    # Check that chain2 is empty
    assert chain2.points == [] or chain1.points == []

    empty_chain = chain1 if len(chain1.points)==0 else chain2
    full_chain = chain2 if empty_chain == chain1 else chain1
    # Check that chain1 now contains all points
    for point in [p1, p2, p3, p4]:
        assert point in full_chain.points
    full_chain.assert_is_valid()

def test_dissolve_endpoint_order_preservation():
    p1 = Point(0, 0)
    p2 = Point(1, 1)
    p3 = Point(2, 2)
    p4 = Point(3, 3)

    chain1 = Chain.from_point_list([p2, p1])
    chain2 = Chain.from_point_list([p2, p3, p4])

    # Dissolve endpoint p2
    p2.dissolve_endpoint()

    # Ensure order is preserved
    assert chain1.points == [p1, p2, p3, p4] or [p4, p3, p2, p1]

def test_dissolve_endpoint_invalid_endpoint():
    p1 = Point(0, 0)
    p2 = Point(1, 1)
    p3 = Point(2, 2)
    p4 = Point(0, 2)
    p5 = Point(2, 0)

    chain = Chain.from_point_list([p1, p2, p3])
    chain2 = Chain.from_point_list([p3, p4])
    chain3 = Chain.from_point_list([p3, p5])

    # p1 has only one chain
    with pytest.raises(ValueError):
        p1.dissolve_endpoint()

    #p2 is not an endpoint
    with pytest.raises(ValueError):
        p2.dissolve_endpoint()

    # p3 connects 3 points instead of 2
    with pytest.raises(ValueError):
        p3.dissolve_endpoint()

from blob import Blob

def test_switch_blob_references_both_none():
    chain = Chain()
    chain.blob_right = None
    chain.blob_left = None
    
    chain.swap_blob_references()
    
    assert chain.blob_right is None
    assert chain.blob_left is None

def test_switch_blob_references_one_none():
    blob = Blob()
    chain = Chain()
    chain.blob_right = blob
    chain.blob_left = None
    
    chain.swap_blob_references()
    
    assert chain.blob_right is None
    assert chain.blob_left == blob

def test_switch_blob_references_both_set():
    blob1 = Blob()
    blob2 = Blob()
    chain = Chain()
    chain.blob_right = blob1
    chain.blob_left = blob2
    
    chain.swap_blob_references()
    
    assert chain.blob_right == blob2
    assert chain.blob_left == blob1

def test_switch_blob_references_same_blob():
    blob = Blob()
    chain = Chain()
    chain.blob_right = blob
    chain.blob_left = blob
    
    with pytest.raises(ValueError):
        chain.swap_blob_references()

def test_switch_blob_references_no_blobs():
    chain = Chain()
    
    chain.swap_blob_references()
    
    assert chain.blob_right is None
    assert chain.blob_left is None


import pytest
from point import Point
from chain import Chain
from blob_test import assert_references

def test_switch_endpoint_to_start():
    p1 = Point(0, 0)
    p2 = Point(1, 1)
    p3 = Point(2, 2)
    target = Point(3, 3)
    points = [p1, p2, p3, target]

    chain = Chain.from_point_list([p1, p2, p3])
    chains = [chain]
    assert_references(chains=chains, points=points)
    chain.assert_is_valid()

    chain.switch_endpoint_to(p1, target)

    assert chain.point_start == target
    assert chain.points == [target, p2, p3]
    assert_references(chains=chains, points=points)
    chain.assert_is_valid()

def test_switch_endpoint_to_end():
    p1 = Point(0, 0)
    p2 = Point(1, 1)
    p3 = Point(2, 2)
    target = Point(3, 3)
    points = [p1, p2, p3, target]

    chain = Chain.from_point_list([p1, p2, p3])
    chains = [chain]
    assert_references(chains=chains, points=points)

    chain.switch_endpoint_to(p3, target)

    assert chain.point_end == target
    assert chain.points == [p1, p2, target]
    assert_references(chains=chains, points=points)
    chain.assert_is_valid()

def test_switch_endpoint_to_invalid_endpoint():
    p1 = Point(0, 0)
    p2 = Point(1, 1)
    p3 = Point(2, 2)
    invalid = Point(4, 4)
    target = Point(3, 3)
    points = [p1, p2, p3, invalid, target]

    chain = Chain.from_point_list([p1, p2, p3])
    chains = [chain]
    assert_references(chains=chains, points=points)
    
    with pytest.raises(ValueError):
        chain.switch_endpoint_to(invalid, target)

    assert chain.points == [p1, p2, p3]
    assert_references(chains=chains, points=points)

def test_switch_endpoint_to_same_point():
    p1 = Point(0, 0)
    p2 = Point(1, 1)
    p3 = Point(2, 2)
    points = [p1, p2, p3]

    chain = Chain.from_point_list([p1, p2, p3])
    chains = [chain]
    assert_references(chains=chains, points=points)

    chain.switch_endpoint_to(p1, p1)

    assert chain.points == [p1, p2, p3]
    assert_references(chains=chains, points=points)

def test_switch_endpoint_to_no_points():
    target = Point(1, 1)
    chain = Chain()
    points = [target]
    chains = [chain]

    with pytest.raises(ValueError):
        chain.switch_endpoint_to(Point(0, 0), target)

    assert chain.points == []
    assert_references(chains=chains, points=points)

def test_switch_endpoint_to_one_point_chain():
    p1 = Point(0, 0)
    target = Point(1, 1)
    points = [p1, target]

    chain = Chain.from_point_list([p1])
    chains = [chain]
    assert_references(chains=chains, points=points)

    chain.switch_endpoint_to(p1, target)

    assert chain.point_start == target
    assert chain.point_end == target
    assert chain.points == [target]
    assert_references(chains=chains, points=points)
    with pytest.raises(AssertionError):
        chain.assert_is_valid()#it is a one point chain, it is invalid

##################################

# blob_test.py

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
    
    with pytest.raises(AssertionError):
        blob = Blob.from_chain_loop([chain1, chain2])
        #loop is not cicular in nature
    chain2.switch_endpoint_to(p3, p1)
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



def test_cut_at():
    for cut_location in range(standard_valid_blob_point_number):
        blob = create_valid_blob()
        expected_chains_amount = len(blob.chain_loop)
        if not blob.is_intersection_at(cut_location):
            expected_chains_amount += 1
        prev_chain, next_chain = blob.cut_at(cut_location)
        assert blob.point_number == standard_valid_blob_point_number, "the cut operation should not change point number"
        assert blob.is_intersection_at(cut_location)
        cut_point = blob.get_point(cut_location)
        assert prev_chain.common_endpoint(next_chain) == cut_point
        before_chain, after_chain = blob.get_chains_at_intersection(cut_location)
        assert before_chain in [prev_chain, next_chain]
        assert after_chain in [next_chain, prev_chain]
        assert blob.assert_is_valid()


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
        blob.assert_is_valid()
        new_blob, chains_to_update = blob.spawn_small_blob(spawn_location)
        assert isinstance(new_blob, Blob)
        assert all(isinstance(c, Chain) for c in chains_to_update)
        assert blob.assert_is_valid()
        assert new_blob.assert_is_valid()

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
    blob.assert_is_valid()
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
    
    with pytest.raises(ValueError):
        invalid_blob = Blob.from_chain_loop([chain1, chain2]) #The chain isn't closed
    
    chain3 = Chain.from_point_list([p1, p3])
    valid_blob = Blob.from_chain_loop([chain1, chain2, chain3])
    valid_blob.assert_is_valid() is True

    first_chain = valid_blob.chain_loop[0]
    #switching them up
    first_chain.blob_left, first_chain.blob_right = first_chain.blob_right, first_chain.blob_left
    assert valid_blob.assert_is_valid() is False
    first_chain.blob_left = None
    assert valid_blob.assert_is_valid() is False



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
    assert blob_cw.cashed_area == 1.0 
    assert blob_ccw.cashed_area == 1.0 

    blob = create_valid_blob()
    blob.recalculate_area()
    assert blob.cashed_area == pytest.approx(100*100)

def test_calculate_area_single_chain():
    p1 = Point(0, 0)
    p2 = Point(1, 0)
    chain = Chain.from_point_list([p1, p2])
    niahc = Chain.from_point_list([p2, p1])
    
    blob = Blob.from_chain_loop([chain,niahc])
    blob.recalculate_area()
    blob.cashed_area== 0.0  # No area for a line




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
    assert blob.point_number == intersections[-1]

def test_create_point_between_indexes():
    valid_blob_point_number = standard_valid_blob_point_number
    for point_index in range(valid_blob_point_number):
        blob = create_valid_blob()
        _, next_index = blob.neighboring_indexes(point_index)
        point1 = blob.get_point(point_index)
        point2 = blob.get_point(next_index)
        
        new_point = blob.create_midpoint(point_index, next_index)
        
        # Check that the number of points increased by one
        assert blob.point_number == valid_blob_point_number + 1
        
        # Check that the new point is approximately in the middle
        expected_midpoint_co = (point1.co + point2.co) / 2
        
        assert new_point.co.x == pytest.approx(expected_midpoint_co.x)
        assert new_point.co.y == pytest.approx(expected_midpoint_co.y)
        
        # Check that the new point is accessible by the i+1 index
        assert blob.get_point(point_index) == point1
        _, next_index = blob.neighboring_indexes(point_index)
        assert blob.get_point(next_index) == new_point

        blob.assert_is_valid()

def test_get_chain_and_indexes_of_neighbors():
    blob = create_valid_blob()
    
    for point_index in range(blob.point_number):
        next_index = (point_index + 1) % blob.point_number
        chain, index1, index2 = blob.get_chain_and_indexes_of_neighbors(point_index, next_index)
        assert index1 >= 0
        assert index2 >= 0
        assert index1 < chain.point_number
        assert index2 < chain.point_number
        point1_blob = blob.get_point(point_index)
        point2_blob = blob.get_point(next_index)
        point1_chain = chain.points[index1]
        point2_chain = chain.points[index2]

        assert point1_blob == point1_chain
        assert point2_blob == point2_chain

def test_get_points_common_chain():
    blob = create_valid_blob()
    for point_index in range(blob.point_number):
        next_index = (point_index + 1) % blob.point_number     
        common_chain = blob.get_points_common_chain(point_index, next_index)
        point1 = blob.get_point(point_index)
        point2 = blob.get_point(next_index)
        assert point1 in common_chain.points
        assert point2 in common_chain.points
        assert common_chain in blob.chain_loop

def test_get_chains_at_point():
    blob = create_valid_blob()
    intersections = [0] + blob.intersection_indexes
    for point_index in range(blob.point_number):
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
        point_index+=0
        blob = create_valid_blob()
        second_blob, chains = blob.spawn_small_blob(7)
        point_num_before_cut = blob.point_number
        prev_index, next_index = blob.neighboring_indexes(point_index)
        point1 = blob.get_point(prev_index)
        point2 = blob.get_point(point_index)
        point3 = blob.get_point(next_index)
        common_chain = blob.get_points_common_chain(point_index, next_index)
        
        removed_point_chains_before_removal = point2.chains.copy()
        removed_point = blob.remove_point(point_index)
        new_blob_point_num = blob.point_number
        assert blob.point_number == point_num_before_cut - 1
        prev_index, _ = blob.neighboring_indexes(point_index)
        next_index = point_index 
        assert blob.get_point(prev_index) == point1
        assert               removed_point == point2
        assert  blob.get_point(next_index) == point3

        #it actually can be point1 or point3, depending on the implementaion,
        #so if this is getting flagged, try changing it. 
        #Though you really should know with which option you went.
        for chain in removed_point_chains_before_removal:
            chain:Chain
            if chain.point_number>0: 
                assert chain in point3.chains
            else:
                assert chain is common_chain
        blob.assert_is_valid()
        second_blob.assert_is_valid()
        assert_references(blobs=[blob, second_blob])


def assert_references(blobs:List[Blob] = [], chains: List[Chain] = [], points:List[Point] = []):
    """checks that all existing references are mutual. Will not catch an error if the reference is absent from both sides. Flags only one-sided references."""
    if blobs != []:
        blob_chains = {chain for blob in blobs for chain in blob.chain_loop}
        blob_chains.update(chains)
        chains = list(blob_chains)

    if chains != []:
        chains_points = {point for chain in chains for point in chain.points}
        chains_points.update(points)
        points = list(chains_points)

    #blob -> chain
    for blob in blobs:
        for chain in blob.chain_loop:
            cbr, cbl = chain.blob_right, chain.blob_left
            assert cbr == blob or cbl == blob
            #at least one of them is our blob.
            assert not cbr == cbl, f'both sides cannot be the same blob!' 

    #chain -> blob
    for chain in chains:
        if chain.blob_right:
            assert chain in chain.blob_right.chain_loop
        if chain.blob_left:
            assert chain in chain.blob_left.chain_loop
        if chain.blob_left and chain.blob_right:
            assert chain.blob_right != chain.blob_left

    #chain -> point
    for chain in chains:
        for point in chain.points:
            assert chain in point.chains, f"Chain not found in point's chains set for point {point}"
    
    #point -> chain
    for point in points:
        for chain in point.chains:
            assert point in chain.points, f"Point {point} not found in chain's points"

    #point-point
    for point in points:
        point.assert_point_is_valid()

    if points == []:
        raise RuntimeError()
    

def test_index_distance():
    blob = create_valid_blob()
    assert blob.index_distance(0, 1) == 1
    assert blob.index_distance(1, 0) == 1
    assert blob.index_distance(0, blob.point_number - 1) == 1
    assert blob.index_distance(0, 0) == 0

def test_circumference_distance():
    link_length = 10
    blob = create_valid_blob()
    assert blob.circumference_distance(0, 1, link_length) == link_length
    assert blob.circumference_distance(1, 0, link_length) == link_length
    assert blob.circumference_distance(0, blob.point_number - 1, link_length) == link_length
    assert blob.circumference_distance(0, 0, link_length) == 0

def test_points_distance():
    
    blob = create_valid_blob()
    point_a = blob.get_point(0)
    point_b = blob.get_point(1)
    point_a.co.x = 0
    point_a.co.y = 0
    point_b.co.x = 3
    point_b.co.y = 4
    assert blob.points_distance(0, 1) == 5
    assert blob.points_distance(1, 0) == 5
    assert blob.points_distance(0, 0) == 0


def test_one_chain_blob():
    points = [
        Point(0, 0),
        Point(1, 0),
        Point(1, 1),
        Point(0, 1)
    ]
    unclosed_chain = Chain.from_point_list(points)
    with pytest.raises(ValueError):
        unclosed_blob = Blob.from_chain_loop([unclosed_chain])

    points.append(points[0])
    for point in points:
        point.chains.clear()
    closed_chain = Chain.from_point_list(points)
    closed_blob = Blob.from_chain_loop([closed_chain])
    assert closed_blob.is_clockwise() is True
    closed_blob.assert_is_valid()
    assert_references(blobs=[closed_blob])
    closed_blob.cut_at(1)
    assert len(closed_blob.chain_loop) ==2
    assert closed_blob.is_clockwise() is True
    assert_references(blobs=[closed_blob])
    closed_blob.assert_is_valid()
    
def test_dissolve_endpoint_remove_from_blobs():
    blob_up:Blob
    blob_down:Blob
    p_top:Point
    p_center:Point
    p_left:Point
    top_left:Chain
    right_top:Chain
    center_left:Chain
    center_right:Chain

    def setup():
        global blob_up, blob_down, p_top, p_center, p_left, top_left, right_top, center_left, center_right
        p_top = Point(0, 0)
        p_center = Point(0, 10)
        p_left = Point(-10, 20)
        p_right = Point(10, 20)

        bottom = Chain.from_point_list([p_left, p_right])
        bottom.name = "Bottom"
        center_left = Chain.from_end_points(start=p_center, end=p_left,point_num=10)
        center_left.name = "Center-Left"
        center_right = Chain.from_end_points(start=p_center, end= p_right,point_num=10)
        center_right.name = "Center-Right"
        top_left = Chain.from_end_points(start=p_top, end=p_left,point_num=10)
        top_left.name = "Top-Left"
        right_top = Chain.from_end_points(start=p_right, end=p_top,point_num=10)
        right_top.name = "Right-Top"

        blob_up = Blob.from_chain_loop([center_left, center_right, right_top, top_left])
        blob_up.name = "Up"
        blob_down=Blob.from_chain_loop([center_left, center_right, bottom])
        blob_down.name = "Down"
        return blob_up, blob_down, p_top, p_center, p_left, top_left, right_top, center_left, center_right

    def check_state():
        blob_up.assert_is_valid()
        blob_down.assert_is_valid()
        assert_references(blobs=[blob_up, blob_down])


    blob_up, blob_down, p_top, p_center, p_left, top_left, right_top, center_left, center_right = setup()
    check_state()
    center_left.merge_with(center_right)
    check_state()
    top_left.merge_with(right_top)
    check_state()
    blob_up, blob_down, p_top, p_center, p_left, top_left, right_top, center_left, center_right = setup()
    check_state()
    center_right.merge_with(center_left)
    check_state()
    setup()
    check_state()
    right_top.merge_with(top_left)
    check_state()

    blob_up, blob_down, p_top, p_center, p_left, top_left, right_top, center_left, center_right = setup()
    check_state()
    points_to_dissolve = [p_top, p_center]
    for p in points_to_dissolve:
        p_neighbors = p.get_connected_points_via_chains()
        p.dissolve_endpoint()
        check_state()
        assert set(p_neighbors) == set(p.get_connected_points_via_chains())
    
    with pytest.raises(ValueError):
        p_left.dissolve_endpoint()


def test_cut_at_shared_chain():

    #plan:
    #cut outer chain
    #cut shared chain
    #cut all points on a blob

    def setup():
        p1 = Point(0, 0)
        p2 = Point(1, 0)
        p3 = Point(2, 0)
        p4 = Point(0, 1)
        p5 = Point(1, 1)
        p6 = Point(2, 1)
        points = [p1, p2, p3,
                  p4, p5, p6]
        # here is a schema:
        #   1 -- 2 -- 3
        #   |    |    |
        #   4 -- 5 -- 6
        
        # horisontal
        chain_12 = Chain.from_end_points(p1, p2, point_num=3)
        chain_23 = Chain.from_end_points(p2, p3, point_num=3)
        chain_45 = Chain.from_end_points(p4, p5, point_num=3)
        chain_56 = Chain.from_end_points(p5, p6, point_num=3)

        # vertical
        chain_14 = Chain.from_end_points(p1, p4, point_num=3)
        chain_25 = Chain.from_end_points(p2, p5, point_num=3)
        chain_36 = Chain.from_end_points(p3, p6, point_num=3)
        chains = [chain_12, chain_23, chain_45, chain_56, 
                  chain_14, chain_25, chain_36]

        outher_chain = chain_12
        shared_chain = chain_25

        blob_left = Blob.from_chain_loop([chain_12, chain_25, chain_45, chain_14])
        blob_right = Blob.from_chain_loop([chain_23, chain_36, chain_56, chain_25])
        blobs = [blob_left, blob_right]
        return blobs, chains, points, outher_chain, shared_chain
    
    blobs, chains, points, outher_chain, shared_chain = setup()
    def check_state():
        for blob in blobs:
            blob.assert_is_valid()
        assert_references(blobs, chains, points)

    def check_result(result:tuple[Chain]):
        for chain in result:
            assert chain.point_number>1
        chain_a, chain_b = result
        assert chain_a != chain_b
        assert chain_a.is_connected_to(chain_b)
        check_state()

    check_result(outher_chain.cut(1)) #middle
    check_result(shared_chain.cut(1))
    
    blob = blobs[1]
    blobs, chains, points, outher_chain, shared_chain = setup()
    for i in range(blob.point_number):
        check_result(blob.cut_at(i))

    # inputting Point instead of index
    outher_chain_point = outher_chain.points[1]
    check_result(outher_chain.cut(outher_chain_point))

def test_get_points_common_chain_with_only_two_chains():
    # Case a: Blob with two chains, 5 points in one chain and 3 points in the other
    p1 = Point(0, 0)
    p2 = Point(100, 100)

    big_chain = Chain.from_end_points(p1, p2, point_num=5)  # 5 points
    small_chain = Chain.from_end_points(p1, p2, point_num=3)  # 5 points

    blob = Blob.from_chain_loop([big_chain, small_chain])

    # Get intersection indexes
    intersections = blob.intersection_indexes
    assert len(intersections) == 2
    assert intersections == [4, 6] #just testing my understanding
    central_index, index2 = intersections
    

    # Rule a: Always return the smaller chain (chain2)
    common_chain = blob.get_points_common_chain(central_index, index2)
    assert common_chain == small_chain
    common_chain = blob.get_points_common_chain(index2, central_index)
    assert common_chain == small_chain

    blob = blob.from_chain_loop([small_chain, big_chain])
    intersections = blob.intersection_indexes
    assert len(intersections) == 2
    central_index, index2 = intersections
    common_chain = blob.get_points_common_chain(central_index, index2)
    assert common_chain == small_chain
    common_chain = blob.get_points_common_chain(index2, central_index)
    assert common_chain == small_chain


    # Case c: Blob with two chains, both having 4 points
    first_chain = Chain.from_end_points(p1, p2, point_num=4)  # 5 points
    second_chain = Chain.from_end_points(p1, p2, point_num=4)  # 5 points

    blob = Blob.from_chain_loop([first_chain, second_chain])

    # Get intersection indexes
    intersections = blob.intersection_indexes
    assert len(intersections) == 2
    central_index, index2 = intersections

    # Rule c: Index order determines the result - only if the number of points on both chains is equal
    common_chain = blob.get_points_common_chain(central_index, index2)
    assert common_chain == second_chain

    common_chain = blob.get_points_common_chain(index2, central_index)
    assert common_chain == first_chain


###################################################

#simulaiton_test.py

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
    
###################################################33

#state_test.py

from blob import Blob
from chain import Chain
from point import Point
import state
from state import construct_state_from_point
def test_utility_functions():
    # 1 - - - 2
    # | \   / |
    # |  3-4  |
    # | /   \ |
    # 5 - 7 - 6 

    p1 = Point(0, 0)
    p2 = Point(1, 0)
    p3 = Point(0.3, 0.5)
    p4 = Point(0.7, 0.5)
    p5 = Point(0, 1)
    p6 = Point(1, 1)
    p7 = Point(0.5, 1)
    points = [p1,p2,p3,p4,p5,p6,p7]

    chain_12 = Chain.from_point_list([p1, p2])
    chain_26 = Chain.from_point_list([p2, p6])
    chain_57 = Chain.from_point_list([p5, p7])
    chain_67 = Chain.from_point_list([p6, p7])
    chain_51 = Chain.from_point_list([p5, p1])
    chain_13 = Chain.from_point_list([p1, p3])
    chain_24 = Chain.from_point_list([p2, p4])
    chain_64 = Chain.from_point_list([p6, p4])
    chain_53 = Chain.from_point_list([p5, p3])
    chain_34 = Chain.from_point_list([p3, p4])
    expected_chains =  {chain_12, chain_26, chain_57, chain_67, chain_51, chain_13, chain_24, chain_64, chain_53, chain_34}

    blob_1243 = Blob.from_chain_loop([chain_12, chain_24, chain_34, chain_13])
    blob_264 = Blob.from_chain_loop([chain_26, chain_64, chain_24])
    blob_64357 = Blob.from_chain_loop([chain_64, chain_34, chain_53, chain_57, chain_67])
    blob_135 = Blob.from_chain_loop([chain_13, chain_53, chain_51])

    blobs = [blob_1243, blob_264, blob_64357, blob_135]

    chains = state.get_chains_list(blobs)
    assert set(chains) == expected_chains, "get_chains_list returned incorrect chains"

    # Test `get_movable_chains`
    movable_chains = state.get_movable_chains(chains)
    expected_movable_chains = {chain_13, chain_24, chain_64, chain_53, chain_34}
    assert set(movable_chains) == expected_movable_chains, "get_movable_chains returned incorrect chains"

    # Test `get_movable_joints`
    movable_joints = state.get_wandering_joints(movable_chains)
    expected_movable_joints = set(points)
    expected_movable_joints.remove(p7) #it isn't connected to any movable chains
    assert set(movable_joints) == expected_movable_joints, "get_movable_joints returned incorrect points"

#####################################

# retrace_test.py

#the retrace system 
#instead of tediously keeping track of
# point_lists in chains, 
# chains lists in points
# blob lists in chains
# and chain lists in blobs
#I decided to represent the data as points and their connctions
#and all above structures will be created at runtime from them. 
#from connected points we get chains
#from connected chains we get blobs 
#to change something, just reconnect the points
#and the chains and blobs should be rebulid from the new structure
from point import Point
from chain import Chain

def test_get_chained_points_lists_from_connected_points():
    p1 = Point(0,0)
    p2 = Point(1,1)
    p3 = Point(2,2)
    p4 = Point(3,3)
    points = [p1, p2, p3, p4]
    chained_points_lists = p1.get_chained_points_lists_from_connected_points()
    assert len(chained_points_lists) == 0, "No connections should mean no chains"

    p1.connect_point(p2)
    p2.connect_point(p3)
    p4.connect_point(p3)
    chained_points_lists = p2.get_chained_points_lists_from_connected_points()
    assert len(chained_points_lists) ==1 
    chained_points = chained_points_lists[0]
    assert set(chained_points) == set(points) , "Not all points were traced"
    points_reversed = points.copy()
    points_reversed.reverse()

    assert chained_points == points or chained_points == points_reversed, "Point order was traced wrong"




def test_construct_chain_from_single_point():
    p1 = Point(0,0)
    p2 = Point(1,1)
    p3 = Point(2,2)
    points = [p1, p2, p3]
    p1.retrace_state_from_connections()
    assert len(p1.chains) == 0, "No connections should mean no chains"

    p1.connect_point(p2)
    p2.connect_point(p3)
    p2.retrace_state_from_connections()
    assert len(p1.chains) ==1 
    chain = list(p1.chains)[0]
    assert type(chain) == Chain
    assert set(chain.points) == set(points) , "Not all points were traced"
    points_reversed = points.copy()
    points_reversed.reverse()

    assert chain.points == points or chain.points == points_reversed, "Point order was traced wrong"



def test_multiple_chains_test():
    raise NotImplementedError()

def test_reconstruct_a_blob():
    raise NotImplementedError()

def test_reconstruct_multiple_blobs():
    raise NotImplementedError()

