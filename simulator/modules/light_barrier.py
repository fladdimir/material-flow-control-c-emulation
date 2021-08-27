from simulator.space.element import Vector
from typing import Tuple

from simulator.space.collidable_element import CollidableElement, Segment, Tag
from simulator.space.moving_element import MovingElement

LENGTH = 10


class LightBarrier:
    def __init__(
        self,
        parent: MovingElement,
        name: str,
        length: float = LENGTH,
        position: Vector = Vector(0, 0),
        rotation: float = 0,
    ) -> None:
        self.parent = parent
        self.name = name
        self.position = position
        self.rotation = rotation
        self.length = length

        self.barrier = CollidableElement(
            position=self.position,
            name=self.name + "_barrier",
            parent=self.parent,
            shape=Segment(self.length),
            tags={Tag.SEGMENT},
        )

    def is_colliding(self) -> bool:
        return self.barrier.is_colliding
