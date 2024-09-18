from pygame.math import Vector2
from list_util import rotate_list


def test_pygame_vector_length_assighnment():
    v = Vector2(1,0)
    v.scale_to_length(2)
    assert v == Vector2(2,0)
    v.scale_to_length(-1)
    assert v == Vector2(-1,0)


def test_rotate_list_in_place():
    # Test case 1: Rotate by 2
    lst = [1, 2, 3, 4, 5]
    lst = rotate_list(lst, -2)
    assert lst == [4, 5, 1, 2, 3]
    lst = rotate_list(lst, 2)
    assert lst == [1, 2, 3, 4, 5]

    # Test case 2: Rotate by 0 (no change)
    lst = [1, 2, 3, 4, 5]
    lst = rotate_list(lst, 0)
    assert lst == [1, 2, 3, 4, 5]

    # Test case 3: Rotate by length of the list (no change)
    lst = [1, 2, 3, 4, 5]
    lst = rotate_list(lst, -5)
    assert lst == [1, 2, 3, 4, 5]

    # Test case 4: Rotate by more than the length of the list
    lst = [1, 2, 3, 4, 5]
    lst = rotate_list(lst, -7)
    assert lst == [4, 5, 1, 2, 3]

    # Test case 5: Rotate a list with one element
    lst = [1]
    lst = rotate_list(lst, -3)
    assert lst == [1]

    # Test case 6: Rotate an empty list
    lst = []
    lst = rotate_list(lst, -3)
    assert lst == []