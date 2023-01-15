
import json
import numpy as np
from typing import List
from isa import write_logs, write_code, read_code, Term, Translate_Detail
import sys


def write_logs_test() -> bool:
    test_file = "test_journal.txt"

    logs: List[Translate_Detail] = [
        Translate_Detail(np.binary_repr(592, 16), Term(1, 1, 'addi')),
        Translate_Detail(np.binary_repr(572, 16), Term(2, 1, 'addi'))
    ]

    write_logs(test_file, logs)

    with open(test_file, encoding="utf-8") as file:
        code = json.loads(file.read())

    if (code[0][0] != logs[0].bin_code):
        return False
    if (code[0][1] != list(logs[0].term)):
        return False
    if (code[1][0] != logs[1].bin_code):
        return False
    if (code[1][1] != list(logs[1].term)):
        return False

    return True


def write_code_test() -> bool:
    test_file = "test_write_code.bin"

    code: List[np.int16] = [
        592,
        572
    ]

    write_code(test_file, code)

    with open(test_file, mode='rb') as file:
        if (file.read(16).decode() != np.binary_repr(code[0], 16)):
            return False
        if (file.read(16).decode() != np.binary_repr(code[1], 16)):
            return False

    return True


def read_code_test() -> bool:
    test_file = "test_read_code.bin"

    codes: List[np.int16] = [
        592,
        572
    ]

    with open(test_file, mode='wb') as file:
        file.write(np.binary_repr(codes[0], 16).encode())
        file.write(np.binary_repr(codes[1], 16).encode())

    received_codes: List[np.int16] = read_code(test_file)

    if (codes[0] != received_codes[0]):
        return False
    if (codes[1] != received_codes[1]):
        return False

    return True


def main(args):
    print(write_logs_test())
    print(write_code_test())
    print(read_code_test())
    pass


if __name__ == '__main__':
    main(sys.argv[1:])
