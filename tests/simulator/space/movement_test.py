from simulator.space.movements import (
    ChildElementTranslation,
    LimitedAngleRotation,
    Rotation,
)
from simulator.space.moving_element import MovingElement as MovingElement
from simulator.space.world import World
from tests.simulator.space.space_test import assert_equal


def test_simple_world_movement_1_element():
    world = World()
    origin = world.origin
    e2 = MovingElement(parent=origin)
    origin.attach(e2)
    assert world.get_elements_breadth_first() == [e2]
    origin.start_movement(ChildElementTranslation((2, 0)))
    assert_equal(e2.position, (0, 0))
    assert_equal(e2.get_global_coordinates()[0], (0, 0))
    world.step(time=3)
    assert_equal(e2.position, (6, 0))
    assert_equal(e2.get_global_coordinates()[0], (6, 0))


def test_simple_world_movement_2_nested_element():
    world = World()
    e1 = MovingElement()
    e2 = MovingElement()
    e3 = MovingElement()
    world.origin.attach(e1)
    e1.attach(e2)
    e2.attach(e3)
    e1.start_movement(ChildElementTranslation((1, 0)))
    e2.start_movement(ChildElementTranslation((0, -1)))
    assert_equal(e2.get_global_coordinates()[0], (0, 0))
    assert_equal(e3.get_global_coordinates()[0], (0, 0))
    world.step(time=1)
    assert_equal(e2.get_global_coordinates()[0], (1, 0))
    assert_equal(e3.get_global_coordinates()[0], (1, -1))


def test_simple_rotation_1_element_0_0():
    world = World()
    e1 = MovingElement()
    world.origin.attach(e1)
    e2 = MovingElement()
    e1.attach(e2)
    e1.start_movement(ChildElementTranslation((0, 0)))
    e1.start_movement(Rotation(45))
    assert_equal(e2.get_global_coordinates()[0], (0, 0))
    world.step(time=1)
    assert_equal(e2.get_global_coordinates()[0], (0, 0))
    assert e2.get_global_coordinates()[1] == 45
    world.step(time=1)
    assert e2.get_global_coordinates()[1] == 90


def test_simple_rotation_1_element_360():
    world = World()
    e1 = MovingElement(position=(1, 1))
    world.origin.attach(e1)
    e2 = MovingElement(position=(2, 1))
    e1.attach(e2)
    e1.start_movement(Rotation(90))
    assert_equal(e2.get_global_coordinates()[0], (2, 1))

    world.step(time=1)
    assert e2.get_global_coordinates()[1] == 90
    assert_equal(e2.get_global_coordinates()[0], (1, 0))

    world.step(time=1)
    assert e2.get_global_coordinates()[1] == 180
    assert_equal(e2.get_global_coordinates()[0], (0, 1))

    world.step(time=1)
    assert e2.get_global_coordinates()[1] == 270
    assert_equal(e2.get_global_coordinates()[0], (1, 2))

    world.step(time=1)
    assert e2.get_global_coordinates()[1] == 0  # 360
    assert_equal(e2.get_global_coordinates()[0], (2, 1))


def test_simple_rotation_2_nested_elements_360():
    world = World()
    e1 = MovingElement(position=(1, 1), name="e1")
    world.origin.attach(e1)
    e2 = MovingElement(position=(2, 1), name="e2")
    e1.attach(e2)
    e3 = MovingElement(position=(1, 0), parent=e2, name="e3")  # global 3:1
    e1.start_movement(Rotation(90))
    assert_equal(e2.get_global_coordinates()[0], (2, 1))
    assert_equal(e3.get_global_coordinates()[0], (3, 1))

    world.step(time=1)
    assert e2.get_global_coordinates()[1] == 90
    assert_equal(e2.get_global_coordinates()[0], (1, 0))
    assert e3.get_global_coordinates()[1] == 90
    assert_equal(e3.get_global_coordinates()[0], (1, -1))

    world.step(time=1)
    assert e2.get_global_coordinates()[1] == 180
    assert_equal(e2.get_global_coordinates()[0], (0, 1))
    assert e3.get_global_coordinates()[1] == 180
    assert_equal(e3.get_global_coordinates()[0], (-1, 1))

    world.step(time=1)
    assert e2.get_global_coordinates()[1] == 270
    assert_equal(e2.get_global_coordinates()[0], (1, 2))
    assert e3.get_global_coordinates()[1] == 270
    assert_equal(e3.get_global_coordinates()[0], (1, 3))

    world.step(time=1)
    assert e2.get_global_coordinates()[1] == 0  # 360
    assert_equal(e2.get_global_coordinates()[0], (2, 1))
    assert e3.get_global_coordinates()[1] == 0
    assert_equal(e3.get_global_coordinates()[0], (3, 1))


