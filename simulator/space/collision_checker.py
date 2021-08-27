import math
from typing import Any, Callable, Dict, Iterable, Set, Tuple

from simulator.space.cohen_sutherland import cohen_sutherland
from simulator.space.collidable_element import (
    CollidableElement,
    Rectangle,
    Segment,
    Tag,
    TagCombination,
)
from simulator.space.element import (
    ARRAY,
    Element,
    Vector,
    get_rot_0_359,
    get_rotated_position,
)


def _cohen_sutherland(
    rect_width: float,  # center: (0,0)
    rect_height: float,
    segment_center: Vector,
    segment_rot: float,
    segment_length: float,
) -> bool:
    xmin, xmax = -(rect_width / 2), +(rect_width / 2)
    ymin, ymax = -(rect_height / 2), +(rect_height / 2)
    seg_rot_rad = math.radians(segment_rot)
    seg_center_x, seg_center_y = segment_center
    segment_top_rel_x = math.sin(seg_rot_rad) * segment_length / 2
    segment_top_rel_y = math.cos(seg_rot_rad) * segment_length / 2
    x1, y1 = seg_center_x + segment_top_rel_x, seg_center_y + segment_top_rel_y
    x2, y2 = seg_center_x - segment_top_rel_x, seg_center_y - segment_top_rel_y
    return cohen_sutherland(xmin, ymax, xmax, ymin, x1, y1, x2, y2)


def check_collision_segment_shape(
    segment_element: CollidableElement, shape_element: CollidableElement
) -> bool:
    assert isinstance(segment_element.shape, Segment)
    segment: Segment = segment_element.shape
    assert isinstance(shape_element.shape, Rectangle)
    rect: Rectangle = shape_element.shape
    # 0. simple broad check of circles
    rect_radius = math.sqrt(
        (rect.width ** 2) + (rect.height ** 2)
    )  # tbd: move function to shape (+cache?)
    segment_radius = segment.length / 2
    rect_gl_pos, rect_gl_rot = shape_element.get_global_coordinates()
    segment_gl_pos, segment_gl_rot = segment_element.get_global_coordinates()
    segment_rel_pos: ARRAY = segment_gl_pos - rect_gl_pos  # = distance_vector
    center_distance = math.sqrt((segment_rel_pos[0] ** 2) + segment_rel_pos[1] ** 2)
    if center_distance > rect_radius + segment_radius:
        return False
    # 1. relative position
    segment_rel_pos = get_rotated_position(segment_rel_pos, -rect_gl_rot)
    segment_rel_rot = get_rot_0_359(segment_gl_rot - rect_gl_rot)
    # 2. cohen sutherland
    return _cohen_sutherland(
        rect.width,
        rect.height,
        Vector(segment_rel_pos[0], segment_rel_pos[1]),
        segment_rel_rot,
        segment.length,
    )


def check_collision_point_shape(
    point_element: CollidableElement, shape_element: CollidableElement
) -> bool:
    assert isinstance(shape_element.shape, Rectangle)
    rect: Rectangle = shape_element.shape
    # 0. simple broad check
    rect_radius = math.sqrt(
        (rect.width ** 2) + (rect.height ** 2)
    )  # tbd: move function to shape (+cache?)
    rect_gl_pos, rect_gl_rot = shape_element.get_global_coordinates()
    point_gl_pos = point_element.get_global_coordinates()[0]
    point_rel_pos: ARRAY = point_gl_pos - rect_gl_pos
    point_distance = math.sqrt(point_rel_pos[0] ** 2 + point_rel_pos[1] ** 2)
    if point_distance > rect_radius:
        return False
    # 1. relative rotated position
    point_rel_pos = get_rotated_position(point_rel_pos, rect_gl_rot)
    # 3. check dimensions
    return _cohen_sutherland(
        rect.width,
        rect.height,
        Vector(point_rel_pos[0], point_rel_pos[1]),
        0,
        0,  # point = segment of length 0
    )


collision_checks: Dict[
    TagCombination, Callable[[CollidableElement, CollidableElement], bool]
] = {
    TagCombination.SEGMENT_AND_SHAPE: check_collision_segment_shape,
    TagCombination.POINT_AND_MOVING_SHAPE: check_collision_point_shape,
}


def check_collisions(
    elements: Iterable[Element[Any]],
    tag_combination: TagCombination,
) -> Set[Tuple[CollidableElement, CollidableElement]]:
    # check for collisions between tagged CollidableElement's
    # (t1 child of t2 if only_direct_children)
    # returns set of all colliding element pairs
    tag_1: Tag
    tag_2: Tag
    tag_1, tag_2 = tag_combination.value

    tagged_1s: Set[CollidableElement] = set()
    tagged_2s: Set[CollidableElement] = set()
    for elem in elements:
        if isinstance(elem, CollidableElement):
            if tag_1 in elem.tags:
                tagged_1s.add(elem)
            elif tag_2 in elem.tags:
                tagged_2s.add(elem)

    # check for all possible collisions
    collision_check = collision_checks[tag_combination]
    result: Set[Tuple[CollidableElement, CollidableElement]] = set()
    for t1 in tagged_1s:
        for t2 in tagged_2s:
            if collision_check(t1, t2):
                result.add((t1, t2))
    return result
