from typing import Dict, List, Set, TypeVar, Generic, List
from abc import ABC, abstractmethod
from numpy import int16, int8

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
    def __init__(self, registers: List[str], inputs: List[str]) -> None:
        self.__registers: Dict[str, int16] = {i: 0 for i in registers}
        self.__inputs: Dict[str, int8] = {i: 0 for i in inputs}

        self.__pipes: Dict[str, WireCircuitComponent[int16]] = dict()
        self.__signals: Dict[str, WireCircuitComponent[int8]] = dict()

    @abstractmethod
    def do_tick(self) -> None:
        pass

    def attach_pipe(self, register_name: str, pipe: WireCircuitComponent[int16]) -> None:
        assert register_name in self.__registers.keys(), 'Указанный регистр не существует'
        self.__pipes.update(register_name=pipe)
        pass

    def attach_signal(self, input_name: str, signal: WireCircuitComponent[bool]) -> None:
        assert input_name in self.__inputs.keys(), 'Указанный выход не существует'
        self.__signals.update(input_name=signal)
        pass

    def receive_value(self, register_name: str) -> None:
        assert register_name in self.__registers.keys(), 'Указанный регистр не существует'

        pipe = self.__pipes.get(register_name)
        if (pipe != None):
            self.__registers[register_name] = pipe.get_value()

        pass

    def set_value(self, register_name: str, val: int16) -> None:
        assert register_name in self.__registers.keys(), 'Указанный регистр не существует'
        self.__registers.update(register_name=val)

        pipe = self.__pipes.get(register_name)
        if (pipe != None):
            pipe.receive_value(val)
        pass

    def receive_signal(self, input_name: str) -> None:
        assert input_name in self.__inputs.keys(), 'Указанный выход не существует'

        signal = self.__signals.get(input_name)
        if (signal != None):
            self.__inputs[input_name] = signal.get_value()

        pass

    def __get_value(self, register_name: str) -> int16:
        assert register_name in self.__registers.keys(), 'Указанный регистр не существует'
        return self.__registers[register_name]

    def __get_signal(self, input_name: str) -> int8:
        assert input_name in self.__inputs.keys(), 'Указанный выход не существует'
        return self.__inputs[input_name]
