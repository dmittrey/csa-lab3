from typing import Dict, List


class CircuitWire():
    def __init__(self, val: int = 0) -> None:
        self._value = val
        pass

    def set(self, value: int) -> None:
        self._value = value
        pass

    def get(self) -> int:
        return self._value


class CircuitComponent():
    def __init__(self, registers: List[str]) -> None:
        self._registers: Dict[str, int] = {i: 0 for i in registers}

        self._wires: Dict[str, CircuitWire] = dict()

    def do_tick(self, tick_num: int = 0) -> None:
        self.update()
        pass

    def attach(self, register_name: str, wire: CircuitWire) -> None:
        assert register_name in self._registers.keys(), 'Указанный регистр не существует'
        assert wire is not None, 'Несуществующий провод данных'
        self._wires[register_name] = wire
        pass

    def set_register(self, name: str, value: int):
        assert name in self._registers.keys(), 'Указанный регистр не существует'
        self._registers[name] = value
        if (self._wires.get(name) is not None):
            self._wires[name].set(value)
        pass

    def get_register(self, name: str):
        assert name in self._registers.keys(), 'Указанный регистр не существует'

        return self._registers[name]

    def update(self):
        for wire_name, wire in self._wires.items():
            self._registers[wire_name] = wire.get()
