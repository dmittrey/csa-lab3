# Зубахин Дмитрий, P33312

Virtual machine and interpreter

# Описание задачи

- **_asm_** - синтаксис ассемблера. Необходима поддержка label-ов.
- **_risc_** - система команд должна быть упрощенной, в духе RISC архитектур.
- **_neum_** - фон Неймановская архитектура.
- **_hw_** - hardwired. Control Unit реализуется как часть модели.
- **_instr_** -- процессор необходимо моделировать с точностью до каждой инструкции (наблюдается состояние после каждой инструкции).
- **_struct_** -- в виде высокоуровневой структуры данных. Считается, что одна инструкция укладывается в одно машинное слово, за исключением CISC архитектур.
- **_trap_** -- Ввод-вывод осуществляется токенами через систему прерываний.
- **_mem_** -- memory mapped output

# Язык программирования

## Описание синтаксиса языка

```ebnf
<letter> ::= [a-z] | [A-Z]
<digit> ::= [0-9]
<digit_list> ::= <digit> | <digit> <digit_list>
<digit_or_letter> ::= <letter> | <digit>
<digit_or_letter_list> ::= <sign> | <sign> <digit_or_letter_list>
<identifier> ::= <letter> | <letter> <digit_or_letter_list>
<sign> ::= "-" | "+"
<comment> ::= ";" <digit_or_letter_list>

<register> ::= "ZR" | "mtvec" | "mepc" | x[3-6]
<immediate> ::= <digit_list>
<shift> ::= <sign> <immediate> "(" <register> ")"

<no_args_op> ::= "halt"
<one_args_op> ::= "jmp" | "jg" | "bne" | "beq"
<two_args_op> ::= "ld" | "sw" | "cmp"
<three_arg_op> ::= "addi" | "add" | "rem" | "mul"

<one_args_instr> ::= <one_args_op> <identifier>
<two_args_instr> ::= <two_arg_op> <register> <shift> | <two_arg_op> <register> <immediate>
<three_args_instr> ::= <three_arg_op> <register> <register> <immediate> | <three_arg_op> <register> <register>

<instruction> ::= <no_args_op> <comment> | <one_args_op> <comment> | <two_args_instr> <comment> | <three_args_instr> <comment> | <comment>
<label> ::= <identifier>
<program_line> ::= <label> <instruction> | <label> | <instruction>
<program_line_list> ::= <program_line> | <program_line> <program_line_list>

<section> ::= "section" <identifier> <program_line_list>
<section_list> ::=  <section> | <section> <section_list>
<program> ::= <section_list>
```

## Описание семантики

### Метки

- `label:` - метка (для выполнения иструкций перехода).
- `_start:` - обязательная метка, сигнализирующая начало программы, может находиться где угодно, главное чтобы указывала на инструкцию.
- На одни и те же инструкции (команды и данные) могут быть указаны несколько меток, однако метки не могут дублироваться, и одни и те же метки указывать на разные инструкции.
- Область видимости глобальная.

### Секции

- `section <name>` - создать секцию с именем `<name>`. Данные внутри секций идут последовательно.
- `.text` - секция для кода
- `.data` - секция для данных

# Организация памяти

## Работа с памятью

- Память одна на команды и данные(согласно варианту). Память адресуется с помощью 17-битного адреса.
- При попытке исполнить данные как инструкцию программа падает с ошибкой.
- Scope в языке глобальный.

## Модель памяти

- Размер машинного слова 16 бит. Адресация абсолютная.
- Структура памяти неоднородная, первые 32 ячейки зарезервированы под устройства ввода-вывода.
- Пользователю доступны 6 регистров(остальные два - CSR регистры)

| Название регистра | Алиас | Назначение                |
| ----------------- | ----- | ------------------------- |
| x0                | ZR    | Регистр всегда хранит 0   |
| x1                | -     | Регистр общего назначения |
| x2                | -     | Регистр общего назначения |
| x3                | -     | Регистр общего назначения |
| x4                | -     | Регистр общего назначения |
| x5                | -     | Регистр общего назначения |
| x6                | mtvec | Interrupt vector address  |
| x7                | mepc  | Previous PC value         |

## Отображение на модель памяти процессора

```text
     Memory (for data and instructions)
+----------------------------------+
|    ...                           |
| 0x00: var1                       |
| 0x20: var2                       |
| 0x40: cmd1                       |
| 0x60: cmd2                       |
|    ...                           |
| mtvec_val interruption handler 0 |
|    ...                           |
+----------------------------------+
```

