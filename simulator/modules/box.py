from simulator.space.element import Vector
from typing import Tuple

from simulator.space.collidable_element import CollidableElement, Rectangle, Tag
from simulator.space.moving_element import MovingElement

LENGTH: float = 5


class Box:
    def __init__(
        self,
        name: str,
        initial_parent: MovingElement,
        initial_position: Vector = Vector(0, 0),
    ) -> None:
        self.name = name

        self.element = CollidableElement(
            position=initial_position,
            rotation=0,
            name=name + "_element",
            parent=initial_parent,
            shape=Rectangle(height=LENGTH, width=LENGTH),
            tags={Tag.MOVABLE_POINT, Tag.SEGMENT_COLLIDABLE},
        )
