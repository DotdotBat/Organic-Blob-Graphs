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