Инструкции и данные не перемешиваются(сначала данные, потом инструкции). Обработчик прерывания размещается в последних 4 машинных словах.

# Система команд

## Особенности процессора

- Машинное слово -- 17 бит, знаковое.
- Память данных и команд:

  - Адресуется через DR.
  - Адрес следующей команды хранится в аккумуляторе
  - Регистр x0 не может изменятся, там статично лежит значение 0.

- Ввод-вывод - memory-mapped. Ячейки 120, 121 зарезервированы под внешние устройства.
- Program_counter - счетчик команд. Инкрементируется с каждой инструкцией, может быть перезаписан командой перехода.
- Прерываний есть, состояние PC, ALUResult, и состояние шины инструкции сохраняется . После обработки прерывания работа программы возобновляется.
- Машина поддерживает только абсолютную адресацию.
- Присутствует флаг Z (zero) для команд перехода.

## Набор инструкций

| №   | Тип команды | Название команды     | Назначение                      | 4 бит    | 3 бит    | 3 бит | 3 бит    | 4 бит  |
| --- | ----------- | -------------------- | ------------------------------- | -------- | -------- | ----- | -------- | ------ |
| 0   | Type B      | ADDI reg1, reg2, IMM | reg1 = reg2 + IMM               | IMM[6:3] | IMM[2:0] | reg2  | reg1     | OPCODE |
| 1   | Type A      | ADD reg1, reg2, reg3 | reg1 = reg2 + reg3              |          | reg3     | reg2  | reg1     | OPCODE |
| 2   | Type A      | REM reg1, reg2, reg3 | reg1 = reg2 % reg3              |          | reg3     | reg2  | reg1     | OPCODE |
| 3   | Type A      | MUL reg1, reg2, reg3 | reg1 = reg2 \* reg3             |          | reg3     | reg2  | reg1     | OPCODE |
| 4   | Type B      | LD reg1, IMM(reg2)   | reg1 = MEM(reg2 + IMM)          | IMM[6:3] | IMM[2:0] | reg2  | reg1     | OPCODE |
| 5   | Type C      | SW reg1, IMM(reg2)   | MEM(reg2 + IMM) = reg1          | IMM[6:3] | reg1     | reg2  | IMM[2:0] | OPCODE |
| 6   |             | CMP reg1, IMM(reg2)  | SET FLAGS (reg1 - reg2)         | IMM[6:3] | reg2     | reg1  | IMM[2:0] | OPCODE |
| 7   |             | JMP IMM(reg1)        | PC = reg1 + IMM                 | IMM[6:3] | IMM[2:0] | reg1  |          | OPCODE |
| 8   |             | JG IMM(reg1)         | PC = reg1 + IMM IF PositiveFlag | IMM[6:3] | IMM[2:0] | reg1  |          | OPCODE |
| 9   |             | BNE IMM(reg1)        | PC = reg1 + IMM IF NOT ZeroFlag | IMM[6:3] | IMM[2:0] | reg1  |          | OPCODE |
| 10  |             | BEQ IMM(reg1)        | PC = reg1 + IMM IF ZeroFlag     | IMM[6:3] | IMM[2:0] | reg1  |          | OPCODE |
| 11  |             | HALT                 | Останов.                        |          |          |       |          | OPCODE |

## Способ кодирования

- **_Type A_**

| 4 бит(13:16) | 3 бит(10:12) | 3 бит(7:9) | 3 бит(4:6) | 4 бит(0:3) |
| ------------ | ------------ | ---------- | ---------- | ---------- |
| IMM[3:0]     | RS2          | RS1        | RD         | OPCODE     |

- **_Type B_**

Команды типа I (immediate, непосредственные)
используют два регистровых операнда и один
непосредственный операнд (константу)

| 4 бит(13:16) | 3 бит(10:12) | 3 бит(7:9) | 3 бит(4:6) | 4 бит(0:3) |
| ------------ | ------------ | ---------- | ---------- | ---------- |
| IMM[6:3]     | IMM[2:0]     | RS         | RD         | OPCODE     |

- **_Type C_**

Инструкции типа S/B (store/branch, хранение слова в памяти / условный пе- реход) используют два регистровых операнда и один непосредственный операнд (константу)

| 4 бит(13:16) | 3 бит(10:12) | 3 бит(7:9) | 3 бит(4:6) | 4 бит(0:3) |
| ------------ | ------------ | ---------- | ---------- | ---------- |
| IMM[6:3]     | RS2          | RS1        | IMM[2:0]   | OPCODE     |

---
