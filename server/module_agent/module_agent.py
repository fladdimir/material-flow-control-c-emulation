# server-side module-control
# implements logic to communicate with physical modules
# and cooperation with neighbour agents to forward/receive boxes

import asyncio, random
from enum import Enum
from multiprocessing.connection import Connection
from typing import Dict, List, Optional

from server.module_agent.dir import Dir
from server.routing.router import Router


class Box:
    def __init__(self, name: str, targets: List[str]) -> None:
        self.name = name
        self.targets = targets
        self.current_target = None
        self.generator = self.create_generator()

    def update_location(self, location: str):
        if self.current_target == location:
            self.current_target = self.get_next_target()

    def get_next_target(self) -> str:
        ts = self.targets.copy()
        ts.remove(self.current_target)
        return random.choice(ts)
        # alternative to random choice: return next(self.generator)

    def create_generator(self):  # repeat targets sequence
        while True:
            i = 0
            while i < len(self.targets):
                yield self.targets[i]
                i += 1


class Skill(Enum):
    RECEIVE_FROM = 1
    FORWARD_TO = 2


COMMAND_MAP: Dict[Skill, Dict[Dir, int]] = {
    Skill.RECEIVE_FROM: {Dir.LEFT: 0, Dir.TOP: 1, Dir.RIGHT: 2, Dir.BOTTOM: 3},
    Skill.FORWARD_TO: {Dir.LEFT: 4, Dir.TOP: 5, Dir.RIGHT: 6, Dir.BOTTOM: 7},
}


class ModuleAgent:
    def __init__(
        self,
        name: str,
        module_connection: Connection,
        router: Router,
        agents: Dict[str, "ModuleAgent"],
    ) -> None:

        self.name = name
        self.module_connection = module_connection
        self.router = router

        self.agents = agents
        self.agents[self.name] = self

        self.handled_box: Optional[Box] = None

    async def forward_box_async(self):
        target = self.handled_box.current_target
        next_dir, next_agent_name = self.router.get_next_direction(self.name, target)
        await self.forward_to_async(next_dir, self.agents[next_agent_name])

    async def forward_to_async(self, direction: Dir, neighbour: "ModuleAgent"):
        command = COMMAND_MAP[Skill.FORWARD_TO][direction]
        self.module_connection.send(command)  # start prepare forward to
        neighbour.handled_box = self.handled_box
        await neighbour.prepare_receive_from_async(
            # opposite direction (tbd: depend on module orientation)
            Dir(((direction.value + 1) % len(Dir)) + 1)
        )
        self.module_connection.send(20)  # start translation
        await neighbour.receive_from_async()  # wait for confirmation of receipt
        self.module_connection.send(20)  # confirm translation, stop belt
        self.busy = False
        self.handled_box = None
        print(self.name + " forwarding done.")

    async def prepare_receive_from_async(self, direction: Dir) -> None:
        self.busy = True
        command = COMMAND_MAP[Skill.RECEIVE_FROM][direction]
        self.module_connection.send(command)
        await self.wait_for_confirmation_async()  # 1: confirmation of readiness

    async def receive_from_async(self) -> None:
        await self.wait_for_confirmation_async()  # 2: confirmation of retrieval
        print(self.name + " box received")
        self.handled_box.update_location(self.name)
        asyncio.create_task(
            self.forward_box_async(),
        )

    async def wait_for_confirmation_async(self) -> None:
        await self.wait_for_confirmation()

    async def wait_for_confirmation(self) -> None:
        while not self.module_connection.poll(timeout=0):
            await asyncio.sleep(0.025)  # blocking wait for confirmation
        result = self.module_connection.recv()
        # print(self.name + " read confirmation: " + str(result))
