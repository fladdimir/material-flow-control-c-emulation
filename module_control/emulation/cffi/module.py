# runs in a sub-process of the emulation environment
# calls C control code
# wires Python implementations for forward-declared C functions

import os
from multiprocessing.connection import Connection
from typing import TYPE_CHECKING


class AIV:  # array index values
    SIZE = 5  # tbd...
    LIGHT_BARRIER = 0
    ENDLAGE_0 = 1
    ENDLAGE_90 = 2
    ROTATION = 3
    TRANSLATION = 4


def int_2_bool(value: int) -> bool:
    return True if value > 0 else False


def start(
    clock_connection: Connection,
    ack_connection: Connection,
    shared_array,  #  shared_array for read / write
    serial_connection: Connection,
    name: str,
):
    print(name + " running with pid: " + str(os.getpid()))  # debug attach

    from module_control.emulation.cffi.cffi_module import ffi

    if TYPE_CHECKING:
        import module_control.emulation.cffi.cffi_module as cffi_module
    else:
        from module_control.emulation.cffi.cffi_module import lib as cffi_module

    # setup everything
    millis = 0

    @ffi.def_extern()
    def _light_barrier() -> bool:
        return shared_array[AIV.LIGHT_BARRIER]

    @ffi.def_extern()
    def _endlage_0() -> bool:
        return shared_array[AIV.ENDLAGE_0]

    @ffi.def_extern()
    def _endlage_90() -> bool:
        return shared_array[AIV.ENDLAGE_90]

    @ffi.def_extern()
    def _set_rotation(dir: int) -> None:
        shared_array[AIV.ROTATION] = dir

    @ffi.def_extern()
    def _set_translation(dir: int) -> None:
        shared_array[AIV.TRANSLATION] = dir

    @ffi.def_extern()
    def _millis() -> int:
        return millis

    @ffi.def_extern()
    def _serial_read() -> int:
        if serial_connection.poll(timeout=0):
            b = serial_connection.recv()  # tbd: read only one byte at a time
            # print(name + " - serial read: " + str(b))
            return b
        return -1

    @ffi.def_extern()
    def _serial_write(b: int) -> None:
        # print(name + " - serial write: " + str(b))
        serial_connection.send(b)

    @ffi.def_extern()
    def _log(message: int) -> None:
        # print(name + " - log: " + str(ffi.string(message)))
        pass

    @ffi.def_extern()
    def _throw_exception() -> None:
        raise RuntimeError("module control error")

    ### run module

    cffi_module.setup()

    while True:
        passed_time_ms: int = clock_connection.recv()  # blocks
        millis += passed_time_ms
        cffi_module.loop()
        ack_connection.send(True)
