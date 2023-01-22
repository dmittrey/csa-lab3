import unittest
from components import Register, SignExpand, Trigger, Memory, RegisterFile, ALU, MUX, IOHandler, IOMemoryCell
from circuit import CircuitWire


class TriggerTests(unittest.TestCase):
    def test_DoTickWithEnSignal_GetStateFromInputValue(self):
        trigger = Trigger()

        trigger.set_register('In', 5)
        trigger.set_register('EN', 1)
        trigger.do_tick()

        self.assertEqual(trigger._state, 5)

    def test_DoTickWithoutEnSignal_NotGetStateFromInputValue(self):
        trigger = Trigger()

        trigger.set_register('In', 5)
        trigger.set_register('EN', 0)
        trigger.do_tick()

        self.assertEqual(trigger._state, 0)

    def test_DoTick_GetOutputValueFromState(self):
        trigger = Trigger()

        trigger._state = 5
        trigger.do_tick()

        self.assertEqual(trigger.get_register('Out'), 5)


class MemoryTests(unittest.TestCase):
    """
    1) Создали с отрицательным кол-вом памяти
    2) Адресовались мимо памяти
    3) Если WE == 1 то записать в память
    4) Если WE == 0 то прочитать в RD
    5) Загрузили программу в память
    6) Загрузили программу мимо памяти
    """

    def test_InitMemoryWithNegativeCellsAmount_ThrowsAssert(self):
        with self.assertRaises(AssertionError):
            Memory(-2)

    def test_AddressOutOfMemory_ThrowsAssert(self):
        memory = Memory(5)

        memory.set_register('A', 7)

        with self.assertRaises(AssertionError):
            memory.do_tick()

    def test_DoTickWithWeSignal_FillMemoryFromWdValue(self):
        memory = Memory(5)
        memory.set_register('A', 3)
        memory.set_register('WD', 5)
        memory.set_register('WE', 1)

        memory.do_tick()

        self.assertEqual(memory._memory[3], 5)

    def test_DoTickWithoutWeSignal_GetRdValueFromMemory(self):
        memory = Memory(5)
        memory._memory[3] = 5
        memory.set_register('A', 3)
        memory.set_register('WE', 0)

        memory.do_tick()

        self.assertEqual(memory.get_register('RD'), 5)

    def test_LoadSameProgram_Calculate(self):
        memory = Memory(5)
        program = [6]

        memory.load_program(program, 0)

        self.assertEqual(memory._memory[0], 6)

    def test_LoadSameProgramOutOfMemory_ThrowsAssert(self):
        memory = Memory(5)
        program = [6]

        with self.assertRaises(AssertionError):
            memory.load_program(program, 5)


class RegisterFileTests(unittest.TestCase):
    """
    1) Проверить маскирование
    2) Без сигнала WE3 посмотреть вывод RD1, RD2
    3) С сигналом WE3 записать в нулевой регистр
    4) С сигналом WE3 записать в другой регистр
    5) С сигналом WE3 записать в PC регистр
    6) Вход в прерывание
    """

    def test_DoTick_ReceiveMaskedValues(self):
        register_file = RegisterFile()
        register_file.attach('A1', CircuitWire(880))   # 1 (101) 110 000
        register_file.attach('A2', CircuitWire(6985))  # 1 (101) 101 001 001
        register_file.attach('A3', CircuitWire(109))   # 1 (101) 101

        register_file.do_tick()

        self.assertEqual(register_file.get_register('A1'), 5)
        self.assertEqual(register_file.get_register('A2'), 5)
        self.assertEqual(register_file.get_register('A3'), 5)

    def test_DoTickWithoutWe3Signal_GetRDValuesFromRegisters(self):
        register_file = RegisterFile()
        register_file.set_register('A1', 7)
        register_file._inner_registers[7] = 20
        register_file.set_register('A2', 5)
        register_file._inner_registers[5] = 10

        register_file.do_tick()

        self.assertEqual(register_file.get_register('RD1'), 20)
        self.assertEqual(register_file.get_register('RD2'), 10)

    def test_WriteInZeroRegister_GetNoImpact(self):
        register_file = RegisterFile()
        register_file.set_register('A3', 0)
        register_file.set_register('WD', 5)
        register_file.set_register('WE3', 1)

        register_file.do_tick()

        self.assertEqual(register_file._inner_registers[0], 0)

    def test_WriteInNonZeroRegister_Calculate(self):
        register_file = RegisterFile()
        register_file.set_register('A3', 3)
        register_file.set_register('WD', 5)
        register_file.set_register('WE3', 1)

        register_file.do_tick()

        self.assertEqual(register_file._inner_registers[3], 5)

    def test_WriteInFirstRegister_ChangePCWireAndPCRegister(self):
        register_file = RegisterFile()
        register_file.set_register('A3', 1)
        register_file.set_register('WD', 5)
        register_file.set_register('WE3', 1)
        pc_wire = CircuitWire()
        register_file.attach('PC', pc_wire)

        register_file.do_tick()

        self.assertEqual(pc_wire.get(), 5)
        self.assertEqual(register_file.get_register('PC'), 5)

    def test_EnterInterrupt_GetPCRegisterValueFromX5Register(self):
        register_file = RegisterFile()
        register_file._inner_registers[Register.x5] = 5

        register_file.enter_interrupt()

        self.assertEqual(register_file.get_register('PC'), 5)


