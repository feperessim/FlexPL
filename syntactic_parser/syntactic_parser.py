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

import sys
sys.path.append("..")
import ply.yacc as yacc
from lexical_parser.lexical_parser import tokens
from abstract_syntax_tree.ast import *
from semantical_parser.semantical_parser import *
from assembly_generator.asm_generator import AsmGen

precedence = (
   ('nonassoc', 'LESS_THAN', 'GREATER_THAN'),  # Nonassociative operators
   ('nonassoc', 'LESS_EQUAL', 'GREATER_EQUAL'),  # Nonassociative operators
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'MOD'),
    ('right', 'UMINUS'),            # Unary minus operator
)

# Initial Rule
def p_program(p):
   '''program : function_definition program
              | class_definition program
              | function_call
              | empty'''
   if len(p) == 3:
      p[0] = Program(p[1], p[2])
   else:
      p[0] = p[1]
   pass

 
def p_class_definition(p):
   ''' class_definition : DEFINE CLASS ID LPAREN RPAREN LBRACE program RBRACE'''
   p[0] = ClassDefinition(p[3], p[7])
   pass

# Function definition
def p_function_definition(p):
    '''function_definition : DEFINE data_type ID LPAREN function_definition_args RPAREN block'''
    p[0] = FunctionDefinition(p[2], p[3], p[5], p[7], p.lineno(2), p.lexpos(2))
    pass

# Arguments that goes inside a function definition
def p_function_definition_args(p):
    '''function_definition_args : var_list
                                | empty'''
    p[0] = p[1]
    pass

# list of declaration of variables or a single variable
def p_var_list(p):
    '''var_list : var_declaration COMMA var_list
                | var_declaration'''
    if len(p) >= 3:
        p[0] = VarList(p[1], p[3])
    else:
        p[0] = p[1]
    pass

# declaration of var
def p_var_declaration(p):
   'var_declaration : data_type ID'
   p[0] = VarDeclaration(p[1], p[2], p.lineno(2), p.lexpos(2))
   pass

# data types for variables 
def p_data_type(p):
    '''data_type : VOID 
                 | INT 
                 | FLOAT 
                 | STRING 
                 | CHAR'''
    p[0] = DataType(p[1])
    pass

def p_function_call(p):
   '''function_call : ID LPAREN function_call_args RPAREN'''
   p[0] = FunctionCall(p[1], p[3], p.lineno(2), p.lexpos(2))
   pass

def p_function_call_args(p):
    '''function_call_args : parameter_list
                          | empty'''
    p[0] = p[1]
    pass

def p_function_call_parameter_list(p):
   '''parameter_list : expression COMMA parameter_list
                     | expression'''
   if len(p) > 2:
      p[0] = ParameterList(p[1], p[3])
   else:
      p[0] = p[1]

   
# block - a block is enclosed by braces {stmt}
def p_block(p):
   'block : LBRACE statements RBRACE'
   p[0] = Block(p[2])
   pass

def p_statements(p):
   '''statements : statement statements
                 | empty'''
   if len(p) >= 3:
      p[0] = Statements(p[1], p[2])
   else:
      p[0] = Node("EMPTY", [])
   pass

# statement is either a compound statement or a simple statement
def p_statement(p):
   '''statement : matched_statement
                | unmatched_statement'''
   p[0] = p[1]
   pass

# Matched Statement - This is used to deal with If ambiguity
def p_matched_statement(p):
   ''' matched_statement : IF LPAREN logical_expression RPAREN matched_statement ELSE matched_statement 
                         | WHILE LPAREN logical_expression RPAREN matched_statement
                         | FOR LPAREN assignment SEMI_COLON logical_expression SEMI_COLON assignment RPAREN matched_statement 
                         | return_statement SEMI_COLON
                         | compound_statement SEMI_COLON
                         | simple_statement SEMI_COLON
                         | block'''
   if len(p) >= 9:
      p[0] = ForStatement(p[3], p[5], p[7], p[9])
   elif len(p) == 8:
      p[0] = IfElseStatement(p[3], p[5], p[7])
   elif len(p) == 6:
      p[0] = WhileStatement(p[3], p[5])
   else:
      p[0] = p[1]
   pass

# Unmateched statement - This is used to deal with If ambiguity 
def p_unmatched_statement(p):
   ''' unmatched_statement : IF LPAREN logical_expression RPAREN matched_statement 
                           | IF LPAREN logical_expression RPAREN matched_statement ELSE unmatched_statement '''
   if len(p) == 7:
      p[0] = IfElseStatement(p[3], p[5], p[6])
   else:
      p[0] = IfStatement(p[3], p[5])
   pass

# Logical expression OR
def p_logical_expression_or(p):
   'logical_expression : logical_term OR logical_term'
   p[0] = BinaryOp(p[1], p[2], p[3])
   pass

# Logical expression term
def p_logical_expression_term(p):
   'logical_expression : logical_term'
   p[0] = p[1]
   pass

# Logical expression AND
def p_logical_term_and(p):
   'logical_term : logical_factor AND logical_factor'
   p[0] = BinaryOp(p[1], p[2], p[3])
   pass

