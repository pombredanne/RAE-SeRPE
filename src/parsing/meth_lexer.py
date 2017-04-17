"""
Date: Thu, Sat, 18 Feb, 2017
Last updated: Sat, 27 Mar, 2017
Author: Samuel Barham
Organization: University of Maryland, College Park (PhD student)

Project: RAE/SeRPE implementation
Component: Planning-DSL Interpreter

Description:
"Lexer" is an abbreviated form of "lexical analyzer" -- also known as a
tokenizer. Lexing, or tokenization, is the process by which a stream of raw
character-data is transformed into a stream of lexemes (tokens) -- each of which
is a sequence of characters from some language L, over some alphabet S. A lexer
is typically implemented as a table-driven finite state automaton -- and those
generated by the popular UNIX tool, lex, are no exception. Lex, in its turn, is
an abbreviation of "lexical analyzer generator," and it does just what you would
expect it to -- it generates lexical analyzers (lexers), based on rules supplied
by you (the user) in the proper format. To put it simply, these rules define the
set of lexemes (tokens) that compose the language -- and, additionally, often
imposes a type system on on that language, perhaps classifying the lexeme
"142,000" as an INT (for example) or the lexeme "some_var" as an ID. This token
stream is then often used by a parser -- which identifies syntactic relations
between lexemes in the token stream, aggregating the tokens into larger struc-
tures.

In particular, this file, meth_lexer.py contains the lexer that lexes the
method-specification DSL we've designed for our RAE/SeRPE system. The resulting
token stream is then parsed by the method parser, specificed in its turn in
meth_parser.py.

PLY is a popular Python-implementation of the UNIX lex/yacc tool, and this
file defines the rules by which PLY will create the lexer for our method-
definition language (i.e., the domain-specific language in which we will define
the methods in a given planning domain).

More information on the PLY module and how it works can be found at the
following URL: http://www.dabeaz.com/ply/ply.html#ply_nn1
"""

import ply.lex as lex
import json                 # a better way of getting a pretty print of a dict
from pydoc import pager     # we'll be using this to produce less-like,
                            # paged output -- primarily for debugging purposes

"""
TOKENS

Following is the tokens list. This is used by both ply.lex and ply.yacc --
by ply.lex for validation purposes, by ply.yacc to identify valid terminals.
"""

reserved = {
    # method delimiter
    'method':   'METHOD',
    # statement delimiters
    'task':     'TASK',
    'pre':      'PRE',
    'body':     'BODY',
    # control structure keywords
    'if':       'IF',
    'then':     'THEN',
    'else':     'ELSE',
    'elsif':    'ELSIF',    # this makes lexing and parsing a bit easier
    'while':    'WHILE',
    'do':       'DO',
    #'for':      'FOR',
    #'in':       'IN',
    'end':      'END',
    # binary boolean operators
    'and':      'AND',
    'or':       'OR',
    # unary operator
    'not':      'NOT'
}

# list(set()) is a common means of removing duplicates from a list
tokens = list(set(reserved.values() + [
    # identifiers
    'ID',
    # data types
    'INT',
    'FLOAT',
    'STRING',
    # punctuation
    'LPAREN',
    'RPAREN',
    'COLON',
    'COMMA',
    # relational operators
    'EQUALS',
    'LTE',
    'GTE',
    'LT',
    'GT',
    # binary boolean operators
    'AND',
    'OR',
    # binary arithmetic operators
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDED_BY',
    # unary boolean operator
    'NOT',
    # assignment operator
    'ASSIGN',
    # boolean primitives
    'TRUE',
    'FALSE',
    # terrible software design decision
    'PYTHON_CODE'
]))

# a lexer state indicating that the portion of the string currently being
# lexed is native python code that must be grouped together in a single,
# monolithic token
states = (
    ('pythoncode', 'exclusive'),
)

"""
LEXER RULES

The lexer provided by ply.lex returns lexemes, or tokens, in the form of
LexToken objects. A LexToken object has instance fields (attributes):
    tok.type
    tok.value [these two form the traditional Token-type/Token-value pair]
    tok.lineno
    tok.linepos [these are used for bookkeeping purposes -- and are handy
                 when, for instance, issuing parse errors. Note that
                 tok.linepos refers to the index of the token relative to the
                 start of the input text]

The lexer is provided with a token stream in the form of a string via the
lex.lex.input() method. It usses tokens one by one via the lex.lex.token()
method.

Lexer token rules can be specified as simple token rules -- i.e., ones that
merely return the token's value --, or as token action rules -- i.e., ones
that perform actions on the token's value(s) [for instance, aggregating a list].
In the former case, the rule is written as a simple assignment of a RE (qua raw
string) to a variable whose identifier begins with 't_' followed by the desired
name of the token (in all caps, to distinguish these rules from those that
include actions). In the latter case, the rules are written as regular Python
functions, each of which takes a paramter 't' which represents a LexToken
object, whose value field (.value) has already been set to the string that the
token represents. Here, the regular expression used to capture the token is
provided as the function's documentation string.
"""

