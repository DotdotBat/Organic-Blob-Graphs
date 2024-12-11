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

def test_closest_of_points_with_self_among_points():
    p1 = Point(0, 0)
    p2 = Point(1, 1)
    p3 = Point(2, 2)

    # Case 1: By default, self should be ignored
    points = [p1, p2, p3]
    assert p1.closest_of_points(points) == p2  # Closest point is p2, not p1 itself

    # Case 2: If dont_ignore_self is True, self should be returned if present
    closest = p1.closest_of_points(points, dont_ignore_self=True)
    assert closest == p1  # Since self is passed and dont_ignore_self=True, p1 should be returned

    # Case 3: If self is not in the list, behavior is unaffected
    points_without_self = [p2, p3]
    assert p1.closest_of_points(points_without_self) == p2  # Closest point is p2
    assert p1.closest_of_points(points_without_self, dont_ignore_self=True) == p2  # Same result



def test_adjacent_points_initially_empty():
    # Create a point
    p1 = Point(0, 0)

    # Check that adjacent points set is initially empty
    assert p1.connected_points == set()


def test_connect_point_adds_to_adjacent_points():
    # Create points
    p1 = Point(0, 0)
    p2 = Point(1, 1)

    # Connect points
    p1.connect_point(p2)

    # Check adjacency
    assert p2 in p1.connected_points
    assert p1 in p2.connected_points  # Bidirectional
    p1.assert_point_is_valid()


def test_disconnect_removes_from_adjacent_points():
    # Create points
    p1 = Point(0, 0)
    p2 = Point(1, 1)

    # Connect and then disconnect points
    p1.connect_point(p2)
    p1.disconnect_point(p2)

    # Check adjacency
    assert p2 not in p1.connected_points
    assert p1 not in p2.connected_points  # Bidirectional
    p1.assert_point_is_valid()



def test_are_connected_returns_correctly():
    # Create points
    p1 = Point(0, 0)
    p2 = Point(1, 1)
    p3 = Point(2, 2)

    # Connect points
    p1.connect_point(p2)

    # Check connectivity
    assert p1.is_connected_to_point(p2) is True
    assert p2.is_connected_to_point(p1) is True  # Bidirectional
    assert p1.is_connected_to_point(p3) is False
    assert p3.is_connected_to_point(p1) is False


def test_connecting_same_point_twice_does_not_duplicate():
    # Create points
    p1 = Point(0, 0)
    p2 = Point(1, 1)

    # Connect the same points multiple times
    p1.connect_point(p2)
    p1.connect_point(p2)

    # Check adjacency
    assert len(p1.connected_points) == 1
    assert len(p2.connected_points) == 1
    assert p2 in p1.connected_points
    assert p1 in p2.connected_points


def test_disconnect_point_not_connected_does_nothing():
    # Create points
    p1 = Point(0, 0)
    p2 = Point(1, 1)

    # Attempt to disconnect points that were not connected
    p1.disconnect_point(p2)

    # Check adjacency
    assert p2 not in p1.connected_points
    assert p1 not in p2.connected_points


def test_self_connection_not_allowed():
    # Create a point
    p1 = Point(0, 0)

    # Attempt to connect the point to itself
    with pytest.raises(ValueError):
        p1.connect_point(p1)

    # Check adjacency
    assert p1 not in p1.connected_points

