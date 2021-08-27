from typing import Any, Generic, List, NamedTuple, Optional, Set, Tuple, TypeVar

import numpy as np
import numpy.typing as npt

T = TypeVar("T", bound="Element[Any]")

ARRAY = npt.NDArray[Any]


class Vector(NamedTuple):
    x: float
    y: float


def xy2arr(xy: Vector) -> ARRAY:
    return np.array(xy, dtype=float)


def get_rotated_position(position: ARRAY, angle_deg: float) -> ARRAY:
    x = position[0]
    y = position[1]
    angle_rad = np.deg2rad(angle_deg)
    # coord-sys rotation counter-clock-wise:
    x_new = x * np.cos(angle_rad) + y * np.sin(angle_rad)
    y_new = -1 * x * np.sin(angle_rad) + y * np.cos(angle_rad)
    return xy2arr(Vector(x_new, y_new))


def get_rot_0_359(value: float) -> float:
    return ((value % 360) + 360) % 360


class Element(Generic[T]):  # T = Type of the parent / children
    # base class of an entity existing in 2D space
    def __init__(
        self,
        position: Vector = Vector(0, 0),
        rotation: float = 0,
        name: str = "element_name",
        parent: Optional[T] = None,
    ) -> None:
        super().__init__()

        # coordinates:
        self._position = xy2arr(position)  # x,y relative to parent
        self._rotation = rotation
        # (deg clockwise, relative to parent, always positive)

        self.name = name

        # hierarchy:
        self._parent = parent
        if parent is not None:
            parent._children.add(self)  # not 'attach', position is already relative
            parent.invalidate_children_bf_cache()
        self._children: Set[T] = set()
        # global coordinates cache:
        self._global_position_cache: Optional[ARRAY] = None
        self._global_rotation_cache: Optional[float] = None
        self._children_breadth_first_cache: Optional[List[T]] = None

    @property
    def position(self) -> ARRAY:
        return self._position

    @position.setter
    def position(self, value: ARRAY) -> None:
        self.invalidate_global_coord_cache()
        self._position = value

    @property
    def rotation(self) -> float:
        return self._rotation

    @rotation.setter
    def rotation(self, value: float) -> None:
        self.invalidate_global_coord_cache()
        self._rotation = get_rot_0_359(value)

    def invalidate_global_coord_cache(self) -> None:
        self._global_position_cache = None
        self._global_rotation_cache = None
        for child in self._children:
            child.invalidate_global_coord_cache()

    # global coordinates:
    def get_global_coordinates(self) -> Tuple[ARRAY, float]:
        # relative to top-level parent
        if not (
            self._global_position_cache is None or self._global_rotation_cache is None
        ):
            return self._global_position_cache.copy(), self._global_rotation_cache
        if self._parent is None:
            return self.position, self.rotation
        parent_gl_pos, parent_gl_rot = self._parent.get_global_coordinates()
        gl_pos_rel = get_rotated_position(self.position, parent_gl_rot)
        gl_pos: ARRAY = parent_gl_pos + gl_pos_rel
        gl_rot = get_rot_0_359(parent_gl_rot + self.rotation)
        # cache:
        self._global_position_cache = gl_pos
        self._global_rotation_cache = gl_rot
        return (gl_pos.copy(), gl_rot)

    # attach / detach:
    def get_children(self: T) -> Set[T]:
        return self._children

    def attach(self, child: T) -> None:
        if child._parent is not None:
            child._parent.detach(child)
        self.update_local_child_position(child)
        child._parent = self
        self._children.add(child)
        self.invalidate_children_bf_cache()

    def update_local_child_position(self, child: T) -> None:
        child_gl_pos, child_gl_rot = child.get_global_coordinates()
        new_parent_gl_pos, new_parent_gl_rot = self.get_global_coordinates()
        child_rel_pos = get_rotated_position(
            child_gl_pos - new_parent_gl_pos, -new_parent_gl_rot
        )
        child.position = child_rel_pos
        child.rotation = child_gl_rot - new_parent_gl_rot

    def detach(self, child: T) -> None:
        child_gl_pos, child_gl_rot = child.get_global_coordinates()
        if child in self._children:
            self._children.remove(child)
        child._parent = None
        child.position = child_gl_pos
        child.rotation = child_gl_rot
        self.invalidate_children_bf_cache()

    def invalidate_children_bf_cache(self) -> None:
        self._children_breadth_first_cache = None
        if self._parent is not None:
            self._parent.invalidate_children_bf_cache()

    # all (grand-) children:
    def get_all_children_breadth_first(self) -> List[T]:
        if self._children_breadth_first_cache is not None:
            return self._children_breadth_first_cache.copy()
        # possible speedup: cached "distance_to_origin"/"_level_cache" int for simple sorting ?
        result = []
        to_be_visited = list(self._children)
        while len(to_be_visited) > 0:
            visited = to_be_visited.pop(0)
            to_be_visited.extend(visited._children)
            result.append(visited)
        self._children_breadth_first_cache = result
        return result
