from math import copysign
from typing import Counter, Optional, SupportsFloat

from simulator.modules.box import Box
from simulator.modules.light_barrier import LightBarrier
from simulator.space.collidable_element import CollidableElement, Rectangle, Tag
from simulator.space.element import Vector
from simulator.space.movements import ChildElementTranslation
from simulator.space.moving_element import MovingElement

# conveyor = rectangular object
# "belt": move children <->(x)
# 1x/2x LB

WIDTH: float = 20
HEIGHT: float = 10
SPEED: float = 10


class Counting:
    counter = 0

    def _increment_and_get(self) -> int:
        self.counter += 1
        return self.counter


class Conveyor:
    def __init__(
        self,
        parent: MovingElement,
        name: str,
        position: Vector = Vector(0, 0),
        rotation: float = 0,
        width: float = WIDTH,
        height: float = HEIGHT,
        speed: float = SPEED,
    ) -> None:
        self.parent = parent
        self.name = name
        self.position = position
        self.rotation = rotation
        self.height = height
        self.width = width
        self.speed = speed

        self.belt_movement: Optional[ChildElementTranslation] = None
        self.current_direction: int = 0

        self.root_element = CollidableElement(
            position=self.position,
            rotation=self.rotation,
            name=self.name + "_root",
            parent=self.parent,
            shape=Rectangle(self.width, self.height),
            tags=set(),  # only for outline
        )
        self.belt_sprite_holder = CollidableElement(
            position=Vector(0, 0),
            rotation=0,
            name=self.name + "_belt_sprite",
            parent=self.root_element,
            shape=Rectangle(self.width, self.height / 2),
            tags=set(),  # only for sprite
        )
        self.belt = CollidableElement(
            position=Vector(0, 0),
            rotation=0,
            name=self.name + "_belt",
            parent=self.root_element,
            shape=Rectangle(self.width, self.height / 2),
            tags={Tag.SHAPE_MOVING_POINTS},  # actual belt
        )

    def start_move_forward(self) -> None:
        self._start_move(+1)

    def start_move_backward(self) -> None:
        self._start_move(-1)

    def _start_move(self, direction: SupportsFloat) -> None:
        if self.belt_movement is not None:
            raise ValueError("already moving")
        self.belt_movement = ChildElementTranslation(
            Vector(copysign(self.speed, direction), 0)
        )
        self.belt.start_movement(self.belt_movement)
        self.current_direction = int(copysign(1, direction))

    def stop_move(self) -> None:
        if self.belt_movement is not None:
            self.belt.end_movement(self.belt_movement)
            self.belt_movement = None
            self.current_direction = 0


class BoxSpawningConveyor(Conveyor, Counting):
    def __init__(
        self,
        parent: MovingElement,
        name: str,
        position: Vector = Vector(0, 0),
        rotation: float = 0,
        width: float = HEIGHT,
        height: float = HEIGHT,
        speed: float = SPEED,
    ) -> None:
        super().__init__(
            parent,
            name,
            position=position,
            rotation=rotation,
            width=width,
            height=height,
            speed=speed,
        )

    def spawn_box(self, offset: float = 0) -> Box:
        return Box(
            self.name + "_box_" + str(self._increment_and_get()),
            self.belt,  # already attached
            Vector(self.width * offset, 0),
        )


class Conveyor1xLb(BoxSpawningConveyor):
    def __init__(
        self,
        parent: MovingElement,
        name: str,
        position: Vector = Vector(0, 0),
        rotation: float = 0,
        width: float = HEIGHT,
        height: float = HEIGHT,
        speed: float = SPEED,
    ) -> None:
        super().__init__(
            parent,
            name,
            position=position,
            rotation=rotation,
            width=width,
            height=height,
            speed=speed,
        )

        self.light_barrier = LightBarrier(
            self.belt_sprite_holder,
            self.name + "_light_barrier",
            length=self.height,
            position=Vector(0, 0),
        )

    def is_light_barrier_active_sensor(self) -> bool:
        return self.light_barrier.is_colliding()


class Conveyor2xLb(BoxSpawningConveyor):
    def __init__(
        self,
        parent: MovingElement,
        name: str,
        position: Vector = Vector(0, 0),
        rotation: float = 0,
        width: float = WIDTH,
        height: float = HEIGHT,
        speed: float = SPEED,
    ) -> None:
        super().__init__(
            parent,
            name,
            position=position,
            rotation=rotation,
            width=width,
            height=height,
            speed=speed,
        )

        pos_factor = 0.4  # > 0.375
        self.light_barrier_1 = LightBarrier(
            self.belt_sprite_holder,
            self.name + "_light_barrier_1",
            length=self.height,
            position=Vector(-self.width * pos_factor, 0),
        )
        self.light_barrier_2 = LightBarrier(
            self.belt_sprite_holder,
            self.name + "_light_barrier_2",
            length=self.height,
            position=Vector(+self.width * pos_factor, 0),
        )

    def is_light_barrier_active_sensor_1(self) -> bool:
        return self.light_barrier_1.is_colliding()

    def is_light_barrier_active_sensor_2(self) -> bool:
        return self.light_barrier_2.is_colliding()
