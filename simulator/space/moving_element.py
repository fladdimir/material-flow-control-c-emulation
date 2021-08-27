from typing import Optional, Set

from simulator.space.element import Element, Vector
from simulator.space.movements import ElementMovement


class MovingElement(Element["MovingElement"]):
    # element subclass which supports moving in space

    def __init__(
        self,
        position: Vector = Vector(0, 0),
        rotation: float = 0,
        name: str = "element_name",
        parent: Optional["MovingElement"] = None,
    ) -> None:
        super().__init__(position=position, rotation=rotation, name=name, parent=parent)
        self._movements: Set[ElementMovement] = set()

    def start_movement(self, movement: ElementMovement) -> None:
        self._movements.add(movement)

    def end_movement(self, movement: ElementMovement) -> None:
        self._movements.remove(movement)

    def step(self, time: float) -> None:
        for move in self._movements:
            move.step(self, time)

        for child in self._children:
            # children are all of this class, thanks to generics (type parameter):
            child.step(time)
            child.get_all_children_breadth_first()
