import pytest
import pygame
from pygame.math import Vector2
from point import Point
from chain import Chain

def test_chain_initialization():
    c = Chain()
    assert c.points == []
    assert c.color == pygame.Color("white")

def test_point_start_and_end():
    p1 = Point(0, 0)
    p2 = Point(1, 1)
    c = Chain.from_point_list([p1, p2])
    assert c.point_start == p1
    assert c.point_end == p2
    assert c.color == pygame.Color("white")
    c.assert_is_valid()

def test_points_number():
    p1 =Point(0, 0)
    p2 = Point(1, 1)
    c = Chain.from_point_list([p1, p2])
    assert c.point_number == 2

def test_from_point_list():
    p1 = Point(0, 0)
    p2 = Point(1, 1)
    c = Chain.from_point_list([p1, p2])
    assert c.points == [p1, p2]

def test_from_coord_list():
    coords = [(0, 0), (1, 1)]
    c = Chain.from_coord_list(coords)
    assert c.points[0].co == Vector2(0, 0)
    assert c.points[1].co == Vector2(1, 1)
    c.assert_is_valid()

def test_apply_accumulated_offsets():
    p1 = Point(0, 0)
    p2 = Point(1, 1)
    c = Chain.from_point_list([p1, p2])
    p1.add_offset(1, 1)
    c.apply_accumulated_offsets(ignore_unmoving_status=True)
    assert p1.co == Vector2(1, 1)

def test_enforce_link_length():
    p1 = Point(0, 0)
    p2 = Point(2, 0)
    c = Chain.from_point_list([p1, p2])
    c.enforce_link_length(1, ignore_umoving_status=True)
    c.apply_accumulated_offsets(ignore_unmoving_status=True)
    assert 1 == pytest.approx(p1.co.distance_to(p2.co), rel=0.1)

def test_cut():
    p1 = Point(0, 0)
    p2 = Point(1, 1)
    p3 = Point(2, 2)
    c = Chain.from_point_list([p1, p2, p3])
    chain_start, chain_end = c.cut(1)
    assert chain_start.points == [p1, p2]
    assert chain_end.points == [p2, p3]
    chain_start.assert_is_valid()
    chain_end.assert_is_valid()

def test_add_point():
    p1 = Point(0, 0)
    p2 = Point(1, 1)
    p3 = Point(2, 2)
    c = Chain.from_point_list([p2])
    c.append_endpoint(p3, append_to_start=False)
    c.append_endpoint(p1, append_to_start=True)
    
    assert c.points == [p1, p2, p3]
    assert c.points != [p2]
    c.assert_is_valid()

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