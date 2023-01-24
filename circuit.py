# pylint: disable=missing-module-docstring    # чтобы не быть Капитаном Очевидностью
# pylint: disable=missing-class-docstring     # чтобы не быть Капитаном Очевидностью
# pylint: disable=missing-function-docstring  # чтобы не быть Капитаном Очевидностью
# pylint: disable=line-too-long               # строки с ожидаемым выводом

from typing import Dict, List


class CircuitWire():
    def __init__(self, val: int = 0) -> None:
        self.value = val

    def set(self, value: int) -> None:
        self.value = value

    def get(self) -> int:
        return self.value


class CircuitComponent():
    def __init__(self, registers: List[str]) -> None:
        self.registers: Dict[str, int] = {i: 0 for i in registers}

        self._wires: Dict[str, CircuitWire] = {}

    def do_tick(self) -> None:
        self.update()

    def attach(self, register_name: str, wire: CircuitWire) -> None:
        assert register_name in self.registers.keys(), 'Указанный регистр не существует'
        assert wire is not None, 'Несуществующий провод данных'
        self._wires[register_name] = wire

    def set_register(self, name: str, value: int):
        assert name in self.registers.keys(), 'Указанный регистр не существует'
        self.registers[name] = value
        if self._wires.get(name) is not None:
            self._wires[name].set(value)

    def get_register(self, name: str):
        assert name in self.registers.keys(), 'Указанный регистр не существует'

        return self.registers[name]

    def update(self):
        for wire_name, wire in self._wires.items():
            self.registers[wire_name] = wire.get()