# Logical expression factor
def p_logical_term_factor(p):
   'logical_term : logical_factor'
   p[0] = p[1]
   pass

# Logical expression NOT, boolean or another logical expression enclosed by parens
def p_logical_factor(p):
   '''logical_factor : boolean_statement
                     | NOT logical_factor
                     | LPAREN logical_expression RPAREN'''
   if len(p) == 4:
      p[0] = BinaryOp(p[1], p[2], p[3])
   elif len(p) == 3:
      p[0] = NotExpression(p[2])
   else:
      p[0] = p[1]
   pass

# boolean_statement
def p_boolean_statement(p):
   '''boolean_statement : value comparison_op value
                        | value'''
   if len(p) == 4:
      p[0] = BinaryOp(p[1], p[2], p[3])
   else:
      p[0] = p[1]
   pass


def p_value(p):
   ''' value : ID
             | number'''
   p[0] = p[1]
   pass

def p_number(p):
   '''number : int
             | float'''
   p[0] = Number(p[1])
   pass

def p_int(p):
   'int : INTCONST'
   p[0] = Const('int', p[1])
   pass

def p_float(p):
   'float : FLOATCONST'
   p[0] = Const('float', p[1])
   pass
   
def p_comparison_op(p):
   '''comparison_op : LESS_THAN
                    | LESS_EQUAL
                    | GREATER_THAN
                    | GREATER_EQUAL
                    | EQUAL
                    | NOT_EQUAL'''
   p[0] = p[1]
   pass

# Compound statement is a while or for or do while or switch case
def p_compound_statment(p):
   '''compound_statement : var_list
                         | assignment'''
   p[0] = p[1]
   pass

# A simple statement is a declaration, or 
def p_simple_statement(p):
   '''simple_statement : expression'''
   p[0] = p[1]
   pass

# Production for atrribution
def p_assignment(p):
    '''assignment  : var_declaration EQUALS expression 
                   | var_declaration EQUALS string
                   | var_declaration EQUALS char
                   | ID EQUALS expression
                   | ID EQUALS string
                   | ID EQUALS char'''
    p[0] = Assignment(p[1], p[3], p.lineno(3), p.lexpos(3))
    pass

def p_string(p):
   'string : STRINGCONST'
   p[0] = Const('string', p[1])
   pass

def p_char(p):
   'char : CHARCONST'
   p[0] = Const('char', p[1])
   pass

# Gramatical rules for expressions
def p_expression_plus(p):
    'expression : expression PLUS term'
    p[0] = BinaryOp(p[1], p[2], p[3])
    pass

def p_expression_minus(p):
    'expression : expression MINUS term'
    p[0] = BinaryOp(p[1], p[2], p[3])
    pass

def p_expression_term(p):
   'expression : term'
   p[0] = p[1]
   pass

def p_term_times(p):
   'term : term TIMES factor'
   p[0] = BinaryOp(p[1], p[2], p[3])
   pass

def p_term_div(p):
   'term : term DIVIDE factor'
   p[0] = BinaryOp(p[1], p[2], p[3])
   pass

def p_term_mod(p):
   'term : term MOD factor'
   p[0] = BinaryOp(p[1], p[2], p[3])
   pass
 
def p_term_factor(p):
   'term : factor'
   p[0] = p[1]
   pass

def p_factor_num(p):
   '''factor : number 
             | ID 
             | factor_expr
             | function_call'''
   p[0] = p[1]
   pass

def p_factor_expr(p):
   'factor_expr : LPAREN expression RPAREN'
   p[0] = p[2]
   pass

def p_uminus_expr(p):
   'uminus_expression : MINUS LPAREN expression RPAREN %prec UMINUS'
   pass
 
# The empty production
def p_empty(p):
   'empty :'
   p[0] = None #Node("EMPTY", [])
   pass

# Return statement1
def p_return_statement(p):
   'return_statement : RETURN expression'
   p[0] = ReturnStatement(p[2])
   pass

# Error rule for syntax errors
def p_error(p):
   if p:
      print("Syntax error at token", p.type)
      print("Syntax error at '%s'" % p.value)
      print("line : '%s'" % p.lineno)
      print("column: '%s'" % p.lexpos)
      #print("Syntax error in input!")
      #parser.errok()
   else:
      print("Syntax error at EOF")
      
def p_function_definition_error(p):
   '''function_definition : DEFINE data_type ID LPAREN function_definition_args RPAREN error'''
   print("Syntax error in function statement at '%s'" % p)
   #print('Line' + str(p.linespan(1)))
   
#parser = yacc.yacc()
#from read_file_into_buffer import readFileIntoBuffer
#data = readFileIntoBuffer('while.fpl')
#ast = parser.parse(data, tracking=True)
#s = SemanticalAnalyzer(ast)
#s.runSemanticalParser()
#a = AsmGen(ast)
#a.runGenerator()
#result = parser.parse('define int function (int a) 2 ', tracking=True)

#while True:
#  try:x
#       s = input('input > ')
#   except EOFError:
#      break
#  if not s: continue
#  result = parser.parse(s)
#  print(result)
