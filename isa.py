"""
Типы данных для представления и сериализации/десериализации машинного кода.

Особенности:

- Машинный код сериализуется в список JSON.
- Один элемент списка -- одна инструкция.
- Индекс списка -- адрес инструкции.

Пример:

```json
[
    {
        "opcode": "jz",
        "arg": 5,
        "term": [
            1,
            5,
            "]"
        ]
    },
]
```

где:

- `opcode` -- строка с кодом операции;
- `arg` -- аргумент инструкции (если требуется);
- `term` -- информация о связанном месте в исходном коде (если есть).
"""

import json
from collections import namedtuple
from enum import Enum


class Opcode(str, Enum):
    """Opcode для ISA."""

    # Коды операций, представленных на уровне языка.
    ADD_IMM = 'ADDI'
    BRANCH_IF_EQUALS = 'BEQ'
    REM_OF_DIV = 'REM'
    MOV = 'MOV'
    LOAD = 'LD'
    SAVE = 'SW'

    # Операция остановки процессора
    HALT = 'halt'


class Term(namedtuple('Term', 'line pos symbol')):
    """Описание выражения из исходного текста программы."""


def write_code(filename, code):
    """Записать машинный код в файл."""
    with open(filename, "w", encoding="utf-8") as file:
        file.write(json.dumps(code, indent=4))


def read_code(filename):
    """Прочесть машинный код из файла."""
    with open(filename, encoding="utf-8") as file:
        code = json.loads(file.read())

    for instr in code:
        # Конвертация строки в Opcode
        instr['opcode'] = Opcode(instr['opcode'])
        # Конвертация списка из term в класс Term
        if 'term' in instr:
            instr['term'] = Term(
                instr['term'][0], instr['term'][1], instr['term'][2])

    return code