class ALUTests(unittest.TestCase):
    """
    1) Проверка SUM
    2) Проверка SUB
    3) Проверка REM
    4) Проверка неподдерживаемой операции
    5) Нулевой результат
    6) Ненулевой после нулевого
    """

    def test_ALUControlIsZero_CalculateSum(self):
        alu = ALU()
        alu.set_register('srcA', 5)
        alu.set_register('srcB', 10)
        alu.set_register('ALUControl', 0)

        alu.do_tick()

        self.assertEqual(alu.get_register('Result'), 15)

    def test_ALUControlIsOne_CalculateSub(self):
        alu = ALU()
        alu.set_register('srcA', 5)
        alu.set_register('srcB', 10)
        alu.set_register('ALUControl', 1)

        alu.do_tick()

        self.assertEqual(alu.get_register('Result'), -5)

    def test_ALUControlIsTwo_CalculateRem(self):
        alu = ALU()
        alu.set_register('srcA', 5)
        alu.set_register('srcB', 10)
        alu.set_register('ALUControl', 2)

        alu.do_tick()

        self.assertEqual(alu.get_register('Result'), 5)

    def test_ALUControlIsThree_ThrowsAssert(self):
        alu = ALU()
        alu.set_register('ALUControl', 3)

        with self.assertRaises(AssertionError):
            alu.do_tick()

    def test_ResultIsZero_ZeroFlagIsActive(self):
        alu = ALU()
        alu.set_register('ALUControl', 0)

        alu.do_tick()

        self.assertEqual(alu.get_register('ZeroFlag'), 1)

    def test_ResultNonZeroAfterZeroResult_ZeroFlagNotIsActive(self):
        alu = ALU()
        alu.set_register('ALUControl', 0)

        alu.do_tick()
        alu.set_register('srcA', 5)
        alu.do_tick()

        self.assertEqual(alu.get_register('ZeroFlag'), 0)


class SignExapndTests(unittest.TestCase):
    """
    1) Проверка расширения 9-15 бит
    2) Проверка расширения 12-15 бит
    3) Проверка расширения 12-15 и 3-5 бит
    4) Проверка неподдерживаемой операции
    """

    def test_DoTickWithImmSrcZero_GetSevenBiggestBits(self):
        sign_expand = SignExpand()
        sign_expand.set_register('ImmSrc', 0)
        sign_expand.set_register('In', 33664)  # (1000 001) 110 000 000 33664

        sign_expand.do_tick()

        self.assertEqual(sign_expand.get_register('Out'), 65)

    def test_DoTickWithImmSrcOne_GetFourBiggestBits(self):
        sign_expand = SignExpand()
        sign_expand.set_register('ImmSrc', 1)
        sign_expand.set_register('In', 40832)  # (1001) 111 110 000 000 40832

        sign_expand.do_tick()

        self.assertEqual(sign_expand.get_register('Out'), 9)

    def test_DoTickWithImmSrcSecond_GetFourBiggestBitsAndThreeInMiddle(self):
        sign_expand = SignExpand()
        sign_expand.set_register('ImmSrc', 2)
        sign_expand.set_register('In', 39036)  # (1001) 100 001 (111) 100 39036

        sign_expand.do_tick()

        self.assertEqual(sign_expand.get_register('Out'), 79)

    def test_DoTickWithUnsupportedImmSrc_ThrowsAssert(self):
        sign_expand = SignExpand()
        sign_expand.set_register('ImmSrc', 3)

        with self.assertRaises(AssertionError):
            sign_expand.do_tick()


class Mux1BitTests(unittest.TestCase):
    """
    1) Тик с инпутом в 0
    2) Тик с инпутом в 1
    """

    def test_DoTickWithInputEqualsZero_SaveIn0ToOut(self):
        mux = MUX(1)
        mux.set_register('In_0', 10)
        mux.set_register('In_1', 20)
        mux.set_register('Src', 0)

        mux.do_tick()

        self.assertEqual(mux.get_register('Out'), 10)

    def test_DoTickWithInputEqualsOne_SaveIn1ToOut(self):
        mux = MUX(1)
        mux.set_register('In_0', 10)
        mux.set_register('In_1', 20)
        mux.set_register('Src', 1)

        mux.do_tick()

        self.assertEqual(mux.get_register('Out'), 20)


