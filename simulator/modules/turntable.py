from typing import Optional

from simulator.modules.box import Box
from simulator.modules.conveyor import SPEED, Conveyor1xLb
from simulator.space.collidable_element import CollidableElement, Rectangle
from simulator.space.element import Vector
from simulator.space.movements import LimitedAngleRotation, Rotation
from simulator.space.moving_element import MovingElement

WIDTH: float = 10
ROTATION_SPEED: float = 45
BELT_SPEED: float = SPEED

MAX_ROTATION_ANGLE: float = 90


class TurnTable:
    # basically a conveyor belt module mounted on a socket and a turning element
    def __init__(
        self,
        parent: MovingElement,
        name: str,
        position: Vector = Vector(0, 0),
        rotation: float = 0,
        width: float = WIDTH,
        belt_speed: float = BELT_SPEED,  # m / s
        rot_speed: float = ROTATION_SPEED,  # deg / s
    ) -> None:
        self.name = name
        self._width = width
        self._rot_speed = rot_speed
        self._max_rotation_angle: float = 90
        self._rotation_movement: Optional[Rotation] = None

        # create own elements
        self.root_element = MovingElement(
            position=position,
            rotation=rotation,
            name=self.name + "_root",
            parent=parent,
        )
        # 1. socket
        self.socket = CollidableElement(
            name=self.name + "_socket",
            parent=self.root_element,
            shape=Rectangle(self._width, self._width),
            tags=set(),  # only for outline
        )
        # 2. table
        self.turning_table = MovingElement(
            position=Vector(0, 0),
            rotation=0,
            name=self.name + "_table",
            parent=self.socket,
        )
        # 3. belt
        self.belt = Conveyor1xLb(
            parent=self.turning_table,
            name=self.name + "_conveyor",
            position=Vector(0, 0),
            rotation=0,
            width=self._width,
            height=self._width,
            speed=belt_speed,
        )

    def start_move_forward(self) -> None:
        self.belt.start_move_forward()

    def start_move_backward(self) -> None:
        self.belt.start_move_backward()

    def stop_move(self) -> None:
        self.belt.stop_move()

    def current_translation_direction(self) -> int:
        return self.belt.current_direction

    def turn_clockwise(self) -> None:
        rot_limit = self._max_rotation_angle - self.turning_table.rotation
        self._start_turn(self._rot_speed, rot_limit)  # max remaining to limit

    def turn_counter_clockwise(self) -> None:
        self._start_turn(-self._rot_speed, self.turning_table.rotation)  # back to 0

    def current_rotation_direction(self) -> int:
        if self._rotation_movement is not None:
            return 1 if self._rotation_movement.deg_s > 0 else -1
        return 0

    def _start_turn(self, rot_speed: float, rot_limit: float) -> None:
        if self._rotation_movement is not None:
            raise ValueError("already rotating")
        self._rotation_movement = LimitedAngleRotation(rot_speed, rot_limit)
        self.turning_table.start_movement(self._rotation_movement)

    def stop_turning(self) -> None:
        if self._rotation_movement is None:
            raise ValueError("not moving")
        self.turning_table.end_movement(self._rotation_movement)
        self._rotation_movement = None

    def is_fully_turned_sensor(self) -> bool:
        return self.turning_table.rotation == self._max_rotation_angle

    def is_not_turned_sensor(self) -> bool:
        return self.turning_table.rotation == 0

    def is_light_barrier_active_sensor(self) -> bool:
        return self.belt.is_light_barrier_active_sensor()

    def spawn_box(self) -> Box:
        return self.belt.spawn_box()
