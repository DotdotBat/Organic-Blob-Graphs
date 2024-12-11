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
    