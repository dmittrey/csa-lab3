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

# Описание ISA

```ebnf
<letter> ::= [a-z] | [A-Z]
<digit> ::= [0-9]
<digit_list> ::= <digit> | <digit> <digit_list>
<digit_or_letter> ::= <letter> | <digit>
<digit_or_letter_list> ::= <sign> | <sign> <digit_or_letter_list>
<identifier> ::= <letter> | <letter> <digit_or_letter_list>
<sign> ::= "-" | "+"

<register> ::= "ZR" | "PC" | "ZF" | "TC" | x[3-6]
<immediate> ::= <digit_list>
<shift> ::= <sign> <immediate> "(" <register> ")"

<two_arg_op> ::= "mov" | "ld" | "sw" | "halt"
<three_arg_op> ::= "addi" | "beq" | "rem"

<two_args_instr> ::= <two_arg_op> <register> <shift> | <two_arg_op> <register> <immediate>
<three_args_instr> ::= <three_arg_op> <register> <register> <immediate> | <three_arg_op> <register> <register>

<instruction> ::= <two_args_instr> | <three_args_instr>
<label> ::= <identifier>
<program_line> ::= <label> <instruction> | <label> | <instruction>
<program_line_list> ::= <program_line> | <program_line> <program_line_list>

<section> ::= "section" <identifier> <program_line_list>
<section_list> ::=  <section> | <section> <section_list>
<program> ::= <section_list>
```

## Типы команд

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

Инструкции типа S/B (store/branch, хранение слова в памяти / условный пе- реход) используют два регистровых операнда и один не- посредственный операнд (константу)

| 4 бит    | 3 бит | 3 бит | 3 бит    | 3 бит  |
| -------- | ----- | ----- | -------- | ------ |
| IMM[6:3] | RS2   | RS1   | IMM[2:0] | OPCODE |

---

## Команды

| Тип команды | Название команды     | Назначение                     | 4 бит    | 3 бит    | 3 бит | 3 бит    | 3 бит  |
| ----------- | -------------------- | ------------------------------ | -------- | -------- | ----- | -------- | ------ |
| Type I      | ADDI reg1, reg2, IMM | reg1 = reg2 + IMM              | IMM[6:3] | IMM[2:0] | reg2  | reg1     | OPCODE |
| Type S/B    | BEQ reg1, reg2, IMM  | if (reg1 = reg2) PC = PC + IMM | IMM[6:3] | reg2     | reg1  | IMM[2:0] | OPCODE |
| Type R      | REM reg1, reg2, reg3 | reg1 = reg2 % reg3             | IMM[3:0] | reg3     | reg2  | reg1     | OPCODE |
| Type I      | MOV reg1, IMM(reg2)  | reg1 = IMM + reg2              | IMM[6:3] | IMM[2:0] | reg2  | reg1     | OPCODE |
| Type I      | LD reg1, IMM(reg2)   | reg1 = MEM(reg2 + IMM)         | IMM[6:3] | IMM[2:0] | reg2  | reg1     | OPCODE |
| Type S/B    | SW reg1, IMM(reg2)   | MEM(reg2 + IMM) = reg1         | IMM[6:3] | reg1     | reg2  | IMM[2:0] | OPCODE |

# Описание регистров

| Название регистра | Алиас | Назначение                                            |
| ----------------- | ----- | ----------------------------------------------------- |
| x0                | ZR    | Регистр всегда хранит 0                               |
| x1                | PC    | Регистр указывает на следующую исполняемую инструкцию |
| zflag             | ZF    | Регистр хранит флаг состояния АЛУ                     |
| trapcause         | TC    | CSR регистр для сохранения причины прерывания         |
| x3-x6             | -     | Регистры общего назначения                            |
