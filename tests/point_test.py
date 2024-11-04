from pygame.math import Vector2
import pytest
from point import Point

def test_initialization():
    p = Point(3, 4)
    assert p.co == Vector2(3, 4)
    assert p.offset == Vector2(0, 0)

def test_add_offset():
    p = Point(3, 4)
    p.add_offset(1, 2)
    assert p.offset == Vector2(1, 2)

def test_add_offset_with_multiplier():
    p = Point(3, 4)
    p.add_offset(1, 2, multiplier=2)
    assert p.offset == Vector2(2, 4)

def test_apply_accumulated_offset():
    p = Point(3, 4)
    p.add_offset(1, 2)
    p.apply_accumulated_offset()
    assert p.co == Vector2(4, 6)
    assert p.offset == Vector2(0, 0)

def test_str_repr():
    p = Point(3, 4)
    assert str(p) == 'Point at [3, 4]'

def test_from_point_and_offset():
    p1 = Point(3, 4)
    offset = Vector2(1, 1)
    p2 = Point.from_point_and_offset(p1, offset)
    assert p2.co == Vector2(4, 5)
    assert p2.offset == Vector2(0, 0)

def test_clamp_offset():
    p = Point(3, 4)
    p.add_offset(5, 4)
    clamp_value = 3
    p.clamp_offset(clamp_value)
    assert p.offset.length() == pytest.approx(clamp_value)
    p.apply_accumulated_offset()
    p.add_offset(1, 1)
    p.clamp_offset(clamp_value)
    assert p.offset == Vector2(1, 1)

def test_in_list():
    p1 = Point(0, 0)
    p2 = Point(1, 2)
    p3 = Point(0, 0)

    l = [p1]
    assert p1 in l
    assert p2 not in l
    assert p3 not in l

def test_comparisons():
    p1 = Point(0, 0)
    p2 = Point(1, 2)
    p3 = Point(0, 0)

    assert p1 != p2
    assert p1 != p3
    assert p1 == p1



def test_mutually_repel_no_correction_needed():
    p1 = Point(0, 0)
    p2 = Point(5, 0)
    p1.mutually_repel(p2, target_distance=3)
    assert p1.offset == Vector2(0, 0)
    assert p2.offset == Vector2(0, 0)

    # Test very close points
    p1 = Point(0, 0)
    p2 = Point(0.001, 0.001)
    p1.mutually_repel(p2, target_distance=3)
    assert p1.offset == Vector2(0, 0)
    assert p2.offset == Vector2(0, 0)

def test_mutually_repel_both_move():
    p1 = Point(0, 0)
    p2 = Point(1, 0)
    p1.is_unmoving_override = False
    p2.is_unmoving_override = False
    p1.mutually_repel(p2, target_distance=4)
    assert p1.offset == Vector2(-1.5, 0)
    assert p2.offset == Vector2(1.5, 0)

def test_mutually_repel_one_moves():
    p1 = Point(0, 0)
    p2 = Point(1, 0)
    p1.is_unmoving_override = True
    p2.is_unmoving_override = False
    p1.mutually_repel(p2, target_distance=4)
    assert p1.offset == Vector2(0, 0)
    assert p2.offset == Vector2(3, 0)

    p1.offset = Vector2(0, 0)  # Reset offsets
    p2.offset = Vector2(0, 0)
    p1.is_unmoving_override = False
    p2.is_unmoving_override = True
    p1.mutually_repel(p2, target_distance=4)
    assert p1.offset == Vector2(-3, 0)
    assert p2.offset == Vector2(0, 0)

def test_mutually_repel_ignore_unmoving():
    p1 = Point(0, 0)
    p2 = Point(1, 0)
    p1.is_unmoving_override = True
    p2.is_unmoving_override = True
    p1.mutually_repel(p2, target_distance=4, ignore_unmoving=True)
    assert p1.offset == Vector2(-1.5, 0)
    assert p2.offset == Vector2(1.5, 0)

from chain import Chain
def test_is_endpoint_on_all_chains():
    # Create points
    p1 = Point(0, 0)
    p2 = Point(1, 1)
    p3 = Point(2, 2)
    p4 = Point(3, 3)

    # Create chains
    chain1 = Chain.from_point_list([p1, p2, p3])
    chain2 = Chain.from_point_list([p1, p4])
    chain3 = Chain.from_point_list([p1, p3, p4])


    assert p1.is_endpoint_on_all_chains is True
    assert p2.is_endpoint_on_all_chains is False
    assert p3.is_endpoint_on_all_chains is False
    assert p1.is_endpoint_on_ONLY_SOME_chains is False
    assert p2.is_endpoint_on_ONLY_SOME_chains is False
    assert p3.is_endpoint_on_ONLY_SOME_chains is True

def test_get_adjacent_points_multiple_chains():
    # Create points
    p1 = Point(0, 0)
    p2 = Point(1, 1)
    p3 = Point(2, 2)
    p4 = Point(3, 3)
    p5 = Point(4, 4)

    # Create chains
    chain1 = Chain.from_point_list([p1, p2, p3])
    chain2 = Chain.from_point_list([p1, p4])
    chain3 = Chain.from_point_list([p1, p5])


    # Test adjacent points
    assert set(p1.get_adjacent_points()) == {p2, p4, p5}
    assert p2.get_adjacent_points() == [p1, p3]
    assert p3.get_adjacent_points() == [p2]

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

def test_closest_of_points_basic_case():
    p1 = Point(0, 0)
    p2 = Point(1, 1)
    p3 = Point(2, 2)
    p4 = Point(3, 3)

    points = [p2, p3, p4]
    assert p1.closest_of_points(points) == p2

def test_closest_of_points_multiple_closest():
    p1 = Point(0, 0)
    p2 = Point(1, 1)
    p3 = Point(1, 1)  # Same distance as p2 from p1
    p4 = Point(3, 3)

    points = [p2, p3, p4]
    closest = p1.closest_of_points(points)
    assert closest == p2 or closest == p3

def test_closest_of_points_single_point():
    p1 = Point(0, 0)
    p2 = Point(1, 1)

    points = [p2]
    assert p1.closest_of_points(points) == p2

def test_closest_of_points_empty_list():
    p1 = Point(0, 0)
    points = []

    with pytest.raises(ValueError):  # Assuming it raises an error for empty list
        p1.closest_of_points(points)

def test_closest_of_points_large_number_of_points():
    p1 = Point(0, 0)
    points = [Point(i, i) for i in range(1,1000)]
    points[500] = Point(0, 1)  # Closest point

    assert p1.closest_of_points(points) == points[500]

def test_closest_of_points_with_negative_coordinates():
    p1 = Point(0, 0)
    p2 = Point(-1, -1)
    p3 = Point(-2, -2)

    points = [p2, p3]
    assert p1.closest_of_points(points) == p2