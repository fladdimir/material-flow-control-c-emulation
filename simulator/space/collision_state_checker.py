# similar level to attachment_checker, but for Tags 1/2
# gets passed tree and updates CollisionDetecting elements states

from typing import Any, Iterable

from simulator.space.collidable_element import CollidableElement, TagCombination
from simulator.space.collision_checker import check_collisions
from simulator.space.element import Element


def update_collision_states(elements: Iterable[Element[Any]]) -> None:
    for elem in elements:
        if isinstance(elem, CollidableElement):
            elem.is_colliding = False

    for t1, t2 in check_collisions(
        elements,
        tag_combination=TagCombination.SEGMENT_AND_SHAPE,
    ):
        for t in t1, t2:
            t.is_colliding = True
