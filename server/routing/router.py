# top of the control hierarchy, providing info of where to move boxes to reach specified target modules

import networkx as nx
from server.module_agent.dir import Dir
from instances.instance_1.instance_1 import X as grid_x
from instances.instance_1.instance_1 import Y as grid_y
from instances.instance_1.instance_1 import excluded

# generate map info from grid dimensions
# 0/0 is bottom left
X = grid_x
Y = grid_y
directions = {
    Dir.LEFT: (-1, 0),
    Dir.TOP: (0, 1),
    Dir.RIGHT: (1, 0),
    Dir.BOTTOM: (0, -1),
}


def get_map():
    mapp = {}
    for x in range(1, X + 1):
        for y in range(1, Y + 1):
            if excluded(x, y):
                continue
            neighbours = {}
            for dir, coords in directions.items():
                x_ = x + coords[0]  # possible neighbours
                y_ = y + coords[1]
                if excluded(x_, y_):
                    continue
                if 0 < x_ <= X and 0 < y_ <= Y:  # (valid neighbour)
                    neighbours[name(x_, y_)] = {"dir": dir}
            mapp[name(x, y)] = neighbours
    return mapp


def name(x, y):
    return "t_" + str(x) + "_" + str(y)


class Router:
    def __init__(self) -> None:
        self.mapp = get_map()
        self.graph = nx.from_dict_of_dicts(self.mapp)

    def get_next_direction(self, frm: str, to: str) -> Dir:
        if frm == to:
            raise ValueError(frm + " (frm) == (to) " + to)
        shortest_path = nx.shortest_path(self.graph, frm, to)
        return self.mapp[frm][shortest_path[1]]["dir"], shortest_path[1]


if __name__ == "__main__":
    router = Router()
    print(router.graph)
    print(nx.shortest_path(router.graph, "t_1_1", "t_8_5"))
    print(router.get_next_direction("t_1_1", "t_2_2"))
    print(router.get_next_direction("t_1_1", "t_8_5"))
