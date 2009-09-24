# -*- coding: utf-8 -*-
"""
    pygments.lexers.compiled
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Lexers for compiled languages.

    :copyright: Copyright 2006-2009 by the Pygments team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

import re
try:
    set
except NameError:
    from sets import Set as set

from pygments.scanner import Scanner
from pygments.lexer import Lexer, RegexLexer, include, bygroups, using, \
                           this, combined
from pygments.util import get_bool_opt, get_list_opt
from pygments.token import \
     Text, Comment, Operator, Keyword, Name, String, Number, Punctuation, \
     Error

__ALL__ = ['NWNLexer']

class NWNLexer(RegexLexer):
    """
    For NWNScript source code with preprocessor directives.
    """
    name = 'NWN'
    aliases = ['nw']
    filenames = ['*.nss', '*.ncs']
    mimetypes = ['text/nss', 'text/ncs']

    #: optional Comment or Whitespace
    _ws = r'(?:\s|//.*?\n|/[*].*?[*]/)+'

    tokens = {
        'whitespace': [
            (r'^\s*#if\s+0', Comment.Preproc, 'if0'),
            (r'^\s*#', Comment.Preproc, 'macro'),
            (r'\n', Text),
            (r'\s+', Text),
            (r'\\\n', Text), # line continuation
            (r'//(\n|(.|\n)*?[^\\]\n)', Comment.Single),
            (r'/(\\\n)?[*](.|\n)*?[*](\\\n)?/', Comment.Multiline),
        ],
        'statements': [
            (r'L?"', String, 'string'),
            (r"L?'(\\.|\\[0-7]{1,3}|\\x[a-fA-F0-9]{1,2}|[^\\\'\n])'", String.Char),
            (r'(\d+\.\d*|\.\d+|\d+)[eE][+-]?\d+[lL]?', Number.Float),
            (r'(\d+\.\d*|\.\d+|\d+[fF])[fF]?', Number.Float),
            (r'0x[0-9a-fA-F]+[Ll]?', Number.Hex),
            (r'0[0-7]+[Ll]?', Number.Oct),
            (r'\d+[Ll]?', Number.Integer),
            (r'[~!%^&*+=|?:<>/-]', Operator),
            (r'[()\[\],.]', Punctuation),
            (r'\b(case)(.+?)(:)', bygroups(Keyword, using(this), Text)),
            (r'(auto|break|case|const|continue|default|do|else|'
             r'for|if|return|static|'
             r'switch|while)\b', Keyword),
            (r'(int|float|char|string|object|location|effect|action|void)\b',
             Keyword.Type),
            (r'(true|false|NULL)\b', Name.Builtin),
            ('[a-zA-Z_][a-zA-Z0-9_]*:(?!:)', Name.Label),
            ('[a-zA-Z_][a-zA-Z0-9_]*', Name),
        ],
        'root': [
            include('whitespace'),
            # functions
            (r'((?:[a-zA-Z0-9_*\s])+?(?:\s|[*]))'    # return arguments
             r'([a-zA-Z_][a-zA-Z0-9_]*)'             # method name
             r'(\s*\([^;]*?\))'                      # signature
             r'(' + _ws + r')({)',
             bygroups(using(this), Name.Function, using(this), using(this),
                      Punctuation),
             'function'),
            # function declarations
            (r'((?:[a-zA-Z0-9_*\s])+?(?:\s|[*]))'    # return arguments
             r'([a-zA-Z_][a-zA-Z0-9_]*)'             # method name
             r'(\s*\([^;]*?\))'                      # signature
             r'(' + _ws + r')(;)',
             bygroups(using(this), Name.Function, using(this), using(this),
                      Punctuation)),
            ('', Text, 'statement'),
        ],
        'statement' : [
            include('whitespace'),
            include('statements'),
            ('[{}]', Punctuation),
            (';', Punctuation, '#pop'),
        ],
        'function': [
            include('whitespace'),
            include('statements'),
            (';', Punctuation),
            ('{', Punctuation, '#push'),
            ('}', Punctuation, '#pop'),
        ],
        'string': [
            (r'"', String, '#pop'),
            (r'\\([\\abfnrtv"\']|x[a-fA-F0-9]{2,4}|[0-7]{1,3})', String.Escape),
            (r'[^\\"\n]+', String), # all other characters
            (r'\\\n', String), # line continuation
            (r'\\', String), # stray backslash
        ],
        'macro': [
            (r'[^/\n]+', Comment.Preproc),
            (r'/[*](.|\n)*?[*]/', Comment.Multiline),
            (r'//.*?\n', Comment.Single, '#pop'),
            (r'/', Comment.Preproc),
            (r'(?<=\\)\n', Comment.Preproc),
            (r'\n', Comment.Preproc, '#pop'),
        ],
        'if0': [
            (r'^\s*#if.*?(?<!\\)\n', Comment.Preproc, '#push'),
            (r'^\s*#el(?:se|if).*\n', Comment.Preproc, '#pop'),
            (r'^\s*#endif.*?(?<!\\)\n', Comment.Preproc, '#pop'),
            (r'.*?\n', Comment),
        ]
    }

    def __init__(self, **options):
        RegexLexer.__init__(self, **options)

    def get_tokens_unprocessed(self, text):
        for index, token, value in \
            RegexLexer.get_tokens_unprocessed(self, text):
            yield index, token, value
