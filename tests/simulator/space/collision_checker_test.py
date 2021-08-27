import pytest
from simulator.space.collidable_element import CollidableElement, Rectangle, Segment
from simulator.space.collision_checker import (
    check_collision_point_shape,
    check_collision_segment_shape,
)


@pytest.mark.parametrize(
    (
        "seg_gl_pos, seg_gl_rot, seg_length, rect_gl_pos, rect_gl_rot, rect_width, rect_height, expected_result"
    ),
    [
        ((9, 9), 0, 2, (1, 1), 0, 3, 2, False),
        ((-1, -1), 0, 2, (2, 2), 0, 1, 2, False),
        ((0, 0), 0, 1, (0, 0), 0, 2, 2, True),  # fully inside
        ((1.1, 0), 0, 1, (0, 0), 0, 2, 3, False),  # inside circle but slightly right
        ((1.1, 0), 0, 1, (0, 0), 90, 2, 3, True),  # rotated, now colliding
        ((1.1, 0), 180, 1, (0, 0), 270, 2, 3, True),
        ((1.1, 0), 180, 1, (0, 0), 180, 2, 3, False),
        ((1, -2.6), 180, 1, (2, -2), 90, 1, 2, True),
        ((1, -2.6), 135, 10, (2, -2), 90, 1, 2, False),
        ((1, -2.6), 315, 10, (2, -2), 90, 1, 2, False),
        ((1, -2.6), 180, 1, (2, -2), 0, 2, 1, True),
        ((0, 0.5), 0, 1, (1, 1), 0, 2, 1, True),
        ((1, 1.1), 90, 2, (0, 0), 0, 2, 2, False),
        ((1, 1.1), 45, 2, (0, 0), 0, 2, 2, True),
        ((1, 1.1), 135, 2, (0, 0), 0, 2, 2, False),
        ((0, 0), 34, 2, (0, 0), 314, 2, 2, True),
    ],
)
def test_segment_shape(
    seg_gl_pos,
    seg_gl_rot,
    seg_length,
    rect_gl_pos,
    rect_gl_rot,
    rect_width,
    rect_height,
    expected_result,
):
    seg = Segment(seg_length)
    seg_elem = CollidableElement(position=seg_gl_pos, rotation=seg_gl_rot, shape=seg)
    rect = Rectangle(rect_width, rect_height)
    rect_elem = CollidableElement(
        position=rect_gl_pos, rotation=rect_gl_rot, shape=rect
    )
    assert check_collision_segment_shape(seg_elem, rect_elem) == expected_result


@pytest.mark.parametrize(
    (
        "point_gl_pos, rect_gl_pos, rect_gl_rot, rect_width, rect_height, expected_result,"
    ),
    [
        ((0, 0), (0, 0), 0, 1, 1, True),  # center
        ((9, 9), (0, 0), 0, 1, 1, False),  # outside
        ((0, 0), (0, 0), 91, 1, 1, True),  # center
        ((9, 9), (0, 0), 91, 1, 1, False),  # outside
        ((1, 1), (0, 0), 0, 2, 2, True),  # corner
        ((1.1, 1), (0, 0), 0, 2, 2, False),  # corner outside
        ((0, 1.1), (0, 0), 0, 2, 2, False),  # central above outside
        ((0, 1.1), (0, 0), 45, 2, 2, True),  # central above inside
        ((1, 2.1), (1, 1), 45, 2, 2, True),  # central above inside
    ],
)
def test_point_shape(
    point_gl_pos,
    rect_gl_pos,
    rect_gl_rot,
    rect_width,
    rect_height,
    expected_result,
):
    point_elem = CollidableElement(
        position=point_gl_pos,
    )
    rect = Rectangle(rect_width, rect_height)
    rect_elem = CollidableElement(
        position=rect_gl_pos, rotation=rect_gl_rot, shape=rect
    )
    assert check_collision_point_shape(point_elem, rect_elem) == expected_result
