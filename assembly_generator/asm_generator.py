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
from abstract_syntax_tree.ast import *

class X8632AsmInstructionsGnuSyntax():
    def __init__(self):
        self.loopLabelCount = 0
        self.labelCount = 0
        self.elseLabel = []

    def move(self, fr, to):
        return "movl " + fr + ", " + to + "\n"
    # used for if statement, not a meaningful name
    def exitLabel(self, whileLabel=False):
        if whileLabel:
            label = "exit_loop_" + str(self.loopLabelCount)
        else:
            label = "exit_label_"+ str(self.labelCount)
        return label

    def startLoopLabel(self):
        label = "start_loop_" + str(self.loopLabelCount)
        return label
    
    def __getElseLabel__(self):
        return self.elseLabel.pop()

    def __setElseLabel__(self, label):
        self.elseLabel.append(label)

    
class AsmGen():
    def __init__(self, ast):
        self.ast = ast
        self.sectionData = ''
        self.sectionText = ''
        self.statements = ''
        self.expressions = ''
        self.data = ''
        self.registerCounter = 0
        self.registers = {'eax': 0, 'ebx': 0, 'ecx': 0, 'edx': 0, 'edi' : 0}
        self.instruction = X8632AsmInstructionsGnuSyntax()
        self.varPosition = {}
        self.parameterCounter = 0
        self.localVarCounter = -1
        
    def __resetLocalVars__(self):
        self.localVarsBytePosition = {}
        
    def __resetRegisters__(self):
        for key in self.registers:
            self.registers[key] = 0
            
    def setVarPosition(self, var, position):
        self.varPosition[var] = position

    def getVarPosition(self, var):
        return self.varPosition[var]

    def __resetVarPosition__(self):
        self.varPosition = {}
    
    def getParameterCounter(self):
        return self.parameterCounter

    def __resetParameterCounter__(self):
        self.parameterCounter = 0
        
    def addVarToSectionData(self, var):
        self.sectionData += var.varName + ':\n'
        dataType = var.dataType.dtype
        if dataType  == 'int':
            pass
    def getNoBusyRegister(self):
        # need to fix the return at the end
        for key in self.registers:
            if self.registers[key] == 0:
                return key
        return '%edi'
        
    def runGenerator(self):
        if self.ast is None:
            print('Something goes wrong - abstract syntax tree is empty!')
            print('Error - Abstract syntax tree is empty')
            return None
        self.__generator__(self.ast)

    def __generator__(self, ast):
        
        if ast is None:
            print(self.data)
       
        elif isinstance(ast, Program):
            if isinstance(ast.scope, FunctionDefinition):
                self.__visitFunctionDefinition__(ast.scope)
            self.__generator__(ast.anotherScope)

        elif isinstance(ast, Statements):
            self.__generator__(ast.statement)
            self.__generator__(ast.moreStatements)
            
        elif isinstance(ast, Block):
            self.__generator__(ast.statements)
            
        elif isinstance(ast, Assignment):
            self.__visitAssignment__(ast)
            
        elif isinstance(ast, VarDeclaration):
            self.__visitVarDeclaration__(ast)

        elif isinstance(ast, VarList):
            self.__visitVarList__(ast)

        elif isinstance(ast, ClassDefinition):
            self.__visitClassDefinition__(ast)

        elif isinstance(ast, IfElseStatement):
            self.__visitIfElseStatement__(ast)
            
        elif isinstance(ast, IfStatement):
            self.__visitIfStatement__(ast)

        elif isinstance(ast, FunctionCall):
            r = self.__visitFunctionCall__(ast)
            self.data += 'call ' + ast.functionName + "\n"
            self.data += "addl $" + str(self.getParameterCounter()*4) + ", %esp" + "\n"
            self.data += 'movl 8(%ebp), %' + r + "\n"
            return r
            
        elif isinstance(ast, ReturnStatement):
            if ast.expression is not None:
                r = self.__visitBinaryOp__(ast.expression)
                # may remove it
                if (not isinstance(ast.expression, FunctionCall)):
                    self.data += 'movl  %' + r + ",  %eax" "\n"
                else:
                    self.data += 'movl  %eax, %' + r + "\n"
                return r

        elif isinstance(ast, WhileStatement):
            self.__visitWhileStatement__(ast)

        elif isinstance(ast, ForStatement):
            self.__visitForStatement__(ast)
            
                
    def __visitFunctionDefinition__(self, function):
        functionName = function.functionName
        self.data += ".type " + functionName + ", @function\n" + functionName + ":\n\n"
        self.data += "pushl %ebp\n"
        self.data += "movl %esp, %ebp\n\n"
        # movl 8(%ebp), %eax" ainda é necessário mover os valores para usá-los nas computações
        block = function.scope
        varList = function.arguments
        if varList:
            self.__visitVarList__(varList, formalParameter=True)
        self.__generator__(block.statements)
        self.data += "movl %eax, %ebx" + "\n"
        self.data += "movl %ebp, %esp" + "\n"
        self.data += "popl %ebp" + "\n"
        self.data += "ret" + "\n\n"
        
        self.__resetParameterCounter__()
        self.__resetRegisters__()
        self.__resetLocalVars__()
        self.__resetVarPosition__()

    def __visitAssignment__(self, assignment):
        # The left hand side of attribution has a variable declaration
        if isinstance(assignment.var, VarDeclaration):
           self.__visitVarDeclaration__(assignment.var)
           if assignment.value is not None:
               r = self.__visitBinaryOp__(assignment.value)
               varPosition = self.getVarPosition(assignment.var.varName)
               self.data += "movl %" + r + "," + str(varPosition) + "(%ebp)\n"
               self.registers['eax'] = 0
               return r
            # Check whether the variable is already declared and insert it to symbol table
            #TODO - PUSH TO STACK FINAL RESULT
        
        if isinstance(assignment.value, BinaryOp):
            binaryOp = assignment.value
            r = '%' + self.__visitBinaryOp__(binaryOp)
                   
        elif isinstance(assignment.value, Const):
            dtype = assignment.value.dtype
            const = assignment.value
            self.data += "movl" + "$" + const.value + ", %eax"
            r = '%eax'
            
        elif isinstance (assignment.value, str):
            # Here the right side might be a variable
            # if it is we just get its position
            # otherwise it is a string or a char value
            # which is not generated the assembly to
            #by this compiler yet.
            if assignment.value in self.varPosition:
                varPosition = self.getVarPosition(assignment.value)
                v = str(varPosition) + "(%ebp)"
                r = self.getNoBusyRegister()
                self.data += "movl " + v + ", %" + r + "\n"
                self.registers[r] = 1
                if '%' not in r:
                    r = '%' + r
            else:
                r = assignment.value
            
          
        elif isinstance (assignment.value, Number):
            r = '$' + assignment.value.value.value
            pass
        
        if isinstance (assignment.var, str):
            varPosition = self.getVarPosition(assignment.var)
            self.data += "movl " + r + ", " + str(varPosition) + "(%ebp)" + "\n"
            self.registers[r]  = 1
        
    def __visitVarDeclaration__(self, varDeclaration, formalParameter=False):
        # If it is not a formal parameter it is a local var
        if formalParameter:
            self.parameterCounter += 1
            self.setVarPosition(varDeclaration.varName, self.parameterCounter*4 + 4)
        else:
            self.localVarCounter += 1
            self.data += "subl $4, %esp\n"
            self.setVarPosition(varDeclaration.varName, -self.localVarCounter*4 - 4)
    
    def __visitBinaryOp__(self, binaryOp):
        if isinstance(binaryOp, BinaryOp):
            tmp = ''
            r = self.__visitBinaryOp__(binaryOp.left)
            self.registers[r] = 1
            r1 = self.__visitBinaryOp__(binaryOp.right)

            if r is None:
                print(type(binaryOp.left))
                
            if "(%ebp)" in r:
                percentLeft = ''
            else:
                percentLeft = "%"
            if "(%ebp)" in r1:
                percentRight = ''
            else:
                percentRight = "%"

            if binaryOp.op == '+':
                tmp += "addl " + percentLeft + r +  ", " + percentRight + r1 + "\n"
                tmp += "movl " + percentRight + r1 + ", " + percentLeft + r + "\n"
            elif binaryOp.op == '-':
                tmp += "subl " +  percentRight + r1 + ", " + percentLeft +  r + "\n"
                tmp += "movl " + percentLeft + r   + ", " + percentRight + r1 + "\n"
            elif binaryOp.op == '*':
                tmp += "imull " +  percentLeft + r + ", " + percentRight + r1 + "\n"
                tmp += "movl "+ percentRight + r1 + ", " + percentLeft + r + "\n"
            elif binaryOp.op == '/':
                tmp += "movl "+ percentLeft + r + ", %eax"  + "\n"
                tmp += "movl "+ percentRight + r1 + ", %ebx"  + "\n"
                tmp += "movl $0, %edx" + "\n"
                tmp += "idivl %ebx" +  "\n"
                r = 'eax'
            elif binaryOp.op == '%':
                tmp += "movl "+ percentLeft + r + ", %eax"  + "\n"
                tmp += "movl "+ percentRight + r1 + ", %ebx"  + "\n"
                tmp += "movl $0, %edx" + "\n"
                tmp += "idivl %ebx" +  "\n"
                r = 'edx'
            elif binaryOp.op == 'equal':
                tmp += "cmpl "+ percentLeft + r + ", " + percentRight + r1 + "\n"
                tmp += "jne " + self.instruction.exitLabel() + "\n"
                self.__resetRegisters__()
            elif binaryOp.op == '>':
                tmp += "cmpl "+ percentRight + r1 + ", " + percentLeft + r  + "\n"
                tmp += "jle " + self.instruction.exitLabel() + "\n"
                self.__resetRegisters__()
            elif binaryOp.op == '<':
                tmp += "cmpl "+ percentRight + r1 + ", " + percentLeft + r  + "\n"
                tmp += "jge " + self.instruction.exitLabel() + "\n"
                self.__resetRegisters__()
            elif binaryOp.op == '>=':
                tmp += "cmpl "+ percentRight + r1 + ", " + percentLeft + r  + "\n"
                tmp += "jl " + self.instruction.exitLabel() + "\n"
                self.__resetRegisters__()
            elif binaryOp.op == '<=':
                tmp += "cmpl "+ percentRight + r1 + ", " + percentLeft + r  + "\n"
                tmp += "jg " + self.instruction.exitLabel() + "\n"
                self.__resetRegisters__()
            elif binaryOp.op == '!=':
                tmp += "cmpl "+ percentLeft + r + ", " + percentRight + r1 + "\n"
                tmp += "je " + self.instruction.exitLabel() + "\n"
                self.__resetRegisters__()
            self.data += tmp
            self.registers[r1] = 0
            return r
        
        elif isinstance(binaryOp, Number):
            if binaryOp.value.dtype == 'int':
                num = binaryOp.value.value
                if self.registers['eax']  == 0:
                    r = 'eax'
                elif self.registers['ebx']  == 0:
                    r = 'ebx'
                elif self.registers['ecx']  == 0:
                    r = 'ecx'
                else:
                    r = 'edx'
                    self.__resetRegisters__()
                self.data += "movl " + "$" + num + ",%" + r  + "\n"
                self.registers[r]  = 1
                return r
            else:
                pass
        elif (isinstance(binaryOp, str)):
            varPosition = self.getVarPosition(binaryOp)
            if self.registers['eax']  == 0:
                r = 'eax'
            elif self.registers['ebx']  == 0:
                r = 'ebx'
            elif self.registers['ecx']  == 0:
                r = 'ecx'
            else:
                r = 'edx'
            self.data += "movl " + str(varPosition) + "(%ebp)" + ", %" + r  + "\n"
            self.registers[r]  = 1
            return r
        
        elif isinstance(binaryOp, FunctionCall):
            return self.__generator__(binaryOp)
        else:
            #TODO
            pass
                
    def __visitVarList__(self, varList, formalParameter=False):
        if not varList:
            pass
        if isinstance(varList, VarDeclaration):
            self.__visitVarDeclaration__(varList, formalParameter)
        else:
            self.__visitVarList__(varList.varDeclaration, formalParameter)
            self.__visitVarList__(varList.varList, formalParameter)
            

    def __visitIfStatement__(self, ifStatement, needElseLabel = False):
        if isinstance (ifStatement.logicalExpression, BinaryOp):
            self.__visitBinaryOp__(ifStatement.logicalExpression)    
        label = self.instruction.exitLabel()
        self.instruction.labelCount += 1
        self.__generator__(ifStatement.scope)
        if needElseLabel:
            self.data += "jmp else_" + label + "\n"
            elseLabel = "else_" + label+ ":\n" 
            self.instruction.__setElseLabel__(elseLabel)
        self.data += label + ":\n"

    def __visitIfElseStatement__(self, ifElseStatement):
        label = self.instruction.exitLabel()
        self.__visitIfStatement__(ifElseStatement, True)
        self.__generator__(ifElseStatement.elseScope)
        self.data += self.instruction.__getElseLabel__()
    
    def  __visitFunctionCall__(self, functionCall):
        # push values to formal parameters
        tmp = ''
        if isinstance(functionCall, FunctionCall):
            if functionCall.args is not None:
                if isinstance (functionCall.args, ParameterList):
                    self. __visitFunctionCall__(functionCall.args.parameterList)
                    r = self. __visitBinaryOp__(functionCall.args.expression)
                    tmp += 'pushl %' + r + "\n"
                else:
                    if isinstance(functionCall.args, BinaryOp):
                        r = self. __visitBinaryOp__(functionCall.args)
                        tmp += 'pushl %' + r + "\n"
                    elif isinstance(functionCall.args, Number):
                            r = self. __visitBinaryOp__(functionCall.args)
                            tmp += 'pushl %' + r + "\n"
                    elif isinstance(functionCall.args, str):
                            r = self. __visitBinaryOp__(functionCall.args)
                            tmp += 'pushl %' + r + "\n"        
                    elif functionCall.args.expression is not None:
                        r = self. __visitBinaryOp__(functionCall.args.expression)
                        tmp += 'pushl %' + r + "\n"
        elif isinstance (functionCall, ParameterList):
            if functionCall.parameterList is not None:
                r = self. __visitBinaryOp__(functionCall.parameterList)
                tmp += 'pushl %' + r + "\n"
            if functionCall.args.expression is not None:
                r1 = self. __visitBinaryOp__(functionCall.expression)
                tmp += 'pushl %' + r1 + "\n"
        else:
            if functionCall is not None:
                r = self. __visitBinaryOp__(functionCall)
                tmp += 'pushl %' + r + "\n"
        self.data += tmp
        return r

    def __visitWhileStatement__(self, whileStatement):
        startLabel =  self.instruction.startLoopLabel() 
        exitLabel  = self.instruction.exitLabel()
        self.instruction.loopLabelCount += 1
        self.data += startLabel + ":\n"
        self.__visitBinaryOp__(whileStatement.logicalExpression)
        self.instruction.labelCount += 1
        self.__generator__(whileStatement.scope)
        self.data += 'jmp ' +  startLabel + "\n"
        self.data += exitLabel + ":\n"

    def __visitForStatement__(self, forStatement):
        self.__generator__(forStatement.varDeclaration)
        startLabel =  self.instruction.startLoopLabel()
        exitLabel  = self.instruction.exitLabel()
        self.instruction.loopLabelCount += 1
        self.data += startLabel + ":\n"
        self.__visitBinaryOp__(forStatement.logicalExpression)
        self.instruction.labelCount += 1
        self.__generator__(forStatement.scope)
        self.__generator__(forStatement.attribution)
        self.data += 'jmp ' +  startLabel + "\n"
        self.data += exitLabel + ":\n"
