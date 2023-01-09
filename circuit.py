from typing import Dict, List, Set, TypeVar, Generic, List
from abc import ABC, abstractmethod
from numpy import int16

T = TypeVar('T', int16, bool)


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

        self.__inputs: List[str] = inputs

        self.__pipes: Dict[str, WireCircuitComponent[int16]] = dict()

        self.__signals: Dict[str, WireCircuitComponent[bool]] = dict()

    @abstractmethod
    def do_tick(self) -> None:
        pass

    @abstractmethod
    def __refresh_state(self) -> None:
        pass

    def attach_pipe(self, register_name: str, pipe: WireCircuitComponent[int16]) -> None:
        assert register_name in self.__registers, 'Указанный регистр не существует'
        self.__pipes[register_name] = pipe
        pass

    def attach_signal(self, input_name: str, signal: WireCircuitComponent[bool]) -> None:
        assert input_name in self.__inputs, 'Указанный выход не существует'
        self.__signals[input_name] = signal
        pass

    def receive_value(self, register_name: str, value: int16) -> None:
        assert register_name in self.__registers, 'Указанный регистр не существует'
        self.__pipes[register_name] = value
        pass

    def receive_signal(self, input_name: str, signal: bool) -> None:
        assert input_name in self.__inputs, 'Указанный выход не существует'
        self.__signals[input_name] = signal
        pass

    def __get_value(self, register_name: str) -> int16:
        assert register_name in self.__registers, 'Указанный регистр не существует'
        return self.__registers[register_name]

    def __get_signal(self, input_name: str) -> bool:
        assert input_name in self.__inputs, 'Указанный выход не существует'
        return self.__inputs[input_name]
