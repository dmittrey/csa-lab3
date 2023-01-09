import sys
from typing import Dict, List, List
from abc import ABC, abstractmethod
from numpy import int16, bitwise_and, binary_repr
from circuit import FunctionalCircuitComponent


class Triger(FunctionalCircuitComponent):
    def __init__(self) -> None:
        registers: List[str] = ['In', 'Out']
        input: str = 'EN'

        super().__init__(registers, input)

        self.__state: int16 = 0

    def do_tick(self) -> None:
        self.__refresh_state()

        if (self.get_signal('EN') == 1):
            self.__state = self.get_value('In')

        self.set_value('Out', self.__state)

    def __refresh_state(self) -> None:
        self.receive_value('In')
        self.receive_signal()


class Memory(FunctionalCircuitComponent):
    def __init__(self, memory_size: int16) -> None:
        registers: List[str] = ['A', 'RD', 'WD']
        input: str = 'WE'

        super().__init__(registers, input)

        self.__memory_size = memory_size
        self.__memory = [0] * self.__memory_size

    def do_tick(self) -> None:
        self.__refresh_state()

        data_addr = self.get_value('A')

        if (self.get_signal('WE') == 1):
            self.__memory[data_addr] = self.get_value('WD')
        else:
            self.set_value('RD', self.__memory[data_addr])

    def __refresh_state(self) -> None:
        self.receive_value('A')
        self.receive_value('WD')
        self.receive_signal()


class RegisterFile(FunctionalCircuitComponent):
    def __init__(self) -> None:
        registers: List[str] = ['A1', 'A2', 'A3', 'RD1', 'RD2', 'WD']
        input: str = 'WE3'

        super().__init__(registers, input)

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

        if (self.get_signal('WE3') == 1):
            if (self.get_value('A3') != 0):
                self.__inner_registers[self.get_value(
                    'A3')] = self.get_value('WD')
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

        self.receive_signal()

    def __receive_value(self, register_name: str, mask: int16) -> None:
        assert register_name in self.__registers.keys(), 'Указанный регистр не существует'
        self.__registers[register_name] = bitwise_and(
            self.__pipes[register_name].get_value(), mask
        )
        pass


class ALU(FunctionalCircuitComponent):
    def __init__(self) -> None:
        registers: List[str] = ['srcA', 'srcB', 'Result']
        input: str = ['ALUControl']

        super().__init__(registers, input)

        self.zeroFlag = False

    # 0 - SUM
    # 1 - SUB
    # 2 - REM
    def do_tick(self) -> None:
        self.__refresh_state()

        match self.get_signal('ALUControl'):
            case 0:
                self.set_value('Result', self.get_value(
                    'srcA') + self.get_value('srcB'))
                pass
            case 1:
                self.set_value('Result', self.get_value(
                    'srcA') - self.get_value('srcB'))
                pass
            case 2:
                self.set_value('Result', self.get_value(
                    'srcA') % self.get_value('srcB'))
                pass
            case _:
                print("ALU operation not permitted: " +
                      self.get_signal('ALUControl'))

    def __refresh_state(self) -> None:
        self.receive_value('srcA')
        self.receive_value('srcB')

        self.receive_signal()


class SignExpand(FunctionalCircuitComponent):
    def __init__(self) -> None:
        registers: List[str] = ['In', 'Out']
        input: str = ['ImmSrc']

        super().__init__(registers, input)

    # 0 - Расширить значение из 9-15 бит команды
    # 1 - Расширить значение из 12-15 бит команды
    # 2 - Расширить значение из 12-15 и 3-5 бит команды
    def do_tick(self) -> None:
        match self.get_signal('ImmSrc'):
            case 0:
                self.__refresh_state(65024)
                pass
            case 1:
                self.__refresh_state(61440)
                pass
            case 2:
                self.__refresh_state(61496)
                pass
            case _:
                print("Expand operation not permitted: " +
                      self.get_signal('ImmSrc'))

        self.set_value('Out', self.get_value('In'))

    def __refresh_state(self, imm_extension_mask: int16) -> None:
        self.__receive_value('In', imm_extension_mask)

        self.receive_signal()

    def __receive_value(self, register_name: str, mask: int16) -> None:
        assert register_name in self.__registers.keys(), 'Указанный регистр не существует'
        self.__registers[register_name] = bitwise_and(
            self.__pipes[register_name].get_value(), mask
        )
        pass


class MUX1Bits(FunctionalCircuitComponent):
    def __init__(self, input: str) -> None:
        registers: List[str] = ['In_0', 'In_1', 'Out']

        super().__init__(registers, input)

    # 0 - Данные со входа In_0
    # 1 - Данные со входа In_1
    def do_tick(self) -> None:
        self.__refresh_state()

        match self.get_signal(self.__input):
            case 0:
                self.set_value('Out', self.get_value('In_0'))
                pass
            case 1:
                self.set_value('Out', self.get_value('In_1'))
                pass
            case _:
                print("MUX operation not permitted: " +
                      self.get_signal(self.__input))

    def __refresh_state(self) -> None:
        self.receive_value('In_0')
        self.receive_value('In_1')

        self.receive_signal()


class MUX2Bits(FunctionalCircuitComponent):
    def __init__(self, input: str) -> None:
        registers: List[str] = ['In_00', 'In_01', 'In_10', 'Out']

        super().__init__(registers, input)

    # 0 - Данные со входа In_00
    # 1 - Данные со входа In_01
    # 2 - Данные со входа In_10
    # 3 - Данные со входа In_11
    def do_tick(self) -> None:
        self.__refresh_state()

        match self.get_signal(self.__input):
            case 0:
                self.set_value('Out', self.get_value('In_00'))
                pass
            case 1:
                self.set_value('Out', self.get_value('In_01'))
                pass
            case 2:
                self.set_value('Out', self.get_value('In_10'))
                pass
            case 3:
                self.set_value('Out', self.get_value('In_11'))
                pass
            case _:
                print("MUXSrcB operation not permitted: " +
                      self.get_signal('ALUSrcB'))

    def __refresh_state(self) -> None:
        self.receive_value('In_00')
        self.receive_value('In_01')
        self.receive_value('In_10')
        self.receive_value('In_11')

        self.receive_signal()


class DataPath():
    def __init__(self) -> None:
        pass


class ControlUnit():

    pass


def main(args):
    val1: int16 = 49098
    val2: int16 = -49098
    # if (val2 < 0):
    str1 = binary_repr(val1)

    # str2 = binary_repr(invert(val2) + 1)
    str2 = binary_repr(val2)

    print(str1)
    print("awdawd")
    print(str2)
    pass


if __name__ == '__main__':
    main(sys.argv[1:])
