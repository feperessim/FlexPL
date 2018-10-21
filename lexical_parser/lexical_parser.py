'''
Copyright (C) 2018 Felipe de Lima Peressim
 
  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.
 
  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.
 
  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

# Flex-pl language compiler
# This is part of Flex-pl compiler
# Author: Felipe de Lima Peressim

import ply.lex as lex
import ply.yacc as yacc


# Reserved words
reserved = {
    'if' : 'IF',
    'else' : 'ELSE',
    'while' : 'WHILE',
    'for' : 'FOR',
    'switch' : 'SWITCH',
    'case' : 'CASE',
    'class' : 'CLASS',
    'define' : 'DEFINE',
    'int' : 'INT',
    'float' : 'FLOAT',
    'char' : 'CHAR',
    'string' : 'STRING',
    'void' : 'VOID',
    'equal' : 'EQUAL',
    'and' : 'AND',
    'or' : 'OR',
    'not' : 'NOT',
    'do' : 'DO',
    'return' : 'RETURN',
}

# The tokens declaration is made here.
tokens = [

    # Literals (identifier, integer constant, float constant, string constant,
    # char const)
    'ID',
    #'NUMBER',

    # Operators +,-,*,/,%
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',
    'MOD',

    # Logical Operators
    'LESS_THAN',
    'LESS_EQUAL',
    'GREATER_THAN',
    'GREATER_EQUAL',
    'NOT_EQUAL',
    
    # Delimeters such as (),{},[],:
    'LPAREN',
    'RPAREN',
    'LBRACE',
    'RBRACE',
    'COLON',
    'COMMA',
    'SEMI_COLON',

    #Assignment Operators
    'EQUALS',

    # Integer literal
    'INTCONST',
    # Floating literal
    'FLOATCONST',
    # String literal
    'STRINGCONST',
    # Character constant 'c' or L'c'
    'CHARCONST'
] 

tokens +=  list(reserved.values())

# Regular expression rules for simple tokens
#t_NUMBER  = r'\d+'

# Operators
t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIVIDE  = r'/'
t_MOD     = r'\%'

# Logical Operators
t_LESS_THAN     = r'<'
t_LESS_EQUAL    = r'<=' 
t_GREATER_THAN  = r'>'
t_GREATER_EQUAL = r'>='
t_NOT_EQUAL     = r'!='

# Delimiters
t_LPAREN     = r'\('
t_RPAREN     = r'\)'
t_COLON      = r'\:'
t_LBRACE     = r'\{'
t_RBRACE     = r'\}'
t_COMMA      = r','
t_SEMI_COLON = R';'

# Assignment
t_EQUALS  = r'='


# Integer literal
t_INTCONST = r'\d+'

# Floating literal
t_FLOATCONST = r'\d+[.]\d+'

# String literal
t_STRINGCONST = r'\"([^\\\n]|(\\.))*?\"'

# Character constant 'c' or L'c'
t_CHARCONST = r'\'([^\\\n]|(\\.))*?\''


# Rule for identificator
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value,'ID')    # Check for reserved words
    return t

# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Compute column.
#     input is the input text string
#     token is a token instance
def find_column(input, token):
    line_start = input.rfind('\n', 0, token.lexpos) + 1
    return (token.lexpos - line_start) + 1

# A string containing ignored characters (spaces and tabs)
t_ignore  = ' \t'

# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# One line comments Python alike
def t_comment(t):
    r"[ ]*\043[^\n]*"  # \043 is '#'
    pass

# Build the lexer
#lexer = lex.lex()

lex.lex()

if __name__ == '__main__':
    lex.runmain()

# read input for test purposes
#from read_file_into_buffer import readFileIntoBuffer    
#data = readFileIntoBuffer('test.fpl')
#data = input()

# feed lexer with input
#lexer.input(data)

# TODO - Create a function to open a file from stdinput
# The file shall be passed as argument


# Tokenize
#while True:
#    tok = lexer.token()
#    if not tok: 
#        break      # No more input
#    print(tok)


