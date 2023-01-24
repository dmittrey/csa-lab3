# pylint: disable=missing-module-docstring     # чтобы не быть Капитаном Очевидностью
# pylint: disable=missing-class-docstring     # чтобы не быть Капитаном Очевидностью
# pylint: disable=missing-function-docstring  # чтобы не быть Капитаном Очевидностью
# pylint: disable=line-too-long               # строки с ожидаемым выводом

import json
from typing import List
from numpy import binary_repr
from isa import write_logs, write_code, read_code, Term


def write_logs_test() -> bool:
    test_file = "test_journal.txt"

    instrs: List[int] = [
        binary_repr(592, 16), binary_repr(572, 16)
    ]

    terms: List[Term] = [
        Term(1, 1, 'addi'),
        Term(2, 1, 'addi')
    ]

    write_logs(test_file, instrs, terms)

    with open(test_file, encoding="utf-8") as file:
        code = json.loads(file.read())

    if code[0]['instr'] != instrs[0]:
        return False
    if code[0]['term'] != list(terms[0]):
        return False
    if code[1]['instr'] != instrs[1]:
        return False
    if code[1]['term'] != list(terms[1]):
        return False

    return True


def write_code_test() -> bool:
    test_file = "test_write_code.bin"

    code: List[int] = [
        592,
        572
    ]

    write_code(test_file, code)

    with open(test_file, mode='rb') as file:
        if file.read(16).decode() != binary_repr(code[0], 16):
            return False
        if file.read(16).decode() != binary_repr(code[1], 16):
            return False

    return True


def read_code_test() -> bool:
    test_file = "test_read_code.bin"

    codes: List[int] = [
        592,
        572
    ]

    with open(test_file, mode='wb') as file:
        file.write(binary_repr(codes[0], 16).encode())
        file.write(binary_repr(codes[1], 16).encode())

    received_codes: List[int] = read_code(test_file)

    if codes[0] != received_codes[0]:
        return False
    if codes[1] != received_codes[1]:
        return False

    return True


def main():
    print(write_logs_test())
    print(write_code_test())
    print(read_code_test())


if __name__ == '__main__':
    main()
