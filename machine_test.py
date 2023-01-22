import unittest
from circuit import CircuitWire

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

    def test_DoTick_MaskFirstThreeBitsFromOPCODE(self):
        control_unit = ControlUnit()
        opcode_wire = CircuitWire(29)  # 11 (101) 29
        control_unit.attach('OPCODE', opcode_wire)

        control_unit.update()

        self.assertEqual(control_unit.get_register('OPCODE'), 5)

    def test_DoPerformHaltOp_CalculateNothingAndStop(self):
        control_unit = ControlUnit()
        opcode_wire = CircuitWire(6)
        control_unit.attach('OPCODE', opcode_wire)

        control_unit.start()

        for register_val in control_unit._registers.values():
            self.assertEqual(register_val, 0)

    def test_DoTickWithUndefinedOpcode_ThrowsAssert(self):
        control_unit = ControlUnit()
        opcode_wire = CircuitWire(7)
        control_unit.attach('OPCODE', opcode_wire)

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


if __name__ == '__main__':
    unittest.main()
