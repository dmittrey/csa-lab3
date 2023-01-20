# csa-lab3

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

<register> ::= "ZR" | "PC" | "ZF" | "TC" | x[3-6]
<immediate> ::= <digit_list>
<shift> ::= <sign> <immediate> "(" <register> ")"

<two_arg_op> ::= "mov" | "ld" | "sw" | "halt"
<three_arg_op> ::= "addi" | "beq" | "rem"

<two_args_instr> ::= <two_arg_op> <register> <shift> | <two_arg_op> <register> <immediate>
<three_args_instr> ::= <three_arg_op> <register> <register> <immediate> | <three_arg_op> <register> <register>

<instruction> ::= <two_args_instr> <comment> | <three_args_instr> <comment> | <comment>
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

- Память одна на команды и данные(согласно варианту). Память адресуется с помощью 16-битного адреса.
- При попытке исполнить данные как инструкцию программа падает с ошибкой.
- Scope в языке глобальный.

## Модель памяти

- Размер машинного слова 16 бит. Адресация абсолютная.
- Структура памяти неоднородная, первые 32 ячейки зарезервированы под устройства ввода-вывода.
- Пользователю доступны 6 регистров(остальные два - CSR регистры)

| Название регистра | Алиас    | Назначение                |
| ----------------- | -------- | ------------------------- |
| x0                | ZR       | Регистр всегда хранит 0   |
| x1                | PC       | Счетчик команд            |
| x2                | -        | Регистр общего назначения |
| x3                | DR       | Регистр данных            |
| x4                | mepc     | Previous PC value         |
| x5                | mtvec    | Interrupt vector address  |
| x6                | AC       | Аккумулятор               |
| x7                | mscratch | Save mem block for state  |

## Отображение на модель памяти процессора

```text
     Memory (for data and instructions)
+-------------------------------+
|    ...                        |
| 0x00: var1                    |
| 0x20: var2                    |
| 0x40: cmd1                    |
| 0x60: cmd2                    |
|    ...                        |
| 0xFFBF interruption handler 0 |
|    ...                        |
+-------------------------------+
```

Инструкции и данные не перемешиваются(сначала данные, потом инструкции). Обработчик прерывания размещается в последних 4 машинных словах.

# Система команд

## Особенности процессора

- Машинное слово -- 16 бит, знаковое.
- Память данных и команд:

  - Адресуется через DR.
  - Адрес следующей команды хранится в аккумуляторе
  - Регистр x0 не может изменятся, там статично лежит значение 0.

- Ввод-вывод - memory-mapped. Первые 32 ячейки зарезервированы под внешние устройства. Доступ осуществляется через запись номера устройства в DR. Данные будут лежать в аккумуляторе.
- Program_counter - счетчик команд. Инкрементируется с каждой инструкцией, может быть перезаписан командой перехода.
- Прерываний есть, состояние AC и PC сохраняется над обработчиком прерывания. После обработки прерывания работа программы возобновляется.
- Машина поддерживает только абсолютную адресацию.
- Присутствует флаг Z (zero) для команд перехода.

## Набор инструкций

| №   | Тип команды | Название команды     | Назначение                      | 4 бит    | 3 бит    | 3 бит | 3 бит    | 3 бит  |
| --- | ----------- | -------------------- | ------------------------------- | -------- | -------- | ----- | -------- | ------ |
| 0   | Type I      | ADDI reg1, reg2, IMM | reg1 = reg2 + IMM               | IMM[6:3] | IMM[2:0] | reg2  | reg1     | OPCODE |
| 1   | Type S/B    | BNE reg1, reg2, IMM  | if (reg1 != reg2) PC = PC + IMM | IMM[6:3] | reg2     | reg1  | IMM[2:0] | OPCODE |
| 2   | Type R      | REM reg1, reg2, reg3 | reg1 = reg2 % reg3              | IMM[3:0] | reg3     | reg2  | reg1     | OPCODE |
| 3   | Type I      | LD reg1, IMM(reg2)   | reg1 = MEM(reg2 + IMM)          | IMM[6:3] | IMM[2:0] | reg2  | reg1     | OPCODE |
| 4   | Type S/B    | SW reg1, IMM(reg2)   | MEM(reg2 + IMM) = reg1          | IMM[6:3] | reg1     | reg2  | IMM[2:0] | OPCODE |

## Способ кодирования

- **_Type R_**

Инструкции типа R используют три регистра
в качестве операндов: два регистра-источника
и один регистр-назначение.

| 4 бит(12:15) | 3 бит(9:11) | 3 бит(6:8) | 3 бит(3:5) | 3 бит(0:2) |
| ------------ | ----------- | ---------- | ---------- | ---------- |
| IMM[3:0]     | RS2         | RS1        | RD         | OPCODE     |

- **_Type I_**

Команды типа I (immediate, непосредственные)
используют два регистровых операнда и один
непосредственный операнд (константу)

| 4 бит    | 3 бит    | 3 бит | 3 бит | 3 бит  |
| -------- | -------- | ----- | ----- | ------ |
| IMM[6:3] | IMM[2:0] | RS    | RD    | OPCODE |

- **_Type S/B_**

Инструкции типа S/B (store/branch, хранение слова в памяти / условный пе- реход) используют два регистровых операнда и один непосредственный операнд (константу)

| 4 бит    | 3 бит | 3 бит | 3 бит    | 3 бит  |
| -------- | ----- | ----- | -------- | ------ |
| IMM[6:3] | RS2   | RS1   | IMM[2:0] | OPCODE |

---
