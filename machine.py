from enum import Enum
import logging
import sys
from typing import Dict, List
from circuit import CircuitComponent, CircuitWire
from components import SignExpand, Trigger, Memory, RegisterFile, ALU, MUX, IOHandler, Register

from isa import read_code, Opcode


class DataPath():
    def __init__(self, memory_size: int = 512) -> None:
        self.tick = 0
        self.in_interrupt = False

        self.PC = Trigger()
        self.Adr_Src_Mux = MUX(1, 'AdrSrc')
        self.Memory = Memory(memory_size)
        self.IR = Trigger()
        self.WD_Src_Mux = MUX(1, 'WDSrc')
        self.Register_File = RegisterFile()
        self.Sign_Expand = SignExpand()
        self.Alu_Src_A_Mux = MUX(1, 'ALUSrcA')
        self.Alu_Src_B_Mux = MUX(2, 'ALUSrcB')
        self.ALU = ALU()
        self.IO_Handler = IOHandler()

        self.control_wires: Dict[str, CircuitWire] = {}

        # Pipes
        alu_result_pipe = CircuitWire()
        pc_pipe = CircuitWire()
        adr_pipe = CircuitWire()
        rd_pipe = CircuitWire()
        wd_pipe = CircuitWire()
        instr_pipe = CircuitWire()
        rd1_pipe = CircuitWire()
        rd2_pipe = CircuitWire()
        ext_imm_pipe = CircuitWire()
        pc_inc_pipe = CircuitWire(1)
        src_a_pipe = CircuitWire()
        src_b_pipe = CircuitWire()

        # Attach pipes
        self.ALU.attach('Result', alu_result_pipe)
        self.PC.attach('In', alu_result_pipe)
        self.Adr_Src_Mux.attach('In_1', alu_result_pipe)
        self.WD_Src_Mux.attach('In_1', alu_result_pipe)

        self.PC.attach('Out', pc_pipe)
        self.Adr_Src_Mux.attach('In_0', pc_pipe)
        self.Alu_Src_A_Mux.attach('In_1', pc_pipe)

        self.Adr_Src_Mux.attach('Out', adr_pipe)
        self.Memory.attach('A', adr_pipe)
        self.IO_Handler.attach('In', adr_pipe)

        self.Memory.attach('RD', rd_pipe)
        self.IR.attach('In', rd_pipe)
        self.WD_Src_Mux.attach('In_0', rd_pipe)
        self.IO_Handler.attach('Out', rd_pipe)

        self.WD_Src_Mux.attach('Out', wd_pipe)
        self.Register_File.attach('WD', wd_pipe)

        self.IR.attach('Out', instr_pipe)
        self.Register_File.attach('A1', instr_pipe)
        self.Register_File.attach('A2', instr_pipe)
        self.Register_File.attach('A3', instr_pipe)
        self.Sign_Expand.attach('In', instr_pipe)

        self.Register_File.attach('RD1', rd1_pipe)
        self.Alu_Src_A_Mux.attach('In_0', rd1_pipe)

        self.Register_File.attach('RD2', rd2_pipe)
        self.Alu_Src_B_Mux.attach('In_00', rd2_pipe)
        self.Memory.attach('WD', rd2_pipe)
        self.IO_Handler.attach('WD', rd2_pipe)

        self.Sign_Expand.attach('Out', ext_imm_pipe)
        self.Alu_Src_B_Mux.attach('In_01', ext_imm_pipe)

        self.Alu_Src_B_Mux.attach('In_10', pc_inc_pipe)

        self.Alu_Src_A_Mux.attach('Out', src_a_pipe)
        self.ALU.attach('srcA', src_a_pipe)

        self.Alu_Src_B_Mux.attach('Out', src_b_pipe)
        self.ALU.attach('srcB', src_b_pipe)

        # Signals
        pc_write_signal = CircuitWire()
        adr_src_signal = CircuitWire()
        mem_write_signal = CircuitWire()
        ir_write_signal = CircuitWire()
        wd_src_signal = CircuitWire()
        imm_src_signal = CircuitWire()
        alu_control_signal = CircuitWire()
        alu_src_b_signal = CircuitWire()
        alu_src_a_signal = CircuitWire()
        reg_write_signal = CircuitWire()
        zero_signal = CircuitWire()
        io_operation_signal = CircuitWire()
        io_inerrupt_signal = CircuitWire()

        # Attach signals
        self.PC.attach('EN', pc_write_signal)
        self.Adr_Src_Mux.attach('AdrSrc', adr_src_signal)
        self.Memory.attach('WE', mem_write_signal)
        self.IR.attach('EN', ir_write_signal)
        self.WD_Src_Mux.attach('WDSrc', wd_src_signal)
        self.Sign_Expand.attach('ImmSrc', imm_src_signal)
        self.Register_File.attach('WE3', reg_write_signal)
        self.Alu_Src_A_Mux.attach('ALUSrcA', alu_src_a_signal)
        self.Alu_Src_B_Mux.attach('ALUSrcB', alu_src_b_signal)
        self.ALU.attach('ALUControl', alu_control_signal)
        self.ALU.attach('ZeroFlag', zero_signal)
        self.IO_Handler.attach('IOOp', io_operation_signal)
        self.IO_Handler.attach('IOInt', io_inerrupt_signal)

        # Register control wires
        self.control_wires['OPCODE'] = instr_pipe
        self.control_wires['PCWrite'] = pc_write_signal
        self.control_wires['PCWrite'] = pc_write_signal
        self.control_wires['AdrSrc'] = adr_src_signal
        self.control_wires['MemWrite'] = mem_write_signal
        self.control_wires['IRWrite'] = ir_write_signal
        self.control_wires['WDSrc'] = wd_src_signal
        self.control_wires['ImmSrc'] = imm_src_signal
        self.control_wires['ALUControl'] = alu_control_signal
        self.control_wires['ALUSrcB'] = alu_src_b_signal
        self.control_wires['ALUSrcA'] = alu_src_a_signal
        self.control_wires['RegWrite'] = reg_write_signal
        self.control_wires['ZeroFlag'] = zero_signal
        self.control_wires['IOOp'] = io_operation_signal
        self.control_wires['IOInt'] = io_inerrupt_signal

    def do_tick(self) -> None:
        self.tick += 1

        self.PC.do_tick()
        self.Adr_Src_Mux.do_tick()
        self.Memory.do_tick()
        self.IO_Handler.do_tick(self.tick)
        self.IR.do_tick()
        self.WD_Src_Mux.do_tick()
        self.Register_File.do_tick()
        self.Sign_Expand.do_tick()
        self.Alu_Src_A_Mux.do_tick()
        self.Alu_Src_B_Mux.do_tick()
        self.ALU.do_tick()

        self.__log_state()

    def enter_interrupt(self) -> None:
        self.in_interrupt = True
        # Save PC
        prev_pc = self.PC._state
        self.PC._state = self.Register_File._inner_registers[Register.x6]
        self.Register_File._inner_registers[Register.x7] = prev_pc
        # Save ALU Result
        self.Memory._memory[256] = self.ALU.get_register('Result')
        # Save current command
        self.Memory._memory[257] = self.IR._state

    def exit_interrupt(self) -> None:
        self.in_interrupt = False
        # Restore PC
        self.PC._state = self.Register_File._inner_registers[Register.x7]
        # Restore ALU Result
        self.ALU.set_register(
            'Result', self.Memory._memory[256])
        # Restore prev instr
        self.IR._state = self.Memory._memory[257]

    def __log_state(self) -> None:
        msg = (f'Tick №{self.tick})\t' +
               f'PC: {self.PC._state}\t' +
               f'Registers: {[x for x in  self.Register_File._inner_registers.values()]}\t' +
               f'SrcA: {self.ALU.get_register("srcA")} | SrcB: {self.ALU.get_register("srcB")} | Result: {self.ALU.get_register("Result")}\t' +
               f'A1: {self.Register_File.get_register("A1")} | A2: {self.Register_File.get_register("A2")} | A3: {self.Register_File.get_register("A3")}')
        if (self.in_interrupt):
            logging.warning('(Int)' + msg)
        else:
            logging.info(msg)


