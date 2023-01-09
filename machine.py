import sys
from typing import Dict, List, Set, TypeVar, Generic, List
from abc import ABC, abstractmethod
from numpy import int16, bitwise_and
from circuit import FunctionalCircuitComponent, WireCircuitComponent


class ProgramCounter(FunctionalCircuitComponent):
    def __init__(self) -> None:
        registers: List[str] = ['PC', 'PCNext']
        inputs: List[str] = ['EN']

        super().__init__(registers, inputs)

    def do_tick(self) -> None:
        self.__refresh_state()

        if (self.__get_signal('EN') == 1):
            self.set_value('PC', self.__get_value('PCNext'))

    def __refresh_state(self) -> None:
        self.receive_value('PCNext')
        self.receive_signal('EN')


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

        if (self.__get_signal('WE') == 1):
            self.__memory[data_addr] = self.__get_value('WD')
        else:
            self.set_value('RD', self.__memory[data_addr])

    def __refresh_state(self) -> None:
        self.receive_value('A')
        self.receive_value('WD')
        self.receive_signal('WE')


class RegisterFile(FunctionalCircuitComponent):
    def __init__(self, registers: List[str], inputs: List[str]) -> None:
        registers: List[str] = ['A1', 'A2', 'A3', 'RD1', 'RD2', 'WD']
        inputs: List[str] = ['WE3']

        super().__init__(registers, inputs)

        self.__inner_registers: Dict[int, int16] = {
            0: 0,
            1: 0,
            2: 0,
            3: 0,
            4: 0,
            5: 0,
            6: 0,
            7: 0
        }

    def do_tick(self) -> None:
        self.__refresh_state()

        if (self.__get_signal('WE3') == 1):
            if (self.__get_value('A3') != 0):
                self.__inner_registers[self.__get_value(
                    'A3')] = self.__get_value('WD')
        else:
            self.set_value(
                'RD1', self.__inner_registers[self.__registers['A1']])
            self.set_value(
                'RD2', self.__inner_registers[self.__registers['A2']])

    def __refresh_state(self) -> None:
        self.__receive_value('A1', 448)
        self.__receive_value('A2', 3584)
        self.__receive_value('A3', 56)
        self.receive_value('WD')

        self.receive_signal('WE3')

    def __receive_value(self, register_name: str, mask: int16) -> None:
        assert register_name in self.__registers.keys(), 'Указанный регистр не существует'
        self.__registers[register_name] = bitwise_and(
            self.__pipes[register_name].get_value(), mask
        )
        pass


class ALU(FunctionalCircuitComponent):
    def __init__(self, registers: List[str], inputs: List[str]) -> None:
        registers: List[str] = ['srcA', 'srcB', 'Result']
        inputs: List[str] = ['ALUControl']

        super().__init__(registers, inputs)

        self.zeroFlag = False

    def do_tick(self) -> None:
        self.__refresh_state()

        match self.__get_signal('ALUControl'):
            case 0:
                self.set_value('Result', self.__get_value(
                    'srcA') + self.__get_value('srcB'))
                pass
            case 1:
                self.set_value('Result', self.__get_value(
                    'srcA') - self.__get_value('srcB'))
                pass
            case 2:
                self.set_value('Result', self.__get_value(
                    'srcA') % self.__get_value('srcB'))
                pass
            case _:
                print("ALU operation not permitted: " +
                      self.__get_signal('ALUControl'))

    def __refresh_state(self) -> None:
        self.receive_value('srcA')
        self.receive_value('srcB')

        self.receive_signal('ALUControl')


class DataPath():
    def __init__(self) -> None:
        pass


class ControlUnit():
    pass


def main(args):
    pc = ProgramCounter()
    pc.do_tick()
    pass


if __name__ == '__main__':
    main(sys.argv[1:])
