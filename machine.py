import sys
from typing import Dict, List, List
from abc import ABC, abstractmethod
from numpy import int16, int8, bitwise_and, binary_repr
from circuit import FunctionalCircuitComponent, WireCircuitComponent


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
    def __init__(self) -> None:
        registers: List[str] = ['OPCODE']
        inputs: List[str] = ['PCWrite', 'AdrSrc', 'MemWrite', 'IRWrite', 'WDSrc',
                             'ImmSrc', 'ALUControl', 'ALUSrcB', 'ALUSrcA', 'RegWrite', 'Zero']

        self.__registers: Dict[str, int16] = {i: 0 for i in registers}
        self.__inputs: Dict[str, int8] = {i: 0 for i in inputs}

        self.__pipes: Dict[str, WireCircuitComponent[int16]] = dict()
        self.__signals: Dict[str, WireCircuitComponent[int8]] = dict()

        # 1 - prev
        # 2 - prev prev
        self.__prev_ops: Dict[int8, int8] | None = None

    def do_tick(self) -> None:
        self.__refresh_state()

        match self.__registers.get('OPCODE'):
            case 0:
                # ADDI
                if (self.__prev_ops[1] != 0):
                    # 1 tick
                    self.set_input('PCWrite', 0)
                    self.set_input('AdrSrc', 1)
                    self.set_input('MemWrite', 0)
                    self.set_input('IRWrite', 1)
                    self.set_input('WDSrc', 0)
                    self.set_input('ImmSrc', 0)
                    self.set_input('RegWrite', 0)
                    self.set_input('ALUSrcA', 0)
                    self.set_input('ALUSrcB', 1)
                    self.set_input('ALUControl', 0)
                elif (self.__prev_ops[1] == 0 and self.__prev_ops[2] != 0):
                    # 2 tick
                    self.set_input('IRWrite', 0)
                    self.set_input('WDSrc', 1)
                    self.set_input('RegWrite', 1)
                else:
                    # PC + 16 bit
                    self.set_input('PCWrite', 1)
                    self.set_input('ALUSrcA', 1)
                    self.set_input('ALUSrcB', 3)
                    pass

                self.__update_prev_ops(0)
                pass
            case 1:
                # BEQ
                if (self.__prev_ops[1] != 1):
                    # 1 tick
                    self.set_input('PCWrite', 0)
                    self.set_input('AdrSrc', 1)
                    self.set_input('MemWrite', 0)
                    self.set_input('IRWrite', 1)
                    self.set_input('WDSrc', 0)
                    self.set_input('ImmSrc', 2)
                    self.set_input('RegWrite', 0)
                    self.set_input('ALUSrcA', 0)
                    self.set_input('ALUSrcB', 0)
                    self.set_input('ALUControl', 1)
                elif (self.__prev_ops[1] == 1 and self.__prev_ops[2] != 1):
                    # 2 tick
                    if (self.__inputs['Zero'] == 1):
                        self.set_input('IRWrite', 0)
                        self.set_input('ALUSrcA', 1)
                        self.set_input('ALUSrcB', 1)
                        self.set_input('PCWrite', 1)

                self.__update_prev_ops(1)
                pass
            case 2:
                # REM
                if (self.__prev_ops[1] != 2):
                    # 1 tick
                    self.set_input('PCWrite', 0)
                    self.set_input('AdrSrc', 1)
                    self.set_input('MemWrite', 0)
                    self.set_input('IRWrite', 1)
                    self.set_input('WDSrc', 0)
                    self.set_input('ImmSrc', 1)
                    self.set_input('RegWrite', 0)
                    self.set_input('ALUSrcA', 0)
                    self.set_input('ALUSrcB', 0)
                    self.set_input('ALUControl', 2)
                elif (self.__prev_ops[1] == 2 and self.__prev_ops[2] != 2):
                    # 2 tick
                    self.set_input('IRWrite', 0)
                    self.set_input('WDSrc', 1)
                    self.set_input('RegWrite', 1)
                else:
                    # PC + 16 bit
                    self.set_input('PCWrite', 1)
                    self.set_input('ALUSrcA', 1)
                    self.set_input('ALUSrcB', 3)
                    pass

                self.__update_prev_ops(2)
                pass
            case 3:
                # MOV
                if (self.__prev_ops[1] != 3):
                    # 1 tick
                    self.set_input('PCWrite', 0)
                    self.set_input('AdrSrc', 1)
                    self.set_input('MemWrite', 0)
                    self.set_input('IRWrite', 1)
                    self.set_input('WDSrc', 0)
                    self.set_input('ImmSrc', 0)
                    self.set_input('RegWrite', 0)
                    self.set_input('ALUSrcA', 0)
                    self.set_input('ALUSrcB', 1)
                    self.set_input('ALUControl', 0)
                elif (self.__prev_ops[1] == 3 and self.__prev_ops[2] != 3):
                    # 2 tick
                    self.set_input('IRWrite', 0)
                    self.set_input('WDSrc', 1)
                    self.set_input('RegWrite', 1)
                else:
                    # PC + 16 bit
                    self.set_input('PCWrite', 1)
                    self.set_input('ALUSrcA', 1)
                    self.set_input('ALUSrcB', 3)
                    pass

                self.__update_prev_ops(3)
                pass
            case 4:
                # LD
                if (self.__prev_ops[1] != 4):
                    # 1 tick
                    self.set_input('PCWrite', 0)
                    self.set_input('AdrSrc', 1)
                    self.set_input('MemWrite', 0)
                    self.set_input('IRWrite', 1)
                    self.set_input('WDSrc', 0)
                    self.set_input('ImmSrc', 0)
                    self.set_input('RegWrite', 0)
                    self.set_input('ALUSrcA', 0)
                    self.set_input('ALUSrcB', 1)
                    self.set_input('ALUControl', 0)
                elif (self.__prev_ops[1] == 4 and self.__prev_ops[2] != 4):
                    # 2 tick
                    self.set_input('AdrSrc', 0)
                    self.set_input('IRWrite', 0)
                    self.set_input('RegWrite', 1)
                else:
                    # PC + 16 bit
                    self.set_input('PCWrite', 1)
                    self.set_input('ALUSrcA', 1)
                    self.set_input('ALUSrcB', 3)
                    pass

                self.__update_prev_ops(4)
                pass
            case 5:
                # SW
                if (self.__prev_ops[1] != 5):
                    # 1 tick
                    self.set_input('PCWrite', 0)
                    self.set_input('AdrSrc', 1)
                    self.set_input('MemWrite', 0)
                    self.set_input('IRWrite', 1)
                    self.set_input('WDSrc', 0)
                    self.set_input('ImmSrc', 2)
                    self.set_input('RegWrite', 0)
                    self.set_input('ALUSrcA', 0)
                    self.set_input('ALUSrcB', 1)
                    self.set_input('ALUControl', 0)
                elif (self.__prev_ops[1] == 5 and self.__prev_ops[2] != 5):
                    # 2 tick
                    self.set_input('AdrSrc', 0)
                    self.set_input('MemWrite', 1)
                else:
                    # PC + 16 bit
                    self.set_input('PCWrite', 1)
                    self.set_input('ALUSrcA', 1)
                    self.set_input('ALUSrcB', 3)
                    pass

                self.__update_prev_ops(5)
                pass
            case _:
                print("Unsupported control unit operation: " +
                      self.__registers.get('OPCODE'))
                pass

    def attach_pipe(self, register_name: str, pipe: WireCircuitComponent[int16]) -> None:
        assert register_name in self.__registers.keys(), 'Указанный регистр не существует'
        self.__pipes.update(register_name=pipe)
        pass

    def attach_signal(self, input_name: str, signal: WireCircuitComponent[bool]) -> None:
        assert input_name in self.__inputs.keys(), 'Указанный выход не существует'
        self.__signals.update(input_name=signal)
        pass

    def set_input(self, input_name: str, val: int8) -> None:
        assert input_name in self.__inputs.keys(), 'Указанный выход не существует'
        self.__registers.update(register_name=val)

        signal = self.__signals.get(input_name)
        if (signal != None):
            signal.receive_value(val)
        pass

    def receive_value(self, register_name: str) -> None:
        assert register_name in self.__registers.keys(), 'Указанный регистр не существует'

        pipe = self.__pipes.get(register_name)
        if (pipe != None):
            self.__registers[register_name] = pipe.get_value()

        pass

    def receive_signal(self, input_name: str) -> None:
        assert input_name in self.__inputs.keys(), 'Указанный выход не существует'

        signal = self.__signals.get(input_name)
        if (signal != None):
            self.__inputs[input_name] = signal.get_value()

        pass

    def __refresh_state(self) -> None:
        self.__receive_value('OPCODE', 7)

        self.receive_signal('Zero')

    def __receive_value(self, register_name: str, mask: int16) -> None:
        assert register_name in self.__registers.keys(), 'Указанный регистр не существует'
        self.__registers[register_name] = bitwise_and(
            self.__pipes[register_name].get_value(), mask
        )
        pass

    def __update_prev_ops(self, op: int8) -> None:
        self.__prev_ops[2] = self.__prev_ops[1]
        self.__prev_ops[1] = op


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
