from typing import Dict, List
from circuit import CircuitComponent
from enum import Enum
import numpy


class Trigger(CircuitComponent):
    def __init__(self) -> None:
        self._state: int = 0

        super().__init__(['In', 'Out', 'EN'])

    def do_tick(self) -> None:
        super().do_tick()

        if (self.get_register('EN') != 0):
            self._state = self.get_register('In')

        self.set_register('Out', self._state)


class Memory(CircuitComponent):
    def __init__(self, memory_size: int) -> None:
        assert memory_size > 0, 'Memory size is not positive'
        self._memory: List[int] = [0] * memory_size

        super().__init__(['A', 'RD', 'WD', 'WE'])

    def do_tick(self) -> None:
        super().do_tick()

        data_addr = self.get_register('A')
        assert data_addr < len(self._memory), 'Memory out'

        if (self.get_register('WE') != 0):
            self._memory[data_addr] = self.get_register('WD')
        else:
            self.set_register('RD', self._memory[data_addr])

    def load_program(self, program: List[int], start_address: int):
        assert len(self._memory) > len(program) + \
            start_address, 'Impossible to accommodate the program'

        for num in range(len(program)):
            self._memory[num + start_address] = program[num]


class Register(int, Enum):
    x0 = 0
    x1 = 1
    x2 = 2
    x3 = 3
    x4 = 4
    x5 = 5
    x6 = 6
    x7 = 7


class RegisterFile(CircuitComponent):
    def __init__(self) -> None:
        self._inner_registers: Dict[int, int] = {
            Register.x0: 0,  # x0 | ZR
            Register.x1: 0,  # x1 | PC
            Register.x2: 0,  # x2
            Register.x3: 0,  # x3 | DR
            Register.x4: 0,  # x4 | mepc(Previous PC value)
            Register.x5: 0,  # x5 | mtvec(Interrupt vector address)
            Register.x6: 0,  # x6 | AC
            Register.x7: 0,  # x7 | mscratch(Save mem block for state)
        }

        super().__init__(['A1', 'A2', 'A3', 'RD1', 'RD2', 'WD', 'PC', 'WE3'])

    def do_tick(self) -> None:
        super().do_tick()

        self._inner_registers[Register.x1] = self.get_register('PC')

        if (self.get_register('WE3') == 0):
            self.set_register(
                'RD1', self._inner_registers[self.get_register('A1')])
            self.set_register(
                'RD2', self._inner_registers[self.get_register('A2')])
        else:
            if (self.get_register('A3') != 0):
                self._inner_registers[self.get_register(
                    'A3')] = self.get_register('WD')

            if (self.get_register('A3') == 1):
                self.set_register('PC', self.get_register('WD'))

    def update(self):
        for wire_name, wire in self._wires.items():
            match wire_name:
                case 'A1':
                    self._registers[wire_name] = (wire.get() >> 6) & 7
                    pass
                case 'A2':
                    self._registers[wire_name] = (wire.get() >> 9) & 7
                    pass
                case 'A3':
                    self._registers[wire_name] = (wire.get() >> 3) & 7
                    pass
                case _:
                    self._registers[wire_name] = wire.get()
                    pass


class ALU(CircuitComponent):
    def __init__(self) -> None:
        super().__init__(['srcA', 'srcB', 'Result', 'ALUControl', 'ZeroFlag'])

    # 0 - SUM, 1 - SUB, 2 - REM
    def do_tick(self) -> None:
        super().do_tick()

        match self.get_register('ALUControl'):
            case 0:
                self.set_register('Result', self.get_register(
                    'srcA') + self.get_register('srcB'))
                pass
            case 1:
                self.set_register('Result', self.get_register(
                    'srcA') - self.get_register('srcB'))
                pass
            case 2:
                self.set_register('Result', self.get_register(
                    'srcA') % self.get_register('srcB'))
                pass
            case _:
                raise AssertionError('ALU operation not permitted')

        if (self.get_register('Result') == 0):
            self.set_register('ZeroFlag', 1)
        else:
            self.set_register('ZeroFlag', 0)


class SignExpand(CircuitComponent):
    def __init__(self) -> None:
        super().__init__(['In', 'Out', 'ImmSrc'])

    # 0 - Расширить значение из 9-15 бит команды
    # 1 - Расширить значение из 12-15 бит команды
    # 2 - Расширить значение из 12-15 и 3-5 бит команды
    def do_tick(self) -> None:
        super().do_tick()

        in_value = self.get_register('In')
        match self.get_register('ImmSrc'):
            case 0:
                self.set_register('Out', (in_value >> 9) & 127)
                pass
            case 1:
                self.set_register('Out', (in_value >> 12) & 15)
                pass
            case 2:
                left_part = (in_value >> 9) & 120
                right_part = (in_value >> 3) & 7
                self.set_register('Out', left_part + right_part)
                pass
            case _:
                raise AssertionError('Expand sign operation not permitted')


class MUX1Bits(CircuitComponent):
    def __init__(self, input: str) -> None:
        super().__init__(['In_0', 'In_1', 'Out', input])

    # 0 - Данные со входа In_0
    # 1 - Данные со входа In_1
    def do_tick(self) -> None:
        super().do_tick()

        self.set_register('Out', self.get_register(
            'In_' + numpy.binary_repr(input, 1)))


class MUX2Bits(CircuitComponent):
    def __init__(self, input: str) -> None:
        super().__init__(['In_00', 'In_01', 'In_10', 'In_11', 'Out', input])

    # 0 - Данные со входа In_00
    # 1 - Данные со входа In_01
    # 2 - Данные со входа In_10
    # 3 - Данные со входа In_11
    def do_tick(self) -> None:
        super().do_tick()

        self.set_register('Out', self.get_register(
            'In_' + numpy.binary_repr(input, 2)))


class IOMemoryCell(int, Enum):
    IN = 120
    OUT = 121


class IOHandler(CircuitComponent):
    def __init__(self) -> None:
        self.state = 0

        self.interrupt_tokens = [
            (1, 'h'), (10, 'e'), (20, 'l'), (25, 'l'), (100, 'o')]
        self.saved_tokens = []

        super().__init__(['In', 'WD', 'Out', 'IOOp', 'IOInt'])

    def do_tick(self, tick: int) -> None:
        super().do_tick()

        for token in self.interrupt_tokens:
            token_tick, token_value = token
            if (token_tick == tick):
                self.set_register('IOInt', 1)
                self.state = token_value

        if (self.get_register('IOOp') == 1):
            if (self.get_register('In') == IOMemoryCell.IN):
                self.set_register('Out', ord(self.state))
                print('Readed:', self.state)

            if (self.get_register('Out') == IOMemoryCell.OUT):
                self.saved_tokens.append(self.get_register('WD'))
                print('Saved:', chr(self.get_register('WD')))
        else:
            if (self.get_register('In') in [120, 121]):
                raise Exception('Unsopported operation on memory cell')
