import sys
from typing import Dict, List, List
from numpy import int16, int8, bitwise_and
from circuit import FunctionalCircuitComponent, WireCircuitComponent

from isa import read_code, Opcode


class DataPath():
    def __init__(self) -> None:
        # Components
        self.pc_triger = Triger()
        self.adr_src_mux = MUX1Bits('AdrSrc')

        self.memory = Memory(300)  # 300 int16 cells
        self.ir_triger = Triger()
        self.wd_src_mux = MUX1Bits('WDSrc')
        self.register_file = RegisterFile()
        self.sign_expand = SignExpand()
        self.alu_src_a_mux = MUX1Bits('ALUSrcA')
        self.alu_src_b_mux = MUX2Bits('ALUSrcB')
        self.alu = ALU()
        self.io_handler = IOHandler()

        # Exit wires for control_unit
        self.control_signals: Dict[str, WireCircuitComponent[int8]] = {}
        self.control_pipes: Dict[str, WireCircuitComponent[int16]] = {}

        # Pipes
        alu_result_pipe = WireCircuitComponent[int16]()
        pc_pipe = WireCircuitComponent[int16]()
        adr_pipe = WireCircuitComponent[int16]()
        rd_pipe = WireCircuitComponent[int16]()
        wd_pipe = WireCircuitComponent[int16]()
        instr_pipe = WireCircuitComponent[int16]()
        rd1_pipe = WireCircuitComponent[int16]()
        rd2_pipe = WireCircuitComponent[int16]()
        ext_imm_pipe = WireCircuitComponent[int16]()
        pc_inc_pipe = WireCircuitComponent[int16]()
        pc_inc_pipe.receive_value(1)
        src_a_pipe = WireCircuitComponent[int16]()
        src_b_pipe = WireCircuitComponent[int16]()

        # Attach pipes
        self.alu.attach_pipe('Result', alu_result_pipe)
        self.pc_triger.attach_pipe('In', alu_result_pipe)
        self.adr_src_mux.attach_pipe('In_1', alu_result_pipe)
        self.wd_src_mux.attach_pipe('In_1', alu_result_pipe)

        self.pc_triger.attach_pipe('Out', pc_pipe)
        self.adr_src_mux.attach_pipe('In_0', pc_pipe)
        self.alu_src_a_mux.attach_pipe('In_1', pc_pipe)
        self.register_file.attach_pipe('PC', pc_pipe)

        self.adr_src_mux.attach_pipe('Out', adr_pipe)
        self.memory.attach_pipe('A', adr_pipe)
        self.io_handler.attach_pipe('In', adr_pipe)

        self.memory.attach_pipe('RD', rd_pipe)
        self.ir_triger.attach_pipe('In', rd_pipe)
        self.wd_src_mux.attach_pipe('In_0', rd_pipe)
        self.io_handler.attach_pipe('Out', rd_pipe)
        self.control_pipes = {'OPCODE': rd_pipe}

        self.wd_src_mux.attach_pipe('Out', wd_pipe)
        self.register_file.attach_pipe('WD', wd_pipe)

        self.ir_triger.attach_pipe('Out', instr_pipe)
        self.register_file.attach_pipe('A1', instr_pipe)
        self.register_file.attach_pipe('A2', instr_pipe)
        self.register_file.attach_pipe('A3', instr_pipe)
        self.sign_expand.attach_pipe('In', instr_pipe)

        self.register_file.attach_pipe('RD1', rd1_pipe)
        self.alu_src_a_mux.attach_pipe('In_0', rd1_pipe)

        self.register_file.attach_pipe('RD2', rd2_pipe)
        self.alu_src_b_mux.attach_pipe('In_00', rd2_pipe)
        self.memory.attach_pipe('WD', rd2_pipe)
        self.io_handler.attach_pipe('WD', rd2_pipe)

        self.sign_expand.attach_pipe('Out', ext_imm_pipe)
        self.alu_src_b_mux.attach_pipe('In_01', ext_imm_pipe)

        self.alu_src_b_mux.attach_pipe('In_10', pc_inc_pipe)

        self.alu_src_a_mux.attach_pipe('Out', src_a_pipe)
        self.alu.attach_pipe('srcA', src_a_pipe)

        self.alu_src_b_mux.attach_pipe('Out', src_b_pipe)
        self.alu.attach_pipe('srcB', src_b_pipe)

        # Signals
        pc_write_signal = WireCircuitComponent[int8]()
        adr_src_signal = WireCircuitComponent[int8]()
        mem_write_signal = WireCircuitComponent[int8]()
        ir_write_signal = WireCircuitComponent[int8]()
        wd_src_signal = WireCircuitComponent[int8]()
        imm_src_signal = WireCircuitComponent[int8]()
        alu_control_signal = WireCircuitComponent[int8]()
        alu_src_b_signal = WireCircuitComponent[int8]()
        alu_src_a_signal = WireCircuitComponent[int8]()
        reg_write_signal = WireCircuitComponent[int8]()
        zero_signal = WireCircuitComponent[int8]()
        io_operation_signal = WireCircuitComponent[int8]()
        io_inerrupt_signal = WireCircuitComponent[int8]()

        # Attach signals
        self.control_signals['PCWrite'] = pc_write_signal
        self.control_signals['PCWrite'] = pc_write_signal
        self.control_signals['AdrSrc'] = adr_src_signal
        self.control_signals['MemWrite'] = mem_write_signal
        self.control_signals['IRWrite'] = ir_write_signal
        self.control_signals['WDSrc'] = wd_src_signal
        self.control_signals['ImmSrc'] = imm_src_signal
        self.control_signals['ALUControl'] = alu_control_signal
        self.control_signals['ALUSrcB'] = alu_src_b_signal
        self.control_signals['ALUSrcA'] = alu_src_a_signal
        self.control_signals['RegWrite'] = reg_write_signal
        self.control_signals['Zero'] = zero_signal
        self.control_signals['IOOp'] = io_operation_signal
        self.control_signals['IOInt'] = io_inerrupt_signal

        self.pc_triger.attach_signal(pc_write_signal)
        self.adr_src_mux.attach_signal(adr_src_signal)
        self.memory.attach_signal(mem_write_signal)
        self.ir_triger.attach_signal(ir_write_signal)
        self.wd_src_mux.attach_signal(wd_src_signal)
        self.sign_expand.attach_signal(imm_src_signal)
        self.register_file.attach_signal(reg_write_signal)
        self.alu_src_a_mux.attach_signal(alu_src_a_signal)
        self.alu_src_b_mux.attach_signal(alu_src_b_signal)
        self.alu.attach_signal('ALUControl', alu_control_signal)
        self.alu.attach_signal('Zero', zero_signal)
        self.io_handler.attach_signal('IOOp', io_operation_signal)
        self.io_handler.attach_signal('IOInt', io_inerrupt_signal)
        # remind zero flag in alu

        self.tick = 0
        pass

    def do_tick(self) -> None:
        self.tick += 1

        self.pc_triger.do_tick()
        self.adr_src_mux.do_tick()
        self.memory.do_tick()
        self.io_handler.do_tick(self.tick)
        self.ir_triger.do_tick()
        self.wd_src_mux.do_tick()
        self.register_file.do_tick()
        self.sign_expand.do_tick()
        self.alu_src_a_mux.do_tick()
        self.alu_src_b_mux.do_tick()
        self.alu.do_tick()

        self.get_info(self.tick)

    def save_pc(self) -> None:
        self.register_file.inner_registers[4] = self.pc_triger.state
        self.pc_triger.state = self.register_file.inner_registers[5]

    def load_pc(self) -> None:
        self.pc_triger.state = self.register_file.inner_registers[4]

    def get_info(self, tick: int) -> Dict[str, int]:
        print(str(tick), ')', sep='', end=' ')
        for register_name, register_value in self.register_file.inner_registers.items():
            print('x' + str(register_name), register_value, sep=' : ', end=' | ')
        print('\nAluSrcA :', self.alu.get_value('srcA'), '|', 'ALUSrcB :', self.alu.get_value(
            'srcB'), '|', 'Result :', self.alu.get_value('Result'), '|', sep=' ', end=' ')
        print('PC :', self.pc_triger.state)


