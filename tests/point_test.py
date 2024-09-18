from pygame.math import Vector2
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
    NotImplementedError()


