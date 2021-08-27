# bad draft of an animation frontend for the simulation

import sys

sys.path.append(".")

import asyncio
import threading
from typing import Dict, List

import arcade
import arcade.gui
from arcade.gui import UIManager
from arcade.sprite import Sprite
from instances.instance_1.instance_1 import World1
from root import root_directory
from server.module_agent.module_agent import Box, ModuleAgent
from server.routing.router import Router
from simulator.module_level.module_level import Module2ControlParent
from simulator.modules.turntable import WIDTH as MODULE_WIDTH
from simulator.space.collidable_element import CollidableElement, Rectangle, Segment
from simulator.space.element import Element
from simulator.space.world import World

SCALE = 10 * 1  # px / m
STEP = 1 / 30

step = 0

BUTTON_2_ACTION = None
BUTTON_3_ACTION = None

world = None


class MyButton(arcade.gui.UIFlatButton):
    def on_click(self):
        print("Click button.")
        global step
        step = STEP if step == 0 else 0


class MyButton2(arcade.gui.UIFlatButton):
    def on_click(self):
        print("Click button 2.")
        if BUTTON_2_ACTION is not None:
            BUTTON_2_ACTION()


class MyButton3(arcade.gui.UIFlatButton):
    def on_click(self):
        print("Click button 3.")
        if BUTTON_3_ACTION is not None:
            BUTTON_3_ACTION()


def get_target_coords_from_name(name: str):
    s = name.split("_")
    x = int(s[1])
    y = int(s[2])
    return map(lambda c: (c * MODULE_WIDTH) * SCALE, (x, y))


class WorldDrawer:
    def __init__(self, world: World) -> None:
        self.world = world

    def draw_world(self):  # tbd: abstract canvas param
        for element in self.world.get_elements_breadth_first():
            position, rotation = element.get_global_coordinates()
            position *= SCALE
            color = arcade.color.YELLOW
            width = 5
            height = 7.5
            if isinstance(element, CollidableElement):
                color = (  # tbd: only lb (element-specific drawer...)
                    arcade.color.RED if element.is_colliding else arcade.color.AERO_BLUE
                )
            if isinstance(element, CollidableElement):
                shape = element.shape
                if isinstance(shape, Segment):
                    width = 0.05
                    height = shape.length
                elif isinstance(shape, Rectangle):
                    width = shape.width
                    height = shape.height
            width *= SCALE
            height *= SCALE
            if element not in sprites:
                draw_box_filled = True
                if draw_box_filled and "box" in element.name:
                    arcade.draw_rectangle_filled(
                        position[0],
                        position[1],
                        width,
                        height,
                        arcade.color.WOOD_BROWN,  # color,
                        rotation,  # counter-clockwise rotation
                    )
                else:
                    arcade.draw_rectangle_outline(
                        position[0],
                        position[1],
                        width,
                        height,
                        color,
                        1,  # border width
                        -rotation,  # counter-clockwise rotation
                    )
                if False:
                    arcade.draw_text(
                        element.name, position[0], position[1], arcade.color.BLACK
                    )
            else:
                sprite = sprites[element]
                sprite.center_x = position[0]
                sprite.center_y = position[1]
                sprite.angle = -rotation
                sprite.width = width
                sprite.height = height
                sprite.draw()


class MyView(arcade.View):
    def __init__(self, world_drawer: WorldDrawer):
        super().__init__()
        self.ui_manager = UIManager()
        self.world_drawer = world_drawer

    def on_show_view(self):
        """Called once when view is activated."""
        self.setup()

    def on_hide_view(self):
        self.ui_manager.unregister_handlers()

    def setup(self):
        self.ui_manager.purge_ui_elements()
        arcade.set_background_color(arcade.color.GRAY)
        button = MyButton(
            "start/stop", center_x=150, center_y=550, width=200, height=20
        )
        button_2 = MyButton2(
            "create_box", center_x=150, center_y=450, width=200, height=20
        )
        button_3 = MyButton3("move", center_x=150, center_y=550, width=200, height=20)
        self.ui_manager.add_ui_element(button)
        # self.ui_manager.add_ui_element(button_2)
        # self.ui_manager.add_ui_element(button_3)

    def on_draw(self):
        """Draw this view. GUI elements are automatically drawn."""
        arcade.start_render()
        if step != 0:
            self.world_drawer.world.step(time=step)
            for c in controller:
                c.loop(int(1000 / 60))
        self.world_drawer.draw_world()
        arcade.draw_text(
            "current_target: " + box.current_target, 50, 400, arcade.color.BLACK
        )
        target_x, target_y = get_target_coords_from_name(box.current_target)
        arcade.draw_text(
            "X",
            target_x + 20,
            target_y,
            arcade.color.BLACK,
            font_size=36,
            align="center",
        )


sprites: Dict[Element, Sprite] = {}


def add_sprite(element: CollidableElement):
    sprite_rel_path = "simulator/frontend/ft_sl.png"
    sprite = Sprite(root_directory + sprite_rel_path)
    sprites[element] = sprite


controller: List[Module2ControlParent] = []
agents: List[ModuleAgent] = []
box: Box


def create_world() -> World:
    global world
    world = World1()
    router = Router()
    agent_dict = {}
    for t in sum(world.modules, []):
        add_sprite(t.belt.belt_sprite_holder)

        control = Module2ControlParent(t)
        controller.append(control)
        agent = ModuleAgent(
            t.name, control.module_parent_connection, router, agent_dict
        )
        agents.append(agent)
    global box  # show current target
    box = Box("box_1", list(router.mapp.keys()))
    box.current_target = "t_1_2"
    agents[0].handled_box = box  # box_1 "info-entity"

    global BUTTON_2_ACTION
    BUTTON_2_ACTION = world.modules[0][0].spawn_box  # physical box_1
    global BUTTON_3_ACTION
    BUTTON_3_ACTION = lambda: asyncio.run_coroutine_threadsafe(
        agents[0].forward_box_async(), event_loop
    )
    return world


event_loop = asyncio.new_event_loop()


def main():
    window = arcade.Window(title="window", width=1200)
    world = create_world()
    view = MyView(WorldDrawer(world))
    window.show_view(view)
    threading.Thread(target=event_loop.run_forever).start()
    BUTTON_2_ACTION()
    BUTTON_3_ACTION()
    arcade.run()


if __name__ == "__main__":
    main()
