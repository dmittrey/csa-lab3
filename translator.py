from enum import Enum
import json
import sys
import re

from typing import List
import numpy as np
from collections import namedtuple


class TokenType(str, Enum):
    COLON = 'colon',
    SEMICOLON = 'semicolon',

    LEFT_BRACKET = 'left_bracket',
    RIGHT_BRACKET = 'right_bracket',

    REGISTER = 'register',
    NO_ARGS_OP = 'no_args_op',
    TWO_ARGS_OP = 'two_args_op',
    THREE_ARGS_OP = 'three_args_op',

    LEXEM = 'lexem',
    NUMBER = 'number',
    STRING = 'string'

    LABEL = 'label',

    ENTRY_POINT = 'entry_point'

    SHIFT = 'shift'
    pass


class Token(namedtuple('Token', 'TokenType value')):
    """Класс для токенов"""


"""
1) Сначала идет лексический анализ кода
Для лексического анализа кода определили enum TokenType

2)

"""


def lexicalAnalysis(code: str) -> List[Token]:
    tokens: List[Token] = list()

    lexem_pattern = re.compile("^.?[A-Z]+$", re.IGNORECASE)
    label_pattern = re.compile("^.?([A-Z]+):$", re.IGNORECASE)
    number_pattern = re.compile("^([0-9]+)$")
    string_pattern = re.compile("^'.*'$", re.IGNORECASE)
    shift_pattern = re.compile("^[+-][0-9]+\([A-Z]+\)$")

    registers = ['x0', 'x1', 'zflag', 'trapcause', 'x3', 'x4', 'x5', 'x6']
    alias_registers = ['ZR', 'PC', 'ZF', 'TC', 'DR', 'AC']

    no_args_ops = ['halt']
    two_args_ops = ['mov', 'ld', 'sw']
    three_args_ops = ['addi', 'beq', 'rem']

    text = code.split()

    for literal in text:
        literal = literal.replace(',', '')

        match literal:
            case ':':
                tokens.append(Token(TokenType.COLON, literal))
                continue
            case ';':
                tokens.append(Token(TokenType.SEMICOLON, literal))
                continue
            case '(':
                tokens.append(Token(TokenType.LEFT_BRACKET, literal))
                continue
            case ')':
                tokens.append(Token(TokenType.RIGHT_BRACKET, literal))
                continue
            case '_start':
                tokens.append(Token(TokenType.ENTRY_POINT, literal))
                continue

        if ((literal in registers) or (literal in alias_registers)):
            tokens.append(Token(TokenType.REGISTER, literal))
            continue

        if (literal in no_args_ops):
            tokens.append(Token(TokenType.NO_ARGS_OP, literal))
            continue

        if (literal in two_args_ops):
            tokens.append(Token(TokenType.TWO_ARGS_OP, literal))
            continue

        if (literal in three_args_ops):
            tokens.append(Token(TokenType.THREE_ARGS_OP, literal))
            continue

        if (lexem_pattern.match(literal)):
            tokens.append(Token(TokenType.LEXEM, literal))
            continue

        if (number_pattern.match(literal)):
            tokens.append(Token(TokenType.NUMBER, literal))
            continue

        if (label_pattern.match(literal)):
            tokens.append(Token(TokenType.LABEL, literal))
            continue

        if (shift_pattern.match(literal)):
            tokens.append(Token(TokenType.SHIFT, literal))
            continue

        if (string_pattern.match(literal)):
            tokens.append(Token(TokenType.STRING, literal))
            continue

    print(text)
    with open('parsing.json', mode='w') as file:
        file.write(json.dumps(tokens, indent=4))


def translate(code: str) -> List[np.int16]:
    tokens: List[Token] = lexicalAnalysis(code)
    pass


def main(args):
    source, target = args

    with open(source, mode='r') as file:
        code = file.read()

    translate(code)
    pass


if __name__ == '__main__':
    main(sys.argv[1:])