# literals = ['%']

# MODE SWITCHING RULES
# Match the "=BEGIN" keyword and enter native-python state
def t_begin_pythoncode(t):
    r'=BEGIN'
    t.lexer.code_start = t.lexer.lexpos     # Record the starting position
    t.lexer.begin('pythoncode')            # Enter 'ccode' state

def t_pythoncode_error(t):
    t.lexer.skip(1)

# Match the "=END" keyword and re-enter meth-file DSL state
def t_pythoncode_end(t):
    r'=END'
    t.type = "PYTHON_CODE"
    t.value = t.lexer.lexdata[t.lexer.code_start:t.lexer.lexpos-4]
    t.lexer.lineno += t.value.count('\n')
    t.lexer.begin('INITIAL')
    return t

# ########################## #
# Simple token rules follow: #
# ########################## #

# punctuation
t_LPAREN =  r'\('
t_RPAREN =  r'\)'
t_COLON =   r':'
t_COMMA =   r','

# relational operators
t_EQUALS =  r'=='
t_LTE =     r'<='
t_GTE =     r'>='
t_LT =      r'<'
t_GT =      r'>'

# binary arithmetic operators
t_PLUS =    r'\+'
t_MINUS =   r'-'
t_TIMES =   r'\*'
t_DIVIDED_BY = r'/' # I know it's not the name of the token, but it's a
                    # good mnemonic, and it makes production rules
                    # read more naturally

# binary boolean operators
t_AND =     r'&&'
t_OR =      r'\|\|'

# unary boolean operator
t_NOT =     r'!'

# assignment operator
t_ASSIGN =  r'='

# boolean primitives
t_TRUE =    r'True'
t_FALSE =   r'False'

# This helper rule defines which lexemes we ignore
t_ignore = ' \t'

# ########################## #
# Token action rules follow: #
# ########################## #

# This function identifies keywords and issues the appropriate
# tokens (e.g., 'body' => 'BODY', or ',' => 'COMMA') -- *or*, if
# no such keyword has been defined, assumes the token is an (e.g.,
# 'some_var' => 'ID').
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9-]*'
    t.type = reserved.get(t.value, 'ID') # if it's not a keyword, it's an ID
    return t

def t_INT(t):
    r'[-+]?0|([1-9]\d*)'
    t.value = int(t.value)
    return t

def t_FLOAT(t):
    r'([-+]?0?|([1-9]\d*))\.?\d+'
    t.value = float(t.value)
    return t

def t_STRING(t):
    r'["\'][^"\r\n]*["\']'
    t.value = t.value[1:-1]
    return t

def t_ONE_LINE_COMMENT(t):
    r'(\#.*$)|(//.*$)'
    pass

def t_MULTI_LINE_COMMENT(t):
    r'/\*(.|[\n\r])*?\*/'
    pass

# This allows us to track line numbers.
# Since it's not a rule -- but rather a kind of helper -- we do not capitalize
# it's identifier.
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)  # counts how many new lines and adds that
                                    # number to current lineno

# This helper rule defines what we do when we encounter a lexing error
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

def find_column(input,token):
    """
    This helper function computes the column at which the current token begins.
    This is super useful for error-handling. Here 'input' is the input text
    string and 'token' is a token instance.
    """
    last_cr = input.rfind('\n',0,token.lexpos)
    if last_cr < 0:
        last_cr = 0
        column = (token.lexpos - last_cr) + 1
    return column

"""
LEXER API

These are some useful methods for sanity-checking basic aspects of the
lexer. They can be run from the top-level (e.g., at the bottom of this
file) to get an idea at a glance of whether anything is horribly broken.
"""

def lex_print(filename, paged=True):
    """
    Attempts to open the file specified by the supplied path ('filename'),
    then reads the file in as a string, lexes it, and prints the lexed output
    in paged format (if paged is left True) -- or not (if paged is set to
    False).

    TODO: add error handling -- in particular against the case where the file-
    name is invalid or the specified file doesn't exist.
    """

    # try to read the supplied file
    input = ''
    with open(filename, 'r') as f:
        input = f.read()
    global_meth_lexer_instance.input(input)

    # lex the file and aggregate the output
    output = ''
    while True:
        tok = global_meth_lexer_instance.token()
        if not tok:
            break
        output += (tok.__repr__() + '\n')
    output += '\n'

    # print the output
    if paged:
        pager(output)
    else:
        print(output)

# some aliases for the above function, for Ruby-like happiness convenience:
print_token_stream = lex_print

"""
Create a global lexer instance.
Other modules should get their lexer from here, to avoid building
unnecessary finite automata.
"""
# global_meth_lexer_instance = lex.lex(optimize=1,lextab="meth_test_tab")
global_meth_lexer_instance = lex.lex()

def get_lexer():
    return global_meth_lexer_instance
