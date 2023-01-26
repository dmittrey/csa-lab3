# pylint: disable=missing-module-docstring    # чтобы не быть Капитаном Очевидностью
# pylint: disable=missing-class-docstring     # чтобы не быть Капитаном Очевидностью
# pylint: disable=missing-function-docstring  # чтобы не быть Капитаном Очевидностью
# pylint: disable=too-many-boolean-expressions
# pylint: disable=line-too-long               # строки с ожидаемым выводом

from enum import Enum
import json
import sys
import re

from typing import Dict, List
from collections import namedtuple

import isa


class TokenType(str, Enum):
    SYMBOL = 'symbol'

    NUMBER_LITERAL = 'number'
    STRING_LITERAL = 'string'
    CHAR_LITERAL = 'char'

    EOL = 'end_of_line'
    EOF = 'end_of_file'

    KEYWORD = 'keyword'
    COMMENT = 'comment'
    WHITESPACE = 'whitespace'


class ImmType(str, Enum):
    STRING = 'string'
    NUMBER = 'number'

    NOTHING = 'nothing'


class SectionType(str, Enum):
    DATA = '.data'
    CODE = '.text'


class Token(namedtuple('Token', 'TokenType value')):
    """Класс для токенов"""


class MemoryCell(namedtuple('MemoryCell', 'section imm_type reg1 reg2 reg3 imm opcode')):
    """Класс для парсинга в код ячеек памяти"""


def lexical_analysis(code: str) -> List[Token]:
    tokens: List[Token] = []

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

            if res is not None:
                found = True
                end_pos = cur_pos + res.end()
                if lexem_type not in (TokenType.COMMENT, TokenType.WHITESPACE):
                    tokens.append(
                        Token(lexem_type, code[cur_pos:end_pos].strip().lower()))
                break

        cur_pos = end_pos
        assert found is True, 'Не распознало лексему'

    return tokens


def shift_and_mask(value: int, shift_length: int, mask: int, length: int) -> int:
    masked_value = value & mask
    while masked_value > (2 ** (length) - 1):
        masked_value = masked_value >> 1
    return masked_value << shift_length


