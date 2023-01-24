from enum import Enum
import json
import sys
import re
import isa

from typing import Dict, List
import numpy as np
from collections import namedtuple


class TokenType(str, Enum):
    SYMBOL = 'symbol'

    NUMBER_LITERAL = 'number',
    STRING_LITERAL = 'string',
    CHAR_LITERAL = 'char',

    EOL = 'end_of_line',
    EOF = 'end_of_file',

    KEYWORD = 'keyword',
    COMMENT = 'comment',
    WHITESPACE = 'whitespace'
    pass


class SectionType(str, Enum):
    DATA = '.data'
    CODE = '.text'


class Token(namedtuple('Token', 'TokenType value')):
    """Класс для токенов"""


class MemoryCell(namedtuple('MemoryCell', 'section reg1 reg2 reg3 imm opcode value')):
    """Класс для парсинга в код ячеек памяти"""


def lexical_analysis(code: str) -> List[Token]:
    tokens: List[Token] = list()

    patterns: Dict[TokenType, str] = {
        TokenType.KEYWORD: r"section",
        TokenType.COMMENT: r";.*$",
        TokenType.SYMBOL: r"[\:\+\-\,\(\)]",
        TokenType.NUMBER_LITERAL: r"[0-9]+",
        TokenType.CHAR_LITERAL: r"'\s*[a-z]*'",
        TokenType.STRING_LITERAL: r".?[a-z]+[0-9]*",
        TokenType.EOL: r"\n",
        TokenType.WHITESPACE: r"\s+"
    }

    cur_pos = 0
    while cur_pos < len(code):
        found = False

        for lexem_type, lexem_re in patterns.items():
            res = re.match(lexem_re, code[cur_pos:],
                           re.MULTILINE | re.IGNORECASE)

            if (res is not None):
                found = True
                end_pos = cur_pos + res.end()
                if (lexem_type != TokenType.COMMENT and lexem_type != TokenType.WHITESPACE):
                    tokens.append(
                        Token(lexem_type, code[cur_pos:end_pos].strip()))
                break

        cur_pos = end_pos
        assert found is True, 'Не распознало лексему'

    return tokens


def shift_and_mask(value: int, shift_length: int, mask: int, length: int) -> int:
    masked_value = value & mask
    while masked_value > (2 ** (length) - 1):
        masked_value = masked_value >> 1
    return masked_value << shift_length


