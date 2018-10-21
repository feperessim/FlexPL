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
from syntactic_parser.syntactic_parser import *
from assembly_generator.asm_generator import AsmGen
from read_file_into_buffer import readFileIntoBuffer

parser = yacc.yacc()
data = readFileIntoBuffer('fatorial_iterativo.fpl')
ast = parser.parse(data, tracking=True)
if ast:
    s = SemanticalAnalyzer(ast)
    if s:
        s.runSemanticalParser()
        if not s.error:
            a = AsmGen(ast)
            a.runGenerator()
        
        