def generate(tokens: List[Token]) -> any:
    memory: List[MemoryCell] = []

    # Add stub to later put it jmp on .start
    jump_stub = MemoryCell(None, None, None, None, None, None, 'JMP')
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
        'x0': 0, 'zr': 0, 'ZR': 0,
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

        if cur_token.value == 'section':
            cur_section_place = num + 1
            num += 2
            continue

        # Идем вперед и ищем секцию
        if cur_section_place == -1:
            num += 1
        else:
            cur_section_token = tokens[cur_section_place]

            if cur_section_token.TokenType != TokenType.STRING_LITERAL:
                raise Exception('Expected string literal after section')

            # Логика парсинга инструкции в зависимости от секции
            section_name = cur_section_token.value
            match section_name:
                case SectionType.DATA:
                    if cur_token.TokenType == TokenType.EOL:
                        num += 1
                        continue
                    # В случае секции данных мы имеем грамматику string_literal: char_literal
                    # Сначала нужно взять три лексемы -> Проверить правильность
                    # -> засунуть и добавить ячейку памяти -> добавить алиас
                    if cur_token.TokenType != TokenType.STRING_LITERAL:
                        raise Exception(
                            'Expected string literal as alias in data section')
                    if tokens[num + 1].value != ':':
                        raise Exception(
                            'Expected colon between alias and char in data section')
                    if tokens[num + 2].TokenType != TokenType.CHAR_LITERAL:
                        raise Exception(
                            'Expected char literal as value in data section')
                    char_sign = tokens[num + 2].value.replace("'", "")
                    memory.append(MemoryCell(
                        SectionType.DATA, None, None, None, None, None, ord(char_sign)))
                    label_to_cell[cur_token.value] = len(memory) - 1
                    num += 3
                case SectionType.CODE:
                    if num + 1 < len(tokens) and tokens[num + 1].value == ':':
                        if tokens[num].TokenType != TokenType.STRING_LITERAL:
                            raise Exception(
                                'Expected string literal as label')
                        # Если нашли label значит он будет указывать
                        # на следующую инструкцию в памяти
                        label_to_cell[cur_token.value] = len(memory)
                        num += 2
                    else:
                        if tokens[num].TokenType == TokenType.EOL:
                            num += 1
                        elif tokens[num].TokenType != TokenType.STRING_LITERAL:
                            raise Exception(
                                'Unable to parse expression in text section')
                        # Парсинг лексем составляющих инструкцию
                        elif tokens[num].value in no_args_op:
                            memory.append(MemoryCell(
                                SectionType.CODE, ImmType.NOTHING, 0, 0, 0, 0, 'halt'))
                            num += 1
                        elif tokens[num].value in one_args_op:
                            if tokens[num + 1].TokenType != TokenType.NUMBER_LITERAL and tokens[num + 1].TokenType != TokenType.STRING_LITERAL:
                                raise Exception(
                                    'Unable to parse instruction ' + str(tokens[num: num + 7]))
                            reg1 = 0
                            imm = tokens[num + 1].value
                            imm_type = ImmType.NOTHING
                            if tokens[num + 1].TokenType == TokenType.NUMBER_LITERAL:
                                imm_type = ImmType.NUMBER
                            else:
                                imm_type = ImmType.STRING

                            memory.append(
                                MemoryCell(
                                    SectionType.CODE, imm_type, reg1, None, None, imm,
                                    tokens[num].value))

                            num += 2
                        elif tokens[num].value in two_args_op:
                            if (tokens[num + 1].TokenType != TokenType.STRING_LITERAL or tokens[num + 2].value != ',' or tokens[num + 3].value not in ['+', '-'] or tokens[num + 4].TokenType not in [TokenType.STRING_LITERAL, TokenType.NUMBER_LITERAL] or tokens[num + 5].value != '(' or tokens[num + 6].TokenType != TokenType.STRING_LITERAL or tokens[num + 7].value != ')'):
                                raise Exception(
                                    'Unable to parse instruction ' + str(tokens[num: num + 7]))
                            reg1 = registers[tokens[num + 1].value]
                            reg2 = registers[tokens[num + 6].value]
                            imm = tokens[num + 4].value
                            imm_type = ImmType.NOTHING
                            if tokens[num + 4].TokenType == TokenType.NUMBER_LITERAL:
                                imm_type = ImmType.NUMBER
                            else:
                                imm_type = ImmType.STRING

                            memory.append(MemoryCell(
                                SectionType.CODE, imm_type, reg1, reg2, None, imm,
                                tokens[num].value))
                            num += 8
                        elif tokens[num].value in three_args_op:
                            if (tokens[num + 1].TokenType != TokenType.STRING_LITERAL or tokens[num + 2].value != ',' or tokens[num + 3].TokenType != TokenType.STRING_LITERAL or tokens[num + 4].value != ',' or tokens[num + 5].TokenType not in (TokenType.STRING_LITERAL, TokenType.NUMBER_LITERAL)):
                                raise Exception(
                                    'Unable to parse instruction ' + str(tokens[num: num + 6]))
                            reg1 = registers[tokens[num + 1].value]
                            reg2 = registers[tokens[num + 3].value]
                            reg3 = tokens[num + 5].value
                            imm = tokens[num + 5].value
                            imm_type = ImmType.NOTHING
                            if tokens[num + 5].TokenType == TokenType.NUMBER_LITERAL:
                                imm_type = ImmType.NUMBER
                            else:
                                imm_type = ImmType.STRING

                            memory.append(MemoryCell(
                                SectionType.CODE, imm_type, reg1, reg2, reg3, imm,
                                tokens[num].value))
                            num += 6
                        else:
                            raise Exception(
                                'Unable to find instruction ' + str(tokens[num]))
                case _:
                    pass

    memory[0] = MemoryCell(SectionType.CODE, ImmType.STRING, 0, None,
                           None, '_start', 'jmp')

    values = []
    for cell in memory:
        res = 0
        imm = 0

        if (cell.section == SectionType.DATA):
            values.append(cell.opcode)
        else:
            if cell.opcode in one_args_op:
                if (cell.imm_type == ImmType.NUMBER):
                    imm = int(cell.imm)
                else:
                    imm = label_to_cell[cell.imm]

                res += shift_and_mask(imm, 10, 127, 7)
                res += shift_and_mask(cell.reg1, 7, 7, 3)

            if cell.opcode in two_args_op:
                if (cell.imm_type == ImmType.NUMBER):
                    imm = int(cell.imm)
                else:
                    imm = label_to_cell[cell.imm]

                if cell.opcode in ['sw', 'cmp']:
                    res += shift_and_mask(imm, 13, 120, 4)
                    res += shift_and_mask(cell.reg1, 10, 7, 3)
                    res += shift_and_mask(imm, 4, 7, 3)
                else:
                    res += shift_and_mask(imm, 10, 127, 7)
                    res += shift_and_mask(cell.reg1, 4, 7, 3)
                res += shift_and_mask(cell.reg2, 7, 7, 3)

            if cell.opcode in three_args_op:
                if cell.opcode in ['mul', 'rem', 'add']:
                    reg3 = registers[cell.imm]
                    res += shift_and_mask(reg3, 10, 7, 3)
                else:
                    if (cell.imm_type == ImmType.NUMBER):
                        imm = int(cell.imm)
                    else:
                        imm = label_to_cell[cell.imm]
                    res += shift_and_mask(imm, 10, 127, 7)
                res += shift_and_mask(cell.reg2, 7, 7, 3)
                res += shift_and_mask(cell.reg1, 4, 7, 3)

            if cell.opcode == 'addi':
                res += 0
            elif cell.opcode == 'add':
                res += 1
            elif cell.opcode == 'rem':
                res += 2
            elif cell.opcode == 'mul':
                res += 3
            elif cell.opcode == 'ld':
                res += 4
            elif cell.opcode == 'sw':
                res += 5
            elif cell.opcode == 'cmp':
                res += 6
            elif cell.opcode == 'jmp':
                res += 7
            elif cell.opcode == 'jg':
                res += 8
            elif cell.opcode == 'bne':
                res += 9
            elif cell.opcode == 'beq':
                res += 10
            else:
                res += 11
            values.append(res)
    return memory, values


def translate(code: str) -> List[MemoryCell]:
    tokens: List[Token] = lexical_analysis(code)
    codes: List[MemoryCell] = generate(tokens)

    return codes


def main(args):
    source, target, logs = ['examples/prob5.asm', 'examples/prob5.out', 'examples/prob5.json']

    with open(source, mode='r', encoding='utf-8') as file:
        code = file.read()

    details, codes  = translate(code)

    with open(logs, mode='w', encoding='utf-8') as file:
        file.write(json.dumps(details, indent=4))

    isa.write_code(target, codes)


if __name__ == '__main__':
    main(sys.argv[1:])
