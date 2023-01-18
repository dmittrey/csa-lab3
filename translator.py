from enum import Enum
import json
import sys
import re

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


class MemoryCell(namedtuple('MemoryCell', 'section value')):
    """Класс для парсинга в код ячеек памяти"""


"""
1) Сначала идет лексический анализ кода
Для лексического анализа кода определили enum TokenType

2)

"""


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
        TokenType.WHITESPACE: '\s+'
    }

    cur_pos = 0
    while cur_pos < len(code):
        found = False

        for lexem_type, lexem_re in patterns.items():
            res = re.match(lexem_re, code[cur_pos:],
                           re.MULTILINE | re.IGNORECASE)

            if (res != None):
                found = True
                end_pos = cur_pos + res.end()
                if (lexem_type != TokenType.COMMENT and lexem_type != TokenType.WHITESPACE):
                    tokens.append(
                        Token(lexem_type, code[cur_pos:end_pos].strip()))
                break

        cur_pos = end_pos
        assert found == True, 'Не распознало лексему'

    return tokens


def generate(tokens: List[Token]) -> List[MemoryCell]:
    memory: List[MemoryCell] = []

    # Сопоставляет номер токена с ячейкой где используется
    label_to_cell: Dict[int, int] = {}

    no_args_op: List[str] = [
        'halt'
    ]

    two_args_op: List[str] = [
        'mov', 'ld', 'sw'
    ]

    three_args_op: List[str] = [
        'addi', 'bne', 'rem'
    ]

    registers: Dict[str, int] = {
        'x0': 0, 'ZR': 0,
        'x1': 1, 'PC': 1,
        'x2': 2, 'TC': 2,
        'x3': 3, 'DR': 3,
        'x4': 4,
        'x5': 5,
        'x6': 6, 'AC': 6
    }

    # for num in range(len(tokens)):
    #     if (tokens[num].value == ':'):
    #         prev_token = tokens[num - 1]
    #         if (prev_token.TokenType == TokenType.STRING_LITERAL):
    #             # Номер токена перед инструкцией к которой привяжем label
    #             labels[prev_token.value] = num - 1
    #         else:
    #             raise Exception('Expected string literal before colon')

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
                        char_binary = int(''.join(format(x, 'b') for x in bytearray(
                            tokens[num + 2].value.replace("'", ""), 'utf-8')), 2)
                        memory.append(MemoryCell(
                            SectionType.DATA, np.binary_repr(char_binary, 16)))

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
                                res = 6
                                memory.append(MemoryCell(
                                    SectionType.CODE, np.binary_repr(res, 16)))
                                num += 1
                                continue

                            if (tokens[num].value in two_args_op):
                                if (tokens[num + 1].TokenType != TokenType.STRING_LITERAL or
                                    tokens[num + 2].value != ',' or
                                    tokens[num + 3].value not in ['+', '-'] or
                                    tokens[num + 4].TokenType not in [TokenType.STRING_LITERAL, TokenType.NUMBER_LITERAL] or
                                    tokens[num + 5].value != '(' or
                                    tokens[num + 6].TokenType != TokenType.STRING_LITERAL or
                                    tokens[num + 7].value != ')'
                                    ):
                                    raise Exception(
                                        'Unable to parse instruction ' + tokens[num:num+7])

                                # Skip <instr>(1) <reg>(1) <comma>(1) <shift>(5)
                                reg1 = registers[tokens[num + 1].value]
                                reg2 = registers[tokens[num + 6].value]
                                imm = 0

                                if (tokens[num + 4].TokenType == TokenType.NUMBER_LITERAL):
                                    imm = int(tokens[num + 4].value)
                                else:
                                    imm = int(
                                        memory[label_to_cell[tokens[num + 4].value]].value.encode(), 2)

                                match (tokens[num].value):
                                    case 'mov':
                                        res = 0
                                        res += imm << 9
                                        res += reg2 << 6
                                        res += reg1 << 3
                                        res += 3
                                        memory.append(MemoryCell(
                                            SectionType.CODE, np.binary_repr(res, 16)))
                                        pass
                                    case 'ld':
                                        res = 0
                                        res += imm << 9
                                        res += reg2 << 6
                                        res += reg1 << 3
                                        res += 4
                                        memory.append(MemoryCell(
                                            SectionType.CODE, np.binary_repr(res, 16)))
                                        pass
                                    case 'sw':
                                        res = 0
                                        res += imm << 12  # mask 2 1 0 bits to 0
                                        res += reg1 << 9
                                        res += reg2 << 6
                                        res += imm << 3  # mask 2 1 0 bits to 1 other 0
                                        res += 5
                                        memory.append(MemoryCell(
                                            SectionType.CODE, np.binary_repr(res, 16)))
                                        pass
                                num += 8
                                continue

                            if (tokens[num].value in three_args_op):
                                if (tokens[num + 1].TokenType != TokenType.STRING_LITERAL or
                                            tokens[num + 2].value != ',' or
                                            tokens[num + 3].TokenType != TokenType.STRING_LITERAL or
                                            tokens[num + 4].value != ',' or
                                            tokens[num + 5].TokenType not in [
                                            TokenType.STRING_LITERAL, TokenType.NUMBER_LITERAL]
                                        ):
                                    raise Exception(
                                        'Unable to parse instruction ' + tokens[num:num+6])

                                reg1 = registers[tokens[num + 1].value]
                                reg2 = registers[tokens[num + 3].value]
                                imm = 0

                                if (tokens[num].value in ['addi', 'bne']):
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
                                        res += imm << 9
                                        res += reg2 << 6
                                        res += reg1 << 3
                                        res += 0
                                        memory.append(MemoryCell(
                                            SectionType.CODE, np.binary_repr(res, 16)))
                                        pass
                                    case 'bne':
                                        res = 0
                                        res += imm << 12  # mask 2 1 0 bits to 0
                                        res += reg2 << 9
                                        res += reg1 << 6
                                        res += imm << 3  # mask 2 1 0 bits to 1 other 0
                                        res += 1
                                        memory.append(MemoryCell(
                                            SectionType.CODE, np.binary_repr(res, 16)))
                                        pass
                                    case 'rem':
                                        reg3 = registers[tokens[num + 5].value]

                                        res = 0
                                        res += imm << 12  # mask 2 1 0 bits to 0
                                        res += reg3 << 9
                                        res += reg2 << 6
                                        res += reg1 << 3
                                        res += 2
                                        memory.append(MemoryCell(
                                            SectionType.CODE, np.binary_repr(res, 16)))
                                        pass
                                num += 6
                                continue
                        pass
                    case _:
                        pass
        num += 1

    return memory


def translate(code: str) -> List[MemoryCell]:
    tokens: List[Token] = lexical_analysis(code)
    codes: List[MemoryCell] = generate(tokens)

    return codes


def main(args):
    source, target = args

    # ['examples/cat.asm', 'code.out']
    with open(source, mode='r') as file:
        code = file.read()

    codes: List[MemoryCell] = translate(code)

    with open(target, mode='w') as file:
        file.write(json.dumps(codes, indent=4))
    pass


if __name__ == '__main__':
    main(sys.argv[1:])