def generate(tokens: List[Token]) -> List[MemoryCell]:
    memory: List[MemoryCell] = []

    # Add stub to later put it jmp on .start
    jump_stub = MemoryCell(None, None, None, None, None, 'JMP', 6)
    memory.append(jump_stub)

    # Map with label and its cell
    label_to_cell: Dict[str, int] = {}

    no_args_op: List[str] = [
        'halt'
    ]

    one_args_op: List[str] = [
        'jmp', 'jg', 'bne', 'beq'
    ]

    two_args_op: List[str] = [
        'ld', 'sw', 'cmp'
    ]

    three_args_op: List[str] = [
        'addi', 'add', 'rem', 'mul'
    ]

    registers: Dict[str, int] = {
        'x0': 0, 'ZR': 0,
        'x1': 1,
        'x2': 2,
        'x3': 3,
        'x4': 4,
        'x5': 5,
        'x6': 6, 'mtvec': 6,
        'x7': 7, 'mepc': 7
    }

    cur_section_place = -1
    num = 0

    while num < len(tokens):
        cur_token = tokens[num]

        if (cur_token.value == 'section'):
            cur_section_place = num + 1
            num += 2
            continue

        # Идем вперед и ищем секцию
        if (cur_section_place == -1):
            num += 1
            continue
        else:
            cur_section_token = tokens[cur_section_place]

            if (cur_section_token.TokenType != TokenType.STRING_LITERAL):
                raise Exception('Expected string literal after section')
            # Логика парсинга инструкции в зависимости от секции
            else:
                section_name = cur_section_token.value
                match section_name:
                    case SectionType.DATA:
                        if (cur_token.TokenType == TokenType.EOL):
                            num += 1
                            continue
                        # В случае секции данных мы имеем грамматику string_literal: char_literal
                        # Сначала нужно взять три лексемы -> Проверить правильность
                        # -> засунуть и добавить ячейку памяти -> добавить алиас
                        if (cur_token.TokenType != TokenType.STRING_LITERAL):
                            raise Exception(
                                'Expected string literal as alias in data section')
                        if (tokens[num + 1].value != ':'):
                            raise Exception(
                                'Expected colon between alias and char in data section')
                        if (tokens[num + 2].TokenType != TokenType.CHAR_LITERAL):
                            raise Exception(
                                'Expected char literal as value in data section')
                        char_sign = tokens[num + 2].value.replace("'", "")
                        memory.append(MemoryCell(
                            SectionType.DATA, None, None, None, None, None, ord(char_sign)))

                        label_to_cell[cur_token.value] = len(memory) - 1

                        num += 3
                        pass
                    case SectionType.CODE:
                        if (num + 1 < len(tokens) and tokens[num + 1].value == ':'):
                            if (tokens[num].TokenType != TokenType.STRING_LITERAL):
                                raise Exception(
                                    'Expected string literal as label')
                            else:
                                # Если нашли label значит он будет указывать на следующую инструкцию в памяти
                                label_to_cell[cur_token.value] = len(memory)
                                num += 2
                                continue

                        else:
                            if (tokens[num].TokenType == TokenType.EOL):
                                num += 1
                                continue

                            if (tokens[num].TokenType != TokenType.STRING_LITERAL):
                                raise Exception(
                                    'Unable to parse expression in text section')

                            # Парсинг лексем составляющих инструкцию
                            if (tokens[num].value in no_args_op):
                                res = 11
                                memory.append(MemoryCell(
                                    SectionType.CODE, 0, 0, 0, 0, 'halt', res))
                                num += 1
                                continue

                            if (tokens[num].value in one_args_op):
                                if (tokens[num + 1].TokenType != TokenType.NUMBER_LITERAL):
                                    raise Exception(
                                        'Unable to parse instruction ' + str(tokens[num: num + 7]))

                                imm = int(tokens[num + 1].value)

                                match (tokens[num].value):
                                    case 'jmp':
                                        res = 0
                                        res += shift_and_mask(imm, 10, 127, 7)
                                        res += shift_and_mask(reg1, 7, 7, 3)
                                        res += 7
                                        memory.append(
                                            MemoryCell(
                                                SectionType.CODE, reg1, None, None, imm, tokens[num].value, res))
                                        pass
                                    case 'jg':
                                        res = 0
                                        res += shift_and_mask(imm, 10, 127, 7)
                                        res += shift_and_mask(reg1, 7, 7, 3)
                                        res += 8
                                        memory.append(
                                            MemoryCell(
                                                SectionType.CODE, reg1, None, None, imm, tokens[num].value, res))
                                        pass
                                    case 'bne':
                                        res = 0
                                        res += shift_and_mask(imm, 10, 127, 7)
                                        res += shift_and_mask(reg1, 7, 7, 3)
                                        res += 9
                                        memory.append(
                                            MemoryCell(
                                                SectionType.CODE, reg1, None, None, imm, tokens[num].value, res))
                                        pass
                                    case 'beq':
                                        res = 0
                                        res += shift_and_mask(imm, 10, 127, 7)
                                        res += shift_and_mask(reg1, 7, 7, 3)
                                        res += 10
                                        memory.append(
                                            MemoryCell(
                                                SectionType.CODE, reg1, None, None, imm, tokens[num].value, res))
                                        pass
                                num += 2
                                continue

                            if (tokens[num].value in two_args_op):
                                if (tokens[num + 1].TokenType != TokenType.STRING_LITERAL or tokens[num + 2].value != ',' or tokens[num + 3].value not in ['+', '-'] or tokens[num + 4].TokenType not in [TokenType.STRING_LITERAL, TokenType.NUMBER_LITERAL] or tokens[num + 5].value != '(' or tokens[num + 6].TokenType != TokenType.STRING_LITERAL or tokens[num + 7].value != ')'):
                                    raise Exception(
                                        'Unable to parse instruction ' + str(tokens[num: num + 7]))

                                # Skip <instr>(1) <reg>(1) <comma>(1) <shift>(5)
                                reg1 = registers[tokens[num + 1].value]
                                reg2 = registers[tokens[num + 6].value]
                                imm = 0

                                if (tokens[num + 4].TokenType == TokenType.NUMBER_LITERAL):
                                    imm = int(tokens[num + 4].value)
                                else:
                                    imm = label_to_cell[tokens[num + 4].value]

                                match (tokens[num].value):
                                    case 'ld':
                                        res = int()
                                        res += shift_and_mask(imm, 10, 127, 7)
                                        res += shift_and_mask(reg2, 7, 7, 3)
                                        res += shift_and_mask(reg1, 4, 7, 3)
                                        res += 4
                                        memory.append(MemoryCell(
                                            SectionType.CODE, reg1, reg2, None, imm, tokens[num].value, res))
                                        pass
                                    case 'sw':
                                        res = int()
                                        res += shift_and_mask(imm, 13, 120, 4)
                                        res += shift_and_mask(reg1, 10, 7, 3)
                                        res += shift_and_mask(reg2, 7, 7, 3)
                                        res += shift_and_mask(imm, 4, 7, 3)
                                        res += 5
                                        memory.append(MemoryCell(
                                            SectionType.CODE, reg1, reg2, None, imm, tokens[num].value, res))
                                        pass
                                    case 'cmp':
                                        res = int()
                                        res += shift_and_mask(imm, 13, 120, 4)
                                        res += shift_and_mask(reg1, 10, 7, 3)
                                        res += shift_and_mask(reg2, 7, 7, 3)
                                        res += shift_and_mask(imm, 4, 7, 3)
                                        res += 6
                                        memory.append(MemoryCell(
                                            SectionType.CODE, reg1, reg2, None, imm, tokens[num].value, res))
                                        pass
                                num += 8
                                continue

                            if (tokens[num].value in three_args_op):
                                if (tokens[num + 1].TokenType != TokenType.STRING_LITERAL or tokens[num + 2].value != ',' or tokens[num + 3].TokenType != TokenType.STRING_LITERAL or tokens[num + 4].value != ',' or tokens[num + 5].TokenType not in [
                                        TokenType.STRING_LITERAL, TokenType.NUMBER_LITERAL]):
                                    raise Exception(
                                        'Unable to parse instruction ' + str(tokens[num: num + 6]))

                                reg1 = registers[tokens[num + 1].value]
                                reg2 = registers[tokens[num + 3].value]
                                imm = 0

                                if (tokens[num].value in ['addi']):
                                    if (tokens[num + 5].TokenType == TokenType.NUMBER_LITERAL):
                                        imm = int(tokens[num + 5].value)
                                    else:
                                        if (memory[label_to_cell[tokens[num + 5].value]].section == SectionType.DATA):
                                            imm = int(
                                                memory[label_to_cell[tokens[num + 5].value]].value.encode(), 2)
                                        else:
                                            imm = label_to_cell[tokens[num + 5].value]

                                match (tokens[num].value):
                                    case 'addi':
                                        res = 0
                                        res += shift_and_mask(imm, 10, 127, 7)
                                        res += shift_and_mask(reg2, 7, 7, 3)
                                        res += shift_and_mask(reg1, 4, 7, 3)
                                        res += 0
                                        memory.append(MemoryCell(
                                            SectionType.CODE, reg1, reg2, None, imm, tokens[num].value, res))
                                        pass
                                    case 'add':
                                        reg3 = registers[tokens[num + 5].value]

                                        res = 0
                                        res += shift_and_mask(reg3, 10, 7, 3)
                                        res += shift_and_mask(reg2, 7, 7, 3)
                                        res += shift_and_mask(reg1, 4, 7, 3)
                                        res += 1
                                        memory.append(MemoryCell(
                                            SectionType.CODE, reg1, reg2, reg3, imm, tokens[num].value, res))
                                        pass
                                    case 'rem':
                                        reg3 = registers[tokens[num + 5].value]

                                        res = 0
                                        res += shift_and_mask(reg3, 10, 7, 3)
                                        res += shift_and_mask(reg2, 7, 7, 3)
                                        res += shift_and_mask(reg1, 4, 7, 3)
                                        res += 2
                                        memory.append(MemoryCell(
                                            SectionType.CODE, reg1, reg2, reg3, imm, tokens[num].value, res))
                                        pass
                                    case 'mul':
                                        reg3 = registers[tokens[num + 5].value]

                                        res = 0
                                        res += shift_and_mask(reg3, 10, 7, 3)
                                        res += shift_and_mask(reg2, 7, 7, 3)
                                        res += shift_and_mask(reg1, 4, 7, 3)
                                        res += 2
                                        memory.append(MemoryCell(
                                            SectionType.CODE, reg1, reg2, reg3, imm, tokens[num].value, res))
                                        pass
                                num += 6
                                continue
                            else:
                                raise Exception(
                                    'Unable to find instruction ' + str(tokens[num]))
                    case _:
                        pass
        num += 1

    res = 0
    res += shift_and_mask(label_to_cell['_start'], 10, 127, 7)
    res += shift_and_mask(0, 7, 15, 3)
    res += 7
    memory[0] = MemoryCell(SectionType.CODE, 0, None,
                           None, label_to_cell['_start'], 'JMP', res)
    return memory


def translate(code: str) -> List[MemoryCell]:
    tokens: List[Token] = lexical_analysis(code)
    codes: List[MemoryCell] = generate(tokens)

    return codes


def main(args):
    source, target, logs = args

    with open(source, mode='r') as file:
        code = file.read()

    codes: List[MemoryCell] = translate(code)

    with open(logs, mode='w') as file:
        file.write(json.dumps(codes, indent=4))

    isa.write_code(target, [x.value for x in codes])
    pass


if __name__ == '__main__':
    main(sys.argv[1:])
