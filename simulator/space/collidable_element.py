from enum import Enum
from simulator.space.element import Vector
from typing import Optional, Set, Tuple

from simulator.space.moving_element import MovingElement


class Shape:
    pass


class Segment(Shape):
    def __init__(self, length: float) -> None:
        self.length = length


class Rectangle(Shape):
    def __init__(self, width: float, height: float) -> None:
        self.width = width  # x
        self.height = height  # y


class Tag(Enum):
    # checked pair 1:
    SEGMENT = 1
    SEGMENT_COLLIDABLE = 2

    # checked pair 2:
    MOVABLE_POINT = 3
    SHAPE_MOVING_POINTS = 4


class TagCombination(Enum):
    SEGMENT_AND_SHAPE = (Tag.SEGMENT, Tag.SEGMENT_COLLIDABLE)
    POINT_AND_MOVING_SHAPE = (Tag.MOVABLE_POINT, Tag.SHAPE_MOVING_POINTS)


class CollidableElement(MovingElement):
    def __init__(
        self,
        position: Vector = Vector(0, 0),
        rotation: float = 0,
        name: str = "element_name",
        parent: Optional["MovingElement"] = None,
        shape: Optional[Shape] = None,
        tags: Set[Tag] = set(),
    ) -> None:
        super().__init__(position=position, rotation=rotation, name=name, parent=parent)
        self.shape: Optional[Shape] = shape
        self.tags: Set[Tag] = tags.copy()

        self.is_colliding = False
