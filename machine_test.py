import unittest
from circuit import CircuitWire
from isa import Opcode
from machine import ControlUnit, DataPath


class ControlUnitTests(unittest.TestCase):
    """
    1) Маскирование опкода
    2) Хальт
    3) Пробежаться по операциям, посмотреть вентили
    4) Подсунуть несуществующую операцию
    5) Чекнуть сохранение контекста прерывания
    6) Чекнуть восстановление контекста прерывания
    """

    def test_DoTick_MaskFirstFourBitsFromOPCODE(self):
        control_unit = ControlUnit()
        opcode_wire = CircuitWire(59)  # 11 (1011) 59
        control_unit.attach('OPCODE', opcode_wire)

        control_unit.update()

        self.assertEqual(control_unit.get_register('OPCODE'), 11)

    def test_DoPerformHaltOp_CalculateNothingAndStop(self):
        control_unit = ControlUnit()
        data_path = DataPath()

        data_path.Memory._memory[0] = 11
        control_unit.start(data_path)

        for register_name, register_val in control_unit._registers.items():
            if (register_name not in ['OPCODE', 'IOInt', 'ZeroFlag', 'IRWrite']):
                self.assertEqual(register_val, 0)

    def test_DoTickWithUndefinedOpcode_ThrowsAssert(self):
        control_unit = ControlUnit()
        control_unit.set_register('OPCODE', 11)

        with self.assertRaises(AttributeError):
            control_unit.start()

    def test_DoSaveContext_SaveAllRegisters(self):
        control_unit = ControlUnit()
        control_unit.set_register('PCWrite', 1)
        control_unit.set_register('IRWrite', 1)
        control_unit.set_register('ALUSrcA', 1)

        registers = control_unit._save_context()

        self.assertEqual(control_unit._in_interrupt_context, True)
        self.assertEqual(registers['PCWrite'], 1)
        self.assertEqual(registers['IRWrite'], 1)
        self.assertEqual(registers['ALUSrcA'], 1)
        self.assertEqual(registers['RegWrite'], 0)
        self.assertEqual(registers['ALUControl'], 0)

    def test_DoRestoreContext_RestoreAllRegisters(self):
        control_unit = ControlUnit()
        control_unit._in_interrupt_context = True
        registers = {
            'PCWrite': 1,
            'IRWrite': 1,
            'ALUSrcA': 1
        }

        control_unit._restore_context(registers)

        self.assertEqual(control_unit._in_interrupt_context, False)
        self.assertEqual(control_unit.get_register('PCWrite'), 1)
        self.assertEqual(control_unit.get_register('IRWrite'), 1)
        self.assertEqual(control_unit.get_register('ALUSrcA'), 1)


class InstructionPerformTests(unittest.TestCase):
    def test_ADDIFirstTick(self):
        """
        Такты ADDI:
        1) Алу слева должна иметь константу, справа должна иметь значение reg2
        2) WD хранит результат суммирование, A3 хранит значение reg1, RegWrite активирован
           Алу слева должна иметь 1, справа должна иметь значение PC
        3) PC, должен иметь значение результата АЛУ
        """
        control_unit = ControlUnit()
        tick_valves = {
            'IRWrite': 1,
            'ALUSrcB': 1
        }

        data_path = DataPath()

        # (0000 101)5 (010)2 (111)7 (0000)ADDI
        data_path.Memory._memory[0] = 5488
        data_path.Register_File._inner_registers[2] = 5

        control_unit.attach_wires(data_path.control_wires)
        control_unit._do_tick(data_path, tick_valves)

        self.assertEquals(data_path.ALU.get_register('srcA'), 5)
        self.assertEquals(data_path.ALU.get_register('srcB'), 5)
        self.assertEquals(data_path.ALU.get_register('Result'), 10)

    def test_ADDISecondTick(self):
        control_unit = ControlUnit()
        tick_valves = {'WDSrc': 1, 'RegWrite': 1,
                       'ALUSrcA': 1, 'ALUSrcB': 2, 'ALUControl': 0}

        data_path = DataPath()

        # (0000 101)5 (010)2 (111)7 (0000)ADDI
        data_path.IR._state = 5488
        data_path.ALU.set_register('Result', 10)

        control_unit.attach_wires(data_path.control_wires)
        control_unit._do_tick(data_path, tick_valves)

        self.assertEquals(data_path.Register_File.get_register('WD'), 10)
        self.assertEquals(data_path.Register_File.get_register('A3'), 7)
        self.assertEquals(data_path.ALU.get_register('srcA'), 0)
        self.assertEquals(data_path.ALU.get_register('srcB'), 1)
        self.assertEquals(data_path.ALU.get_register('Result'), 1)

    def test_ADDIThirdTick(self):
        control_unit = ControlUnit()
        tick_valves = {'PCWrite': 1}

        data_path = DataPath()

        data_path.ALU.set_register('Result', 2)

        control_unit.attach_wires(data_path.control_wires)
        control_unit._do_tick(data_path, tick_valves)

        self.assertEquals(data_path.PC._state, 2)


if __name__ == '__main__':
    unittest.main()
