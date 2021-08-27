from typing import Any

import pytest
from numpy import testing as npt
from simulator.space.element import Element, xy2arr


def assert_equal(actual: Any, expected: Any) -> None:
    npt.assert_almost_equal(actual, expected)


@pytest.mark.parametrize(
    ("pos_1, rot_1, pos_2, rot_2, pos_3, rot_3, pos_exp, rot_exp"),
    [
        ((0, 0), 0, (0, 0), 0, (0, 0), 0, (0, 0), 0),
        ((0, 1), 0, (0, -1), 0, (1, 0), 0, (1, 0), 0),
        ((0, 0), 180, (0, 0), 180, (0, 0), 0, (0, 0), 0),
        ((0, 0), 180.1, (0, 0), 180, (0, 0), 0, (0, 0), 0.1),
        ((1, 1), 90, (0, 1), 90, (0, 0), 90, (2, 1), 270),
        ((-1, -1), -90, (0, 1), 0, (0, 0), 0, (-2, -1), 270),
        ((2, 2), 45, (1, 1), 180, (1, 1), 0, (2, 2), 225),
    ],
)
def test_global_coords_3_elements(
    pos_1, rot_1, pos_2, rot_2, pos_3, rot_3, pos_exp, rot_exp
):
    origin = Element(name="origin")
    e1 = Element(parent=origin, position=pos_1, rotation=rot_1)
    e2 = Element(parent=e1, position=pos_2, rotation=rot_2)
    e3 = Element(parent=e2, position=pos_3, rotation=rot_3)

    e3_pos_gl, e3_rot_gl = e3.get_global_coordinates()
    assert_equal(e3_pos_gl, xy2arr(pos_exp))
    assert_equal(e3_rot_gl, rot_exp)
    e3_pos_gl, e3_rot_gl = e3.get_global_coordinates()  # cached
    assert_equal(e3_pos_gl, xy2arr(pos_exp))
    assert_equal(e3_rot_gl, rot_exp)