class ControlUnit():
    def __init__(self, interrupt_flag: bool) -> None:
        registers: List[str] = ['OPCODE']
        inputs: List[str] = ['PCWrite', 'AdrSrc', 'MemWrite', 'IRWrite', 'WDSrc', 'IOOp',
                             'ImmSrc', 'ALUControl', 'ALUSrcB', 'ALUSrcA', 'RegWrite', 'Zero', 'IOInt']

        self.__registers: Dict[str, int16] = {i: 0 for i in registers}
        self.__inputs: Dict[str, int8] = {i: 0 for i in inputs}

        self.__pipes: Dict[str, WireCircuitComponent[int16]] = dict()
        self.__signals: Dict[str, WireCircuitComponent[int8]] = dict()

        self.interrupt_flag = interrupt_flag
        self.in_inerrupt = False

    def start(self, data_path: DataPath) -> bool:
        while True:
            # 1 tick
            self.__reset_inputs()
            data_path.do_tick()
            self.__refresh_state()
            self.__handle_interrupt(data_path)
            if (data_path.pc_triger.state == 206):
                pass

            match self.__registers.get('OPCODE'):
                case Opcode.ADDI:
                    # 2 tick
                    self.__set_inputs({
                        'IRWrite': 1, 'ALUSrcB': 1  # Sum reg and imm_ext
                    })
                    data_path.do_tick()
                    self.__handle_interrupt(data_path)

                    # 3 tick
                    self.__set_inputs({
                        # Write sum in reg[a3]
                        'WDSrc': 1, 'IRWrite': 0, 'RegWrite': 1,
                        'ALUSrcA': 1, 'ALUSrcB': 2, 'ALUControl': 0  # Inc PC
                    })
                    data_path.do_tick()
                    self.__handle_interrupt(data_path)

                    # 4 tick
                    self.__set_inputs({
                        'RegWrite': 0,  # Disable write to register file from prev tick
                        'PCWrite': 1,  # Update PC value
                    })
                    data_path.do_tick()
                    self.__handle_interrupt(data_path)

                case Opcode.BNE:
                    # 2 tick
                    self.__set_inputs({
                        'IRWrite': 1, 'ImmSrc': 2, 'ALUControl': 1  # Sub reg1 and reg2
                    })
                    data_path.do_tick()
                    self.__receive_signal('Zero')
                    self.__handle_interrupt(data_path)

                    if (self.__get_input('Zero') == 0):
                        # 3 tick
                        self.__set_inputs({
                            # Not save new state in register file[a3]
                            'IRWrite': 0,
                            'ALUSrcA': 0, 'ALUSrcB': 1, 'ALUControl': 0  # RD1 + Imm
                        })
                        data_path.do_tick()
                        self.__handle_interrupt(data_path)

                        # 4 tick
                        self.__set_inputs({
                            'PCWrite': 1,  # Update PC value
                        })
                        data_path.do_tick()
                        self.__handle_interrupt(data_path)
                    else:
                        # 3 tick
                        self.__set_inputs({
                            'ALUSrcA': 1, 'ALUSrcB': 2, 'ALUControl': 0  # Inc PC
                        })
                        data_path.do_tick()
                        self.__handle_interrupt(data_path)

                        # 4 tick
                        self.__set_inputs({
                            'PCWrite': 1,  # Update PC value
                        })
                        data_path.do_tick()
                        self.__handle_interrupt(data_path)

                case Opcode.REM:
                    # 2 tick
                    self.__set_inputs({
                        'IRWrite': 1, 'ImmSrc': 1, 'ALUControl': 2  # Rem reg2 and reg3
                    })
                    data_path.do_tick()
                    self.__handle_interrupt(data_path)

                    # 3 tick
                    self.__set_inputs({
                        # Write rem in reg[a3]
                        'WDSrc': 1, 'IRWrite': 0, 'RegWrite': 1,
                        'ALUSrcA': 1, 'ALUSrcB': 2, 'ALUControl': 0  # Add PC + ALURes
                    })
                    data_path.do_tick()
                    self.__handle_interrupt(data_path)

                    # 4 tick
                    self.__set_inputs({
                        'RegWrite': 0,
                        'PCWrite': 1  # Update PC value
                    })
                    data_path.do_tick()
                    self.__handle_interrupt(data_path)

                case Opcode.LD:
                    # 2 tick
                    self.__set_inputs({
                        'IRWrite': 1, 'ALUSrcB': 1  # Sum reg and imm_ext
                    })
                    data_path.do_tick()
                    self.__handle_interrupt(data_path)

                    # 3 tick
                    self.__set_inputs({
                        # Read mem[reg+imm] in register
                        'AdrSrc': 1, 'IRWrite': 0, 'RegWrite': 1, 'IOOp': 1,
                        'ALUSrcA': 1, 'ALUSrcB': 2, 'ALUControl': 0  # Inc PC
                    })
                    data_path.do_tick()
                    self.__handle_interrupt(data_path)

                    # 4 tick
                    self.__set_inputs({
                        'RegWrite': 0,  # Disable write to register file from prev tick
                        'PCWrite': 1,  # Update PC value
                        'IOOp': 0
                    })
                    data_path.do_tick()
                    self.__handle_interrupt(data_path)

                case Opcode.SW:
                    # 2 tick
                    self.__set_inputs({
                        'IRWrite': 1, 'ALUSrcB': 1, 'ImmSrc': 2  # Sum reg and imm_ext
                    })
                    data_path.do_tick()
                    self.__handle_interrupt(data_path)

                    # 3 tick
                    self.__set_inputs({
                        # Write mem[reg+imm] from register
                        'AdrSrc': 1, 'IRWrite': 0, 'IOOp': 1,
                        'ALUSrcA': 1, 'ALUSrcB': 2, 'ALUControl': 0  # Inc PC
                    })
                    data_path.do_tick()
                    self.__handle_interrupt(data_path)

                    # 4 tick
                    self.__set_inputs({
                        'MemWrite': 0,  # Disable write to register file from prev tick
                        'PCWrite': 1,  # Update PC value
                        'IOOp': 0
                    })
                    data_path.do_tick()
                    self.__handle_interrupt(data_path)

                case Opcode.JMP:
                    # 3 tick
                    self.__set_inputs({
                        'ALUSrcA': 1, 'ALUSrcB': 1, 'ALUControl': 0  # PC + ALURes
                    })
                    data_path.do_tick()
                    self.__handle_interrupt(data_path)

                    # 4 tick
                    self.__set_inputs({
                        'PCWrite': 1,  # Update PC value
                    })
                    data_path.do_tick()
                    self.__handle_interrupt(data_path)

                case Opcode.HALT:
                    break

                case _:
                    print("Unsupported control unit operation: " +
                          self.__registers.get('OPCODE'))
                    pass

    def __handle_interrupt(self, data_path: DataPath) -> None:
        self.__receive_signal('IOInt')

        if (self.interrupt_flag and (not self.in_inerrupt) and self.__get_input('IOInt')):
            self.in_inerrupt = True
            self.__set_input('IOInt', 0)

            pc = data_path.pc_triger.state
            data_path.pc_triger.state = data_path.register_file.inner_registers[5]

            registers = self.__registers.copy()
            inputs = self.__inputs.copy()
            self.start(data_path)
            self.__registers = registers
            self.__inputs = inputs

            data_path.pc_triger.state = pc
            self.in_inerrupt = False
            pass

    def attach_pipes(self, pipes: Dict[str, WireCircuitComponent]) -> None:
        for register_name, pipe in pipes.items():
            if register_name in self.__registers.keys():
                self.__pipes[register_name] = pipe
        pass

    def attach_signals(self, signals: Dict[str, WireCircuitComponent]) -> None:
        for input_name, signal in signals.items():
            if input_name in self.__inputs.keys():
                self.__signals[input_name] = signal
        pass

    def __reset_inputs(self):
        for input in self.__inputs.keys():
            self.__set_input(input, 0)

    def __set_inputs(self, inputs: Dict[str, int8]):
        for input_name, input_val in inputs.items():
            self.__set_input(input_name, input_val)

    def __set_input(self, input_name: str, val: int8) -> None:
        assert input_name in self.__inputs.keys(), 'Указанный выход не существует'
        self.__inputs[input_name] = val

        signal = self.__signals.get(input_name)
        if (signal != None):
            signal.receive_value(val)
        pass

    def __get_input(self, input_name: str) -> None:
        assert input_name in self.__inputs.keys(), 'Указанный выход не существует'
        return self.__inputs[input_name]

    def __receive_signal(self, input_name: str) -> None:
        assert input_name in self.__inputs.keys(), 'Указанный выход не существует'

        signal = self.__signals.get(input_name)
        if (signal != None):
            self.__inputs[input_name] = signal.get_value()

        pass

    def __refresh_state(self) -> None:
        self.__receive_value('OPCODE', 7)

        self.__receive_signal('Zero')
        self.__receive_signal('IOInt')

    def __receive_value(self, register_name: str, mask: int16) -> None:
        assert register_name in self.__registers.keys(), 'Указанный регистр не существует'
        self.__registers[register_name] = bitwise_and(
            self.__pipes[register_name].get_value(), mask
        )
        pass


def simulation(start_code: int16, codes: List[int16], interrupt_flag: bool) -> None:
    control_unit = ControlUnit(interrupt_flag)
    data_path = DataPath()

    control_unit.attach_signals(data_path.control_signals)
    control_unit.attach_pipes(data_path.control_pipes)

    data_path.memory.load_program(codes, 0)
    data_path.pc_triger.state = start_code

    interrupt_program = [96, 3524, 61467, 499, 264, 6]

    data_path.register_file.inner_registers[5] = 200
    data_path.memory.load_program(interrupt_program, 200)

    data_path.register_file.inner_registers[7] = 256

    # Цвиллинга 28 21 окт 2002 - декабрь 2002
    # Проспект Ленина 67 143 2003
    # Пустового 15 5

    control_unit.start(data_path)


def main(args):
    # filename = 'examples/prob5.out'
    # filename = 'examples/cat.out'

    filename, start_code, is_interrupts_enabled = [
        'examples/hello.out', 8, True]

    codes = read_code(filename)

    simulation(start_code, codes, is_interrupts_enabled)
    pass


if __name__ == '__main__':
    main(sys.argv[1:])
