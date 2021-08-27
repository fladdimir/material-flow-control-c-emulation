# contains different types of useful simple movements which can be applied to elements
# -> position/rotation changes over time

import math
from typing import Any

import numpy as np
from simulator.space.element import Element, Vector


class ElementMovement:
    done = False

    def step(self, element: Element[Any], time: float) -> None:
        raise NotImplementedError()


class LimitedMovement:
    def __init__(self) -> None:
        self.done = False


class Rotation(ElementMovement):
    def __init__(self, deg_s: float = 0) -> None:
        super().__init__()
        self.deg_s = deg_s  # deg / s (clockwise)

    def step(self, element: Element[Any], time: float) -> None:
        element.rotation += self.deg_s * time


class LimitedAngleRotation(Rotation):
    def __init__(
        self,
        deg_s: float,
        limit: float,
    ) -> None:
        super().__init__(deg_s=deg_s)
        self.remaining = limit

    def step(self, element: Element[Any], time: float) -> None:
        # tbd: this must not be applied to different elements
        # -> use only from 1 moving_element
        if self.done:
            return
        raw_change = self.deg_s * time
        limited_abs_change = min(np.abs(raw_change), self.remaining)
        self.remaining -= limited_abs_change
        element.rotation += limited_abs_change * math.copysign(1, self.deg_s)
        if self.remaining <= 0:
            self.done = True


class Translation(ElementMovement):  # relative to parent
    def __init__(self, m_s: Vector = Vector(0, 0)) -> None:
        self.m_s = np.array(m_s)  # units / s for each dimension

    def step(self, element: Element[Any], time: float) -> None:
        element.position += self.m_s * time


class ChildElementTranslation(Translation):
    # apply translation to all children
    def step(self, element: Element[Element[Any]], time: float) -> None:
        for child in element._children:
            super().step(child, time)