def test_simple_rotation_translation_2_elements_360():
    world = World()
    e1 = MovingElement(position=(1, 1))
    world.origin.attach(e1)
    e2 = MovingElement(position=(1, 0), parent=e1)  # 2:1
    e3 = MovingElement(position=(3, 1))
    e2.attach(e3)
    e1.start_movement(Rotation(90))  # inner child rotates
    # and outer child takes off from inner:
    e2.start_movement(ChildElementTranslation((1, 0)))
    assert_equal(e2.get_global_coordinates()[0], (2, 1))
    assert_equal(e3.get_global_coordinates()[0], (3, 1))

    world.step(time=1)
    assert e2.get_global_coordinates()[1] == 90
    assert_equal(e2.get_global_coordinates()[0], (1, 0))
    assert e3.get_global_coordinates()[1] == 90
    assert_equal(e3.get_global_coordinates()[0], (1, -2))

    world.step(time=1)
    assert e2.get_global_coordinates()[1] == 180
    assert_equal(e2.get_global_coordinates()[0], (0, 1))
    assert e3.get_global_coordinates()[1] == 180
    assert_equal(e3.get_global_coordinates()[0], (-3, 1))

    world.step(time=1)
    assert e2.get_global_coordinates()[1] == 270
    assert_equal(e2.get_global_coordinates()[0], (1, 2))
    assert e3.get_global_coordinates()[1] == 270
    assert_equal(e3.get_global_coordinates()[0], (1, 6))

    world.step(time=1)
    assert e2.get_global_coordinates()[1] == 0  # 360
    assert_equal(e2.get_global_coordinates()[0], (2, 1))
    assert e3.get_global_coordinates()[1] == 0
    assert_equal(e3.get_global_coordinates()[0], (7, 1))


def test_simple_rotation_1_element_91_max():
    world = World()
    e1 = MovingElement(position=(1, 1))
    world.origin.attach(e1)
    e2 = MovingElement(position=(2, 1))
    e1.attach(e2)
    e1.start_movement(LimitedAngleRotation(deg_s=90, limit=91))
    assert_equal(e2.get_global_coordinates()[0], (2, 1))

    world.step(time=1)
    assert e2.get_global_coordinates()[1] == 90
    assert_equal(e2.get_global_coordinates()[0], (1, 0))

    world.step(time=1)
    assert e2.get_global_coordinates()[1] == 91

    world.step(time=1)
    assert e2.get_global_coordinates()[1] == 91


def test_nested_rotation_2_elements_max_180_90():
    world = World()
    e1 = MovingElement(position=(1, 1))
    world.origin.attach(e1)
    e2 = MovingElement(position=(2, 1))
    e1.attach(e2)
    e3 = MovingElement(position=(3, 1))
    e2.attach(e3)
    # inner child rotates, max 180
    e1.start_movement(LimitedAngleRotation(deg_s=90, limit=180))
    # outer child rotates max 90
    e2.start_movement(LimitedAngleRotation(deg_s=90, limit=90))
    assert_equal(e2.get_global_coordinates()[0], (2, 1))
    assert_equal(e3.get_global_coordinates()[0], (3, 1))

    world.step(time=1)
    assert e2.get_global_coordinates()[1] == 180
    assert_equal(e2.get_global_coordinates()[0], (1, 0))
    assert e3.get_global_coordinates()[1] == 180
    assert_equal(e3.get_global_coordinates()[0], (0, 0))

    world.step(time=1)
    assert e2.get_global_coordinates()[1] == 270
    assert_equal(e2.get_global_coordinates()[0], (0, 1))
    assert e3.get_global_coordinates()[1] == 270
    assert_equal(e3.get_global_coordinates()[0], (0, 2))

    world.step(time=1)
    assert e2.get_global_coordinates()[1] == 270
    assert_equal(e2.get_global_coordinates()[0], (0, 1))
    assert e3.get_global_coordinates()[1] == 270
    assert_equal(e3.get_global_coordinates()[0], (0, 2))


def test_rotation_max_90_2():
    world = World()
    e1 = MovingElement()
    world.origin.attach(e1)
    e1.start_movement(LimitedAngleRotation(deg_s=90.1, limit=90.2))

    world.step(time=1)
    assert_equal(e1.get_global_coordinates()[1], 90.1)

    world.step(time=1)
    assert_equal(e1.get_global_coordinates()[1], 90.2)


def test_rotation_max_90_0():
    world = World()
    e1 = MovingElement()
    world.origin.attach(e1)
    e1.start_movement(LimitedAngleRotation(deg_s=-90, limit=90))
    assert e1.get_global_coordinates()[1] == 0

    world.step(time=1)
    assert e1.get_global_coordinates()[1] == 270

    world.step(time=1)
    assert e1.get_global_coordinates()[1] == 270


def test_rotation_max__90():
    world = World()
    e1 = MovingElement(rotation=89)
    world.origin.attach(e1)
    e1.start_movement(LimitedAngleRotation(deg_s=-45, limit=90))

    world.step(time=1)
    assert e1.get_global_coordinates()[1] == 44

    world.step(time=1)
    assert e1.get_global_coordinates()[1] == 359

    world.step(time=1)
    assert e1.get_global_coordinates()[1] == 359
