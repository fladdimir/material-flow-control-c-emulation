from typing import Any, Sequence

from simulator.space.attachment_checker import update_element_attachments
from simulator.space.collision_state_checker import update_collision_states
from simulator.space.element import Element
from simulator.space.moving_element import MovingElement


class World:
    # manages all elements + movements

    def __init__(self) -> None:
        self.origin = MovingElement(name="origin")

    def step(self, time: float) -> None:
        self.origin.step(time)  # execute all movements
        update_element_attachments(self.origin.get_all_children_breadth_first())
        update_collision_states(self.origin.get_all_children_breadth_first())

    def get_elements_breadth_first(self) -> Sequence[Element[Any]]:
        return self.origin.get_all_children_breadth_first()
