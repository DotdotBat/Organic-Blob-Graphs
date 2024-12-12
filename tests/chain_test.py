import pygame
from pygame import Vector2
import pytest
from point import Point
from chain import Chain

def test_is_endpoint_of_chain():
    # Create points
    p1 = Point(0, 0)
    p2 = Point(1, 1)
    p3 = Point(2, 2)
    p4 = Point(3, 3)

    # Create chains
    chain1 = Chain.from_point_list([p1, p2, p3])
    chain2 = Chain.from_point_list([p3, p4])

    # Test if points are endpoints of the chain
    assert p1.is_endpoint_of_chain(chain1) is True
    assert p3.is_endpoint_of_chain(chain1) is True
    assert p2.is_endpoint_of_chain(chain1) is False

    assert p3.is_endpoint_of_chain(chain2) is True
    assert p4.is_endpoint_of_chain(chain2) is True
    assert p1.is_endpoint_of_chain(chain2) is False



def test_chain_initialization():
    c = Chain()
    assert c.points == []
    assert c.color == pygame.Color("white")
    with pytest.raises(AssertionError):
        c.assert_is_valid() #an empty chain is not valid


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
    c.assert_is_valid()

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

    assert p2.is_endpoint_of_chain(c) is False
    chain_start, chain_end = c.cut(1)
    assert p2.is_endpoint_of_chain(c) is True
    assert chain_start.points == [p1, p2]
    assert chain_end.points == [p2, p3]
    chain_start.assert_is_valid()
    chain_end.assert_is_valid()
    assert c==chain_start or c==chain_end
    assert c==chain_end or c==chain_start

    
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

def test_add_point_to_connect_two_chains():
    p1 = Point(1, 1)
    p2 = Point(2, 2)
    p3 = Point(3, 3)
    p4 = Point(4, 4)
    c = Chain.from_point_list([p1, p2])
    c1 = Chain.from_point_list([p3, p4])
    
    p2.connect_point(p3)

    chains = Chain.construct_chains_from_point_connections(p2)
    assert len(chains) == 1
    chains = list(chains)
    c = chains[0]
    assert set(c.points) == set([p1, p2, p3, p4])

    #points order
    order_is_preserved = False
    if c.points == [p1, p2, p3, p4]:
        order_is_preserved = True
    #or
    if c.points == [p4, p3, p2, p1]:
        order_is_preserved = True
    assert order_is_preserved
    c.assert_is_valid()

def test_connect_to_midpoint_splits_chain():
    p1 = Point(-1, 0)
    mid_point = Point(0, 0)
    p3 = Point(1, 0)
    p5 = Point(0, 0.5)
    p4 = Point(0, 1)
    original_chain = Chain.from_point_list([p1, mid_point, p3])
    
    p5.connect_point(p4)
    mid_point.connect_point(p5)
    chains_from_midpoint = Chain.construct_chains_from_point_connections(mid_point)
    chains = Chain.construct_chains_from_point_connections(p1)
    assert len(chains_from_midpoint) == 3
    assert len(chains) == 3
    for chain in chains:
        assert mid_point in chain.points
    for chain in chains:
        chain.assert_is_valid()
    a, b, c = chains
    assert a != b
    assert a.points != b.points
    
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
    
def test_insert_midpoint():
    chain_points_number = 5
    for i in range(chain_points_number - 1):
        start = Point(0, 0)
        end = Point(5, 0)
        chain = Chain.from_end_points(start, end, point_num=chain_points_number)
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
        for p in chain.points:
            if p in [start,end]:
                assert len(p.connected_points) == 1
            else:
                assert len(p.connected_points) == 2



def test_dismantle_structure():
    p1 = Point(-1, 0)
    mid_point = Point(0, 0)
    p3 = Point(1, 0)
    p5 = Point(0, 0.5)
    p4 = Point(0, 1)
    original_chain = Chain.from_point_list([p1, mid_point, p3])
    
    p5.connect_point(p4)
    mid_point.connect_point(p5)

    points = [p1,mid_point, p3, p4,p5]
    assert all(len(p.connected_points)>0 for p in points)
    p1.dismantle_structure()
    assert all(len(p.connected_points)==0 for p in points)

from point import connect_point_list

def test_connect_point_list():
    p1 = Point(0, 0)
    p2 = Point(1, 0)
    p3 = Point(0, 1)
    p4 = Point(-1, 0)
    p5 = Point(0, -1)

    points_to_connect = [p1, p2, p3, p4]

    # Ensure no connections initially
    assert len(p5.connected_points) == 0
    assert all(len(p.connected_points) == 0 for p in points_to_connect)

    connect_point_list(points_to_connect)

    endpoints = [p1, p4]
    #are they all sequentially connected?
    for i, point in enumerate(points_to_connect):
        expected_number_of_connections = 0
        if i > 0:
            expected_number_of_connections +=1
            previous_point = points_to_connect[i-1]
            assert point.is_connected_to_point(previous_point)
        last_index = len(points_to_connect) -1
        if i < last_index:
            expected_number_of_connections +=1
            next_point = points_to_connect[i+1]
            assert point.is_connected_to_point(next_point)
        assert len(point.connected_points) == expected_number_of_connections, "point got more connections than expected"

    assert len(p5.connected_points) == 0, "this point has nothing to do with the connections, why is it connected?"


def test_chain_construction_from_point_ring():
    p1 = Point(0, 0)
    p2 = Point(1, 0)
    p3 = Point(1, 1)
    p4 = Point(0, 1)
    connect_point_list([p1, p2, p3, p4, p1])
    assert p1.is_connected_to_point(p4)
    chains = Chain.construct_chains_from_point_connections(p1)
    assert len(chains) == 1
    chain = chains[0]
    assert len(set(chain.points)) == 4
    assert len(chain.points) == 5
    # assert chain.point_number == 4 #You don't really want that. Thats the evil talking within you. 
    assert chain.point_start == chain.point_end
