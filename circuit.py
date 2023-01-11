from typing import Dict, List, Set, TypeVar, Generic, List
from abc import ABC, abstractmethod
from numpy import int16, int8, bitwise_and, binary_repr

T = TypeVar('T', int16, int8)


class WireCircuitComponent(Generic[T]):
    def __init__(self) -> None:
        self.__value: T = 0
        pass

    def receive_value(self, value: T) -> None:
        self.__value = value
        pass

    def get_value(self) -> T:
        return self.__value


class FunctionalCircuitComponent(ABC):
    def __init__(self, registers: List[str], input: str) -> None:
        self.__input = input

        self.registers: Dict[str, int16] = {i: 0 for i in registers}
        self.__inputs: Dict[str, int8] = {input: 0}

        self.__pipes: Dict[str, WireCircuitComponent[int16]] = dict()
        self.__signals: Dict[str, WireCircuitComponent[int8]] = dict()

    @abstractmethod
    def do_tick(self) -> None:
        pass

    def attach_pipe(self, register_name: str, pipe: WireCircuitComponent[int16]) -> None:
        assert register_name in self.registers.keys(), 'Указанный регистр не существует'
        self.__pipes[register_name] = pipe
        pass

    def attach_signal(self, signal: WireCircuitComponent[bool]) -> None:
        self.__signals[self.__input] = signal
        pass

    def receive_value(self, register_name: str) -> None:
        assert register_name in self.registers.keys(), 'Указанный регистр не существует'

        pipe = self.__pipes.get(register_name)
        if (pipe != None):
            self.registers[register_name] = pipe.get_value()

        pass

    def receive_mask_value(self, register_name: str, mask: int16, shift: int16) -> None:
        assert register_name in self.registers.keys(), 'Указанный регистр не существует'

        pipe = self.__pipes.get(register_name)
        if (pipe != None):
            self.registers[register_name] = bitwise_and(
                self.__pipes[register_name].get_value(), mask) >> shift
        pass

    def set_value(self, register_name: str, val: int16) -> None:
        assert register_name in self.registers.keys(), 'Указанный регистр не существует'
        self.registers[register_name] = val

        pipe = self.__pipes.get(register_name)
        if (pipe != None):
            pipe.receive_value(val)
        pass

    def receive_signal(self) -> None:
        signal = self.__signals.get(self.__input)
        if (signal != None):
            self.__inputs[self.__input] = signal.get_value()

        pass

    def get_value(self, register_name: str) -> int16:
        assert register_name in self.registers.keys(), 'Указанный регистр не существует'
        return self.registers[register_name]

    def get_signal(self) -> int8:
        return self.__inputs[self.__input]
