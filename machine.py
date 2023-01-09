from typing import Dict, List, Set, TypeVar, Generic, List
from abc import ABC, abstractmethod
from numpy import int16
from circuit import FunctionalCircuitComponent, WireCircuitComponent


class ProgramCounter(FunctionalCircuitComponent):
    def __init__(self) -> None:
        registers: List[str] = ['PC', 'PCNext']
        inputs: List[str] = ['EN']

        super().__init__(registers, inputs)

    def do_tick(self) -> None:
        self.__refresh_state()

        if (self.__get_signal('EN')):
            self.set_value('PC', self.__get_value('PCNext'))

    def __refresh_state(self) -> None:
        self.receive_value('PCNext')
        self.receive_signal('EN')

        pass


class Memory(FunctionalCircuitComponent):
    def __init__(self, memory_size: int16) -> None:
        registers: List[str] = ['A', 'RD', 'WD']
        inputs: List[str] = ['WE']

        super().__init__(registers, inputs)

        self.__memory_size = memory_size
        self.__memory = [0] * self.__memory_size

    def do_tick(self) -> None:
        self.__refresh_state()

        data_addr = self.__get_value('A')

        if (self.__get_signal('WE')):
            self.__memory[data_addr] = self.__get_value('WD')
        else:
            self.set_value('RD', self.__memory[data_addr])

    def __refresh_state(self) -> None:
        self.receive_value('A')
        self.receive_value('WD')
        self.receive_signal('WE')

        pass


class DataPath():
    def __init__(self) -> None:
        pass


class ControlUnit():
    pass


def main(args):

    pass


if __name__ == '__main__':
    main()