class ControlUnit(CircuitComponent):

    def __init__(self, is_interrupts_allowed: bool = False) -> None:
        self.__is_interrupts_allowed: bool = is_interrupts_allowed

        self._in_interrupt_context: bool = False
        self._instruction_transitions: Dict[Opcode, List[Dict[str, int]]] = {
            Opcode.ADDI: [{'IRWrite': 1,
                           'ALUSrcB': 1},
                          {'WDSrc': 1, 'RegWrite': 1,
                           'ALUSrcA': 1, 'ALUSrcB': 2, 'ALUControl': 0},
                          {'PCWrite': 1}],
            Opcode.BNE: [{'IRWrite': 1, 'ImmSrc': 2, 'ALUControl': 1},
                         {'IRWrite': 0,
                          'ALUSrcA': 0, 'ALUSrcB': 1, 'ALUControl': 0},
                         {'PCWrite': 1}],
            Opcode.REM: [{'IRWrite': 1, 'ALUControl': 2},
                         {'WDSrc': 1, 'RegWrite': 1,
                          'ALUSrcA': 1, 'ALUSrcB': 2, 'ALUControl': 0},
                         {'PCWrite': 1}],
            Opcode.MUL: [{'IRWrite': 1, 'ALUControl': 3},
                         {'WDSrc': 1, 'RegWrite': 1,
                          'ALUSrcA': 1, 'ALUSrcB': 2, 'ALUControl': 0},
                         {'PCWrite': 1}],
            Opcode.LD: [{'IRWrite': 1, 'ALUSrcB': 1},
                        {'AdrSrc': 1, 'RegWrite': 1, 'IOOp': 1,
                         'ALUSrcA': 1, 'ALUSrcB': 2},
                        {'PCWrite': 1}],
            Opcode.SW: [{'IRWrite': 1, 'ALUSrcB': 1, 'ImmSrc': 2},
                        {'AdrSrc': 1, 'IOOp': 1,
                        'ALUSrcA': 1, 'ALUSrcB': 2, 'ALUControl': 0},
                        {'PCWrite': 1}],
            Opcode.JMP: [{'ALUSrcA': 1, 'ALUSrcB': 1, 'ALUControl': 0},
                         {'PCWrite': 1}],
        }

        super().__init__(['OPCODE', 'PCWrite', 'AdrSrc', 'MemWrite', 'IRWrite', 'WDSrc', 'IOOp',
                          'ImmSrc', 'ALUControl', 'ALUSrcB', 'ALUSrcA', 'RegWrite', 'ZeroFlag', 'IOInt'])

    def start(self, data_path: DataPath = None) -> None:
        self.attach_wires(data_path.control_wires)

        while True:
            self._do_tick(data_path, {'IRWrite': 1})

            opcode = self.get_register('OPCODE')
            if (opcode == Opcode.HALT):
                break

            op_transitions = self.__get_op_transitions(opcode)
            if (op_transitions != None):
                for valves_state in op_transitions:
                    self._do_tick(data_path, valves_state)
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

    def attach_wires(self, wires: Dict[str, CircuitWire]):
        for wire_name, wire in wires.items():
            self.attach(wire_name, wire)

    def _save_context(self) -> Dict[str, int]:
        # Set interrupt mode and receive INT signal
        self._in_interrupt_context = True
        self.set_register('IOInt', 0)

        # Save control unit state
        return self._registers.copy()

    def _restore_context(self, registers: Dict[str, int]) -> None:
        # Restore state after handling interrupt
        self._registers = registers
        self._in_interrupt_context = False

    def _change_valves(self, new_state: Dict[str, int]) -> None:
        for register_name in self._registers.keys():
            # Volatile registers
            if (register_name in ['OPCODE', 'Zero', 'IOInt']):
                continue
            elif (new_state.get(register_name) != None):
                self.set_register(register_name, new_state[register_name])
            else:
                # Set to zero all unused registers to easily handle instructions
                self.set_register(register_name, 0)

    def _do_tick(self, data_path: DataPath, new_state: Dict[str, int] = {}) -> None:
        self._change_valves(new_state)
        data_path.do_tick()
        self.update()
        self.__handle_interrupt(data_path)

    def __handle_interrupt(self, data_path: DataPath) -> None:
        if (self.__is_interrupts_allowed and (not self._in_interrupt_context)
                and self.get_register('IOInt') == 1):
            registers = self._save_context()

            # Goto interrupt vector
            data_path.enter_interrupt()
            # Start executing
            self.start(data_path)
            # Back to prev PC
            data_path.exit_interrupt()

            self._restore_context(registers)

    def __get_op_transitions(self, op: int) -> None | List[Dict[str, int]]:
        return self._instruction_transitions.get(op)


def simulation(program: List[int], text_start_adr: int = 0, is_interrupts_allowed: bool = False,
               memory_size: int = 512) -> None:
    control_unit = ControlUnit(is_interrupts_allowed)
    data_path = DataPath(memory_size)

    data_path.Memory.load_program(program, 0)
    data_path.PC._state = text_start_adr

    interrupt_program = [61452, 7]
    # Interrupt vector address
    data_path.Register_File._inner_registers[6] = 200
    data_path.Memory.load_program(interrupt_program, 200)
    # Interrupt buffer
    # data_path.Register_File._inner_registers[7] = 256

    control_unit.start(data_path)


def main(args):
    logging.basicConfig(level=logging.INFO,
                        filename="py_log.log", filemode="w", format="%(levelname)s %(message)s")

    filename, start_code, is_interrupts_enabled = args

    codes = read_code(filename)

    simulation(codes, int(start_code), is_interrupts_enabled == 'True')

    pass


if __name__ == '__main__':
    main(sys.argv[1:])
