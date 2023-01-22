from enum import Enum
import sys
from typing import Dict, List, List
from numpy import int16, int8
from circuit import CircuitComponent
from components import Register, SignExpand, Trigger, Memory, RegisterFile, ALU, MUX, IOHandler, IOMemoryCell

from isa import read_code, Opcode


class DataPath():
    class DataPathComponent(CircuitComponent, Enum):
        PC = Trigger()
        Adr_Src_Mux = MUX(1, 'AdrSrc')
        Memory = Memory(512)
        IR = Trigger()
        WD_Src_Mux = MUX(1, 'WDSrc')
        Register_File = RegisterFile()
        Sign_Expand = SignExpand()
        Alu_Src_A_Mux = MUX(1, 'ALUSrcA')
        Alu_Src_B_Mux = MUX(2, 'ALUSrcB')
        ALU = ALU()
        IO_Handler = IOHandler()

        @classmethod
        def list(cls) -> List[CircuitComponent]:
            return list(map(lambda c: c.value, cls))

    def __init__(self) -> None:
        self.tick = 0
        pass

    def do_tick(self) -> None:
        self.tick += 1

        for component in self.DataPathComponent.list():
            component.do_tick()

        self.__get_info(self.tick)

    def enter_interrupt(self) -> None:
        for component in self.DataPathComponent.list():
            component.enter_interrupt()

    def __get_info(self, tick: int) -> Dict[str, int]:
        print(str(tick), ')', sep='', end=' ')
        for register_name, register_value in self.register_file.inner_registers.items():
            print('x' + str(register_name), register_value, sep=' : ', end=' | ')
        print('\nAluSrcA :', self.alu.get_value('srcA'), '|', 'ALUSrcB :', self.alu.get_value(
            'srcB'), '|', 'Result :', self.alu.get_value('Result'), '|', sep=' ', end=' ')
        print('PC :', self.pc_triger.state)


class ControlUnit(CircuitComponent):

    def __init__(self, is_interrupts_allowed: bool = False) -> None:
        self.__is_interrupts_allowed: bool = is_interrupts_allowed

        self._in_interrupt_context: bool = False
        self._instruction_transitions: Dict[Opcode, List[Dict[str, int]]] = {
            Opcode.ADDI: [{}, {}, {}],
            Opcode.BNE: [{}, {}, {}],
            Opcode.REM: [{}, {}, {}],
            Opcode.LD: [{}, {}, {}],
            Opcode.SW: [{}, {}, {}],
            Opcode.JMP: [{}, {}, {}],
            Opcode.HALT: [{}, {}, {}]
        }

        super().__init__(['OPCODE', 'PCWrite', 'AdrSrc', 'MemWrite', 'IRWrite', 'WDSrc', 'IOOp',
                          'ImmSrc', 'ALUControl', 'ALUSrcB', 'ALUSrcA', 'RegWrite', 'Zero', 'IOInt'])

    def start(self, data_path: DataPath) -> None:
        while True:
            opcode = self._wires['OPCODE'].get()
            if (opcode == Opcode.HALT):
                break

            op_transitions = self.__get_op_transitions(opcode)
            if (op_transitions != None):
                for valves_state in op_transitions:
                    self.update()
                    self.__handle_interrupt(data_path)
                    self.__change_valves(valves_state)
            else:
                raise AttributeError('Unsopported opcode: ' + str(opcode))

    def update(self):
        for wire_name, wire in self._wires.items():
            match wire_name:
                case 'OPCODE':
                    self._registers[wire_name] = wire.get() & 7
                    pass
                case _:
                    self._registers[wire_name] = wire.get()
                    pass

    def __change_valves(self, new_state: Dict[str, int]) -> None:
        for register_name, register_val in self._registers.items():
            if (new_state.get(register_name) != None):
                self.set_register(register_name, register_val)
            else:
                # Set to zero all unused registers to easily handle instructions
                self.set_register(register_name, 0)

    def __get_op_transitions(self, op: int) -> None | List[Dict[str, int]]:
        return self._instruction_transitions.get(op)

    def __handle_interrupt(self, data_path: DataPath) -> None:
        if (self.__is_interrupts_allowed and (not self._in_interrupt_context)
                and self.get_register('IOInt') == 1):
            # Set interrupt mode and receive INT signal
            self._in_interrupt_context = True
            self.set_register('IOInt', 0)

            # Save control unit state
            registers = self._registers.copy()
            # Goto interrupt vector
            data_path.enter_interrupt()
            # Start executing
            self.start(data_path)

            # Restore state after handling interrupt
            self._registers = registers
            self._in_interrupt_context = False


def main(args):
    # filename = 'examples/prob5.out'
    # filename = 'examples/cat.out'

    filename, start_code, is_interrupts_enabled = [
        'examples/hello.out', 8, True]

    codes = read_code(filename)

    pass


if __name__ == '__main__':
    main(sys.argv[1:])
