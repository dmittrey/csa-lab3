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
from typing import Dict, List
from numpy import int16, int8, bitwise_and, binary_repr


class Opcode(int, Enum):
    """Opcode для ISA."""

    # Коды операций, представленных на уровне языка.
    ADD = 0
    BNE = 1
    REM = 2
    MOV = 3
    LOAD = 4
    SAVE = 5

    # Операция остановки процессора
    HALT = 6


class Register(str, Enum):
    """Алиасы для регистров"""


class Term(namedtuple('Term', 'line pos symbol')):
    """Описание выражения из исходного текста программы."""


# def write_logs(filename, code: List[int16], terms: List[Term]):
#     with open(filename, "w", encoding="utf-8") as file:
#         file.write(json.dumps({
#             'code': binary_repr(code, 16),
#             'term': terms
#         }, indent=4))

def write_logs(filename, instrs: List[str], terms: List[Term]):
    """Записать машинный код в файл."""
    logs: List[Dict] = list()

    for num in range(len(instrs)):
        logs.append({
            'instr': instrs[num],
            'term': terms[num]
        })

    with open(filename, "w", encoding="utf-8") as file:
        file.write(json.dumps(logs, indent=4))


def write_code(filename, code: List[int16]) -> None:
    """Записать машинный код в файл."""
    with open(filename, mode='wb') as file:
        for instr in code:
            instr_str = binary_repr(instr, 16)
            file.write(instr_str.encode())


def read_code(filename: str) -> List[int16]:
    """Прочесть машинный код из файла."""
    codes: List[int16] = []

    with open(filename, encoding="utf-8") as file:
        while True:
            code_str = file.read(16)
            if (code_str == ''):
                break

            codes.append(int(code_str.encode(), 2))

    return codes
