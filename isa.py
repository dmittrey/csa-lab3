# pylint: disable=missing-module-docstring     # чтобы не быть Капитаном Очевидностью
# pylint: disable=missing-class-docstring     # чтобы не быть Капитаном Очевидностью
# pylint: disable=missing-function-docstring  # чтобы не быть Капитаном Очевидностью
# pylint: disable=line-too-long               # строки с ожидаемым выводом

import json
from collections import namedtuple
from enum import Enum
from typing import Dict, List
from numpy import int16, binary_repr


class Opcode(int, Enum):
    """Opcode для ISA."""

    # Коды операций, представленных на уровне языка.
    ADDI = 0
    ADD = 1
    REM = 2
    MUL = 3
    DIV = 4
    LD = 5
    SW = 6
    CMP = 7
    JMP = 8
    JG = 9
    BNE = 10
    BEQ = 11

    # Операция остановки процессора
    HALT = 12


class Term(namedtuple('Term', 'line pos symbol')):
    """Описание выражения из исходного текста программы."""


def write_logs(filename, instrs: List[str], terms: List[Term]):
    """Записать машинный код в файл."""
    logs: List[Dict] = []

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
            instr_str = binary_repr(instr, 17)
            file.write(instr_str.encode())


def read_code(filename: str) -> List[int16]:
    """Прочесть машинный код из файла."""
    codes: List[int16] = []

    with open(filename, encoding="utf-8") as file:
        while True:
            code_str = file.read(17)
            if code_str == '':
                break

            codes.append(int(code_str.encode(), 2))

    return codes
