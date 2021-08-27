# sample test layout
# control code works in arbitrary layouts, so more versions can be created to provide different test scenarios

from typing import List

from simulator.modules.turntable import WIDTH, TurnTable
from simulator.space.element import Vector
from simulator.space.world import World


X = 6
Y = 3
EXCLUDES_X_Y = {2: [1, 2], 4: [3]}  # remote some elements of the grid


def excluded(x, y):
    return x in EXCLUDES_X_Y and y in EXCLUDES_X_Y[x]


class World1(World):
    def __init__(self) -> None:
        super().__init__()
        self.modules: List[List[TurnTable]] = [
            [
                TurnTable(
                    self.origin,
                    "t_" + str(x) + "_" + str(y),
                    position=Vector(WIDTH * x, WIDTH * y),
                    rotation=0,
                    belt_speed=20,
                    rot_speed=90,
                )
                for y in range(1, Y + 1)
                if not excluded(x, y)
            ]
            for x in range(1, X + 1)
        ]
