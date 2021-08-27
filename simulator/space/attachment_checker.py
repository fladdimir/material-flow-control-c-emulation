from typing import Any, Dict, Iterable, Set

from simulator.space.collidable_element import CollidableElement, Tag, TagCombination
from simulator.space.collision_checker import check_collisions
from simulator.space.element import Element


def update_element_attachments(elements: Iterable[Element[Any]]) -> None:
    # change element attachments according to collisions (Tags 3/4)
    collisions = check_collisions(elements, TagCombination.POINT_AND_MOVING_SHAPE)
    collisions_dict: Dict[CollidableElement, Set[CollidableElement]] = {}
    for movable_point, point_moving_shape in collisions:
        collisions_dict[movable_point] = collisions_dict.get(movable_point, set())
        collisions_dict[movable_point].add(point_moving_shape)
    for child in elements:
        if isinstance(child, CollidableElement) and Tag.MOVABLE_POINT in child.tags:
            colliding_with = collisions_dict.get(child, set())
            # 1. check for tagged children not colliding with parents (and detach)
            if child._parent not in colliding_with and child._parent is not None:
                child._parent.detach(child)
                # 2. check for these children for new collisions (and attach)
                if len(colliding_with) > 0:
                    colliding_with.pop().attach(child)
