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


class Token(namedtuple('Token', 'TokenType value')):
    """Класс для токенов"""


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
        TokenType.STRING_LITERAL: r".?[a-z]+",
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
                    tokens.append(Token(lexem_type, code[cur_pos:end_pos]))
                break

        cur_pos = end_pos
        assert found == True, 'Не распознало лексему'

    return tokens


def translate(code: str) -> List[np.int16]:
    tokens: List[Token] = lexical_analysis(code)
    with open('parsing.json', mode='w') as file:
        file.write(json.dumps(tokens, indent=4))
    pass


def main(args):
    source, target = args

    # ['examples/cat.asm', 'code.out']
    with open(source, mode='r') as file:
        code = file.read()

    translate(code)
    pass


if __name__ == '__main__':
    main(sys.argv[1:])