class Mux2BitsTests(unittest.TestCase):
    """
    1) Тик с инпутом в 00
    2) Тик с инпутом в 01
    3) Тик с инпутом в 10
    4) Тик с инпутом в 11
    """

    def test_DoTickWithInputEqualsZero_SaveIn00ToOut(self):
        mux = MUX(2)
        mux.set_register('In_00', 10)
        mux.set_register('In_01', 20)
        mux.set_register('In_10', 30)
        mux.set_register('In_11', 40)
        mux.set_register('Src', 0)

        mux.do_tick()

        self.assertEqual(mux.get_register('Out'), 10)

    def test_DoTickWithInputEqualsOne_SaveIn01ToOut(self):
        mux = MUX(2)
        mux.set_register('In_00', 10)
        mux.set_register('In_01', 20)
        mux.set_register('In_10', 30)
        mux.set_register('In_11', 40)
        mux.set_register('Src', 1)

        mux.do_tick()

        self.assertEqual(mux.get_register('Out'), 20)

    def test_DoTickWithInputEqualsTwo_SaveIn10ToOut(self):
        mux = MUX(2)
        mux.set_register('In_00', 10)
        mux.set_register('In_01', 20)
        mux.set_register('In_10', 30)
        mux.set_register('In_11', 40)
        mux.set_register('Src', 2)

        mux.do_tick()

        self.assertEqual(mux.get_register('Out'), 30)

    def test_DoTickWithInputEqualsThree_SaveIn11ToOut(self):
        mux = MUX(2)
        mux.set_register('In_00', 10)
        mux.set_register('In_01', 20)
        mux.set_register('In_10', 30)
        mux.set_register('In_11', 40)
        mux.set_register('Src', 3)

        mux.do_tick()

        self.assertEqual(mux.get_register('Out'), 40)


class IOHandlerTests(unittest.TestCase):
    """
    1) Проверить на прерывание на тик
    2) Чтение на IOOp выдает dip_value на Out
    3) Запись на IOOp выдает WD на dip_value
    4) Чтение без IOOp ошибка
    5) Запись без IOOp ошибка
    6) Записать два значения и проверить буффер
    """

    def test_DoTickWithInterruptToken_ActivateIOIntRegisterAndFillDip(self):
        io_handler = IOHandler([(1, 'a')])

        io_handler.do_tick(1)

        self.assertEqual(io_handler.get_register('IOInt'), 1)
        self.assertEqual(io_handler._dip_value, ord('a'))

    def test_DoTickWithActiveIOOpFromReadMemoryCell_SetDipValueToOutRegister(self):
        io_handler = IOHandler([])
        io_handler._dip_value = ord('a')
        io_handler.set_register('IOOp', 1)
        io_handler.set_register('In', IOMemoryCell.IN)
        io_handler.set_register('WD', ord('b'))

        io_handler.do_tick(1)

        self.assertEqual(io_handler.get_register('IOInt'), 0)
        self.assertEqual(io_handler.get_register('Out'), ord('a'))
        self.assertEqual(io_handler._dip_value, ord('a'))

    def test_DoTickWithActiveIOOpFromWriteMemoryCell_SetWDRegisterValueToDipValue(self):
        io_handler = IOHandler([])
        io_handler._dip_value = ord('a')
        io_handler.set_register('IOOp', 1)
        io_handler.set_register('In', IOMemoryCell.OUT)
        io_handler.set_register('WD', ord('b'))

        io_handler.do_tick(1)

        self.assertEqual(io_handler.get_register('IOInt'), 0)
        self.assertEqual(io_handler.get_register('Out'), 0)
        self.assertEqual(io_handler._dip_value, ord('b'))

    def test_DoTickWithoutActiveIOOpFromReadMemoryCell_ThrowsAssert(self):
        io_handler = IOHandler([])
        io_handler._dip_value = ord('a')
        io_handler.set_register('IOOp', 0)
        io_handler.set_register('In', IOMemoryCell.IN)
        io_handler.set_register('WD', ord('b'))

        with self.assertRaises(AttributeError):
            io_handler.do_tick(1)

    def test_DoTickWithoutActiveIOOpFromWriteMemoryCell_ThrowsAssert(self):
        io_handler = IOHandler([])
        io_handler._dip_value = ord('a')
        io_handler.set_register('IOOp', 0)
        io_handler.set_register('In', IOMemoryCell.OUT)
        io_handler.set_register('WD', ord('b'))

        with self.assertRaises(AttributeError):
            io_handler.do_tick(1)

    def test_WriteTwoValues_BufferIncludeTwoChars(self):
        io_handler = IOHandler([])
        io_handler.set_register('IOOp', 1)
        io_handler.set_register('In', IOMemoryCell.OUT)
        io_handler.set_register('WD', ord('b'))

        io_handler.do_tick(1)
        io_handler.do_tick(2)

        self.assertEqual(io_handler._saved_tokens, ['b', 'b'])


if __name__ == '__main__':
    unittest.main()
