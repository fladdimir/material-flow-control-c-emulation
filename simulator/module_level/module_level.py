# helper class to connect a running simulation with emulated module controls running in own processes
# just passes control to the sub-process and waits for confirmation signal

from multiprocessing import Array, Pipe, Process

from module_control.emulation.cffi.module import AIV, start
from simulator.modules.turntable import TurnTable


def bool_2_int(value: bool) -> int:
    return 1 if value else 0  # tbd: needed?


class Module2ControlParent:
    def __init__(self, tt: TurnTable) -> None:
        self.tt = tt

        self.clock_connection, clock_connection = Pipe()
        ack_connection, self.ack_connection = Pipe()  # todo: replace by duplex clock

        self.module_parent_connection, module_child_connection = Pipe()
        # tbd: limit capacity (64 Byte), inject from outside

        self.array = Array("i", AIV.SIZE)  # tbd: proper enum

        self.conveyor_control_proc = Process(
            target=start,
            args=(
                clock_connection,
                ack_connection,
                self.array,
                module_child_connection,
                self.tt.name,
            ),
        )
        self.conveyor_control_proc.start()

    def loop(self, passed_time_ms: int) -> None:
        self.array[AIV.LIGHT_BARRIER] = bool_2_int(
            self.tt.is_light_barrier_active_sensor()
        )
        self.array[AIV.ENDLAGE_0] = bool_2_int(self.tt.is_not_turned_sensor())
        self.array[AIV.ENDLAGE_90] = bool_2_int(self.tt.is_fully_turned_sensor())

        self.clock_connection.send(passed_time_ms)  # passes control to module-process
        success: bool = self.ack_connection.recv()  # blocks

        rotation: int = self.array[AIV.ROTATION]  # -1, 0, 1
        if self.tt.current_rotation_direction() != rotation:
            if self.tt.current_rotation_direction() != 0:
                self.tt.stop_turning()
            if rotation == 1:
                self.tt.turn_clockwise()
            if rotation == -1:
                self.tt.turn_counter_clockwise()

        translation: int = self.array[AIV.TRANSLATION]  # -1, 0, 1
        if self.tt.belt.current_direction != translation:
            if self.tt.current_translation_direction() != 0:
                self.tt.stop_move()
            if translation == 1:
                self.tt.start_move_forward()
            if translation == -1:
                self.tt.start_move_backward()
