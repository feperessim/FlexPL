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

# -*- coding: utf-8 -*-
"""
Created on Fri Apr 27 08:27:02 2018

@author: Felipe
"""
# TODO
# When a char, or string type is declared unitialized it is being allowed to used in expression they shouldn't
# e.g : int foo; char bar = 1 + foo * 8;
# Needs to visit NotExpression
# Need to count the number of formal parameters and check its type
    
# Scope with function and Classes
class ScopedSymbolTable():
    def __init__(self, name='None', instance=None, level=0):
        self.globalScope = {}
        self.name = name
        self.instance = instance
        self.level=level

    def insertScope(self, scope):
        self.globalScope[scope.name] = scope
        
    def lookup(self, name):
        # 'symbol' is either an instance of the Symbol class or None
        symbol = self.globalScope.get(name)
        if symbol is not None:
            return symbol
        return None     

class Scope():
    def __init__(self, previousScope=None, name="Global", level=1, instance=None):
        self.previousScope = previousScope
        self.level = level
        self.name = name
        self.instance = instance
        self.scopes = []
        self.symbols = {}        
        
    def insertScope(self, scope):
        self.scopes.append(scope)
        
    def insertSymbol(self, symbol):
        self.symbols[symbol.name] = symbol

    def lookup(self, name, currentScopeOnly=False):
        # 'symbol' is either an instance of the Symbol class or None
        symbol = self.symbols.get(name)
        
        if symbol is not None:
            return symbol

        if currentScopeOnly:
            return None
        
        # recursively go up the chain and lookup the name
        if self.previousScope is not None:
            return self.previousScope.lookup(name)
        
class Symbol():
    def __init__(self, dtype, name, instance, scope=None):
        self.name = name
        self.instance = instance
        self.dtype = dtype
        self.scope = scope

import sys
sys.path.append("..")
from abstract_syntax_tree.ast import *
from .stack import Stack

class SemanticalAnalyzer():
    def __init__(self, ast):
        self.ast = ast
        self.stack = Stack()
        self.symbolTable = ScopedSymbolTable('Global Scope')
        self.globalScope = self.symbolTable
        self.stack.push(self.symbolTable)
        self.currentScope = self.__getCurrentScope__()
        self.error = False
        
    def errorProcedure(self, message=None, obj=None):
        error_message = ''
        if message is not None:
            error_message += message
        if obj is not None:
            error_message += ' at line: ' + str(obj.line) +  " column: " + str(obj.column) + '\n'
        if error_message:
            print(error_message)
        self.error = True
        
    def __getCurrentScope__(self):
        if not self.stack.isEmpty():
            return self.stack.peek()
        else:
            return None

    def runSemanticalParser(self):
        if self.ast is None:
            print('Error - Abstract syntax tree is empty')
            return None
        self.__parser__(self.ast)

    def __parser__(self, ast):
        if ast is None:
            if not self.stack.isEmpty():
                self.stack.pop()
            else:
                pass
            
        elif isinstance(ast, Program):
            if isinstance(ast.scope, FunctionDefinition):
                self.__visitFunctionDefinition__(ast.scope)
            if isinstance(ast.scope, ClassDefinition):
                self.__parser__(ast.scope)
            self.__parser__(ast.anotherScope)

        elif isinstance(ast, Statements):
            self.__parser__(ast.statement)
            self.__parser__(ast.moreStatements)
            
        elif isinstance(ast, Block):
            self.__parser__(ast.statements)
            
        elif isinstance(ast, Assignment):
            self.__visitAssignment__(ast)
            
        elif isinstance(ast, VarDeclaration):
           self.__visitVarDeclaration__(ast)

        elif isinstance(ast, VarList):
           self.__visitVarList__(ast)

        elif isinstance(ast, FunctionCall):
            self.__visitFunctionCall__(ast)

        elif isinstance(ast, ClassDefinition):
            self.__visitClassDefinition__(ast)
            
        elif isinstance(ast, IfElseStatement):
            self.__parser__(ast.logicalExpression)
            self.__parser__(ast.scope)
            self.__parser__(ast.elseScope)
            
        elif isinstance(ast, IfStatement):
            self.__parser__(ast.logicalExpression)
            self.__parser__(ast.scope)

        elif isinstance(ast, ReturnStatement):
            if ast.expression is not None:
                self.__visitBinaryOp__(ast.expression)

        elif isinstance(ast, WhileStatement):
            whileStatement = ast
            self.__visitBinaryOp__(whileStatement.logicalExpression)
            self.__parser__(whileStatement.scope)

        elif isinstance(ast, ForStatement):
            forStatement = ast
            self.__parser__(forStatement.varDeclaration)
            self.__visitBinaryOp__(forStatement.logicalExpression)
            self.__parser__(forStatement.scope)
            self.__parser__(forStatement.attribution)

        elif isinstance(ast, NotExpression):
            self.__parser__(ast.right)
            
    def __visitFunctionDefinition__(self, function):
        # If the function already exists, then trow an error
        try:
            if self.symbolTable.lookup(function.functionName):
                self.errorProcedure("Error: Redefinition of function  " + function.functionName, function)
        except:
            exit()
        else:
            # If the function does not exist
            # create a scope to it and push to
            # the stack. Push the list of variables
            # to the symbol table at the stack    
            functionName = function.functionName
            currentScope = self.__getCurrentScope__()    
            newScope = Scope(currentScope, functionName, instance=function)
            block = function.scope
            varList = function.arguments
            function.formalParameterCounter = self.__formalParameterCounter__(varList)
            function.formalParameterTypeList = self.__makeformalParameterList__(varList)
            self.symbolTable.insertScope(newScope)
            self.stack.push(newScope)
            # The variable list isn't empty
            if varList:
                self.__parser__(varList)
            self.__parser__(block.statements)
            if not self.stack.isEmpty():
                self.stack.pop()
            
    def __visitAssignment__(self, assignment):
        currentScope = self.__getCurrentScope__()
        # To verify whether the types of attribution agree
        leftType = ''
        rightType = ''
        # The left hand side of attribution has a variable declaration
        if isinstance(assignment.var, VarDeclaration):
            # Check whether the variable is already declared and insert it to symbol table
            self.__parser__(assignment.var)
            leftType = assignment.var.dataType.dtype
            # A value was assigned to the variable in question
            assignment.var.isAssigned = True
        else:
            # The left hand side of attribution has a variable
            # so we need o check if it is declared in some place.
            symbol = currentScope.lookup(assignment.var)
            if not symbol:
                self.errorProcedure("Error: variable '" + assignment.var +  "' not declared", assignment)
            else:
                symbol.instance.isAssigned = True
                leftType = symbol.dtype
        # expression at the right hand side of attribtion
        if isinstance(assignment.value, BinaryOp):
            # The resulting type of the expressions are
            # 1 for int and 2 for float
            resultingType = self.__visitBinaryOp__(assignment.value)
            if resultingType:
                rightType = (lambda x : 'int' if x == 0 else 'float' if x == 1 else 'char or string')(resultingType)
                if rightType:
                    if leftType == 'float' and (rightType == 'float' or rightType == 'int'):
                        pass
                    elif leftType == 'int' and rightType == 'int':
                        pass
                    elif leftType == 'char' and rightType == 'char':
                        pass
                    elif leftType == 'string' and rightType == 'string':
                        pass
                    else:
                        self.errorProcedure(message="Error: Assignment error - Trying to assign " + rightType +  " to " + leftType, obj=assignment)
        elif isinstance(assignment.value, Const):
            rightType = assignment.value.dtype
            if rightType:
                if leftType == 'float' and (rightType == 'float' or rightType == 'int'):
                    pass
                elif leftType == 'int' and rightType == 'int':
                    pass
                elif leftType == 'char' and rightType == 'char':
                        pass
                elif leftType == 'string' and rightType == 'string':
                        pass
                else:
                    self.errorProcedure(message="Error: Assignment error - Trying to assign " + rightType +  " to " + leftType, obj=assignment)
        if isinstance(assignment.value, FunctionCall):
            self.__visitFunctionCall__(assignment.value)
        elif isinstance (assignment.value, str):
            symbol = currentScope.lookup(assignment.value)
            if not symbol:
                self.errorProcedure("Error: Variable '" + assignment.var +  "' not declared")
            else:
                rightType = symbol.dtype
                if rightType:
                    if leftType == 'float' and (rightType == 'float' or rightType == 'int'):
                        pass
                    elif leftType == 'int' and rightType == 'int':
                        pass
                    elif leftType == 'char' and rightType == 'char':
                        pass
                    elif leftType == 'string' and rightType == 'string':
                        pass
                    else:
                        self.errorProcedure(message="Error: Assignment error - Trying to assign " + rightType +  " to " + leftType, obj=assignment)
                    
    def __visitVarDeclaration__(self, varDeclaration):
        currentScope = self.__getCurrentScope__()
        if currentScope.lookup(varDeclaration.varName):
            self.errorProcedure("Error: Redefinition of the variable " + varDeclaration.varName, obj=varDeclaration)
        else:
            varName = varDeclaration.varName
            dtype = varDeclaration.dataType.dtype
            instance = varDeclaration
            symbol = Symbol(dtype, varName, instance)
            currentScope.insertSymbol(symbol)
            
    def __visitBinaryOp__(self, binaryOp):
        if isinstance(binaryOp, BinaryOp):
            return self.__visitBinaryOp__(binaryOp.left) | self.__visitBinaryOp__(binaryOp.right)
        elif isinstance(binaryOp, Number):
            if binaryOp.value.dtype == 'int':
                return 0
            else:
                return 1
        elif isinstance(binaryOp, FunctionCall):
            scope = self.symbolTable.lookup(binaryOp.functionName)
            if not scope:
                self.errorProcedure("Error: Function not declared")
                return -1
            else:
                functionName = binaryOp.functionName
                formalParameterFuncDefLen = self.symbolTable.lookup(functionName).instance.formalParameterCounter
                formalParameterFuncCallLen = self.__formalParameterCounter__(binaryOp.args)
                if formalParameterFuncCallLen < formalParameterFuncDefLen:
                    self.errorProcedure("Error: Too few arguments to function " + functionName, binaryOp)
                elif formalParameterFuncCallLen > formalParameterFuncDefLen:
                    self.errorProcedure("Error: Too many arguments to function " + functionName, binaryOp)
                        
                dtype = scope.instance.dataType
                if type(dtype) == DataType:
                    dtype = dtype.dtype
                if dtype == 'int':
                    return 0
                elif dtype == 'float':
                    return 1
                else: 
                    self.errorProcedure("Error: The type " + dtype + " is not allowed to be used in expressions")
                    return -1
        elif isinstance(binaryOp, NotExpression):
            return self.__visitBinaryOp__(binaryOp.right)
        else:
            currentScope = self.__getCurrentScope__()
            symbol = currentScope.lookup(binaryOp)
            if not symbol:
                self.errorProcedure("Error: Variable '" +  binaryOp + "' is not declared")
                return 0
            else:
                if symbol.dtype == 'int':
                    return 0
                elif symbol.dtype == 'float':
                    return 1
                else:
                    print("Error: The type " + symbol.dtype + " is not allowed to be used in expressions")
                    return -1
            
    def __visitVarList__(self, varList):
        if not varList:
            pass
        if isinstance(varList, VarDeclaration):
            self.__visitVarDeclaration__(varList)
        else:
            self.__visitVarList__(varList.varDeclaration)
            self.__visitVarList__(varList.varList)
               

    def __visitFunctionCall__(self, functionCall):
        if isinstance(functionCall, FunctionCall):
            functionName = functionCall.functionName
            if self.symbolTable.lookup(functionName) is None:
                self.errorProcedure("Error: Function" + functionName + " not declared", functionCall)
            if functionCall.args is not None:
                # if the function call has too few arguments it shall call the error procedure
                # lookup returns an instance of symbol class which has a pointer to a instance
                # to the function into the table.
                formalParameterFuncDefLen = self.symbolTable.lookup(functionName).instance.formalParameterCounter
                formalParameterFuncCallLen = self.__formalParameterCounter__(functionCall.args)
                if formalParameterFuncCallLen < formalParameterFuncDefLen:
                    self.errorProcedure("Error: Too few arguments to function " + functionName, functionCall)
                elif formalParameterFuncCallLen > formalParameterFuncDefLen:
                    self.errorProcedure("Error: Too many arguments to function " + functionName, functionCall)
                self.__checkFunctionCallDataTypeFormalParameters__(functionCall)
                if isinstance (functionCall.args, ParameterList):
                    self. __visitFunctionCall__(functionCall.args.parameterList)
                    self. __visitBinaryOp__(functionCall.args.expression)
                else:
                    if isinstance(functionCall.args, BinaryOp):
                        self. __visitBinaryOp__(functionCall.args)
                    elif isinstance(functionCall.args, Number):
                        self. __visitBinaryOp__(functionCall.args)
                    elif isinstance(functionCall.args, str):
                        self. __visitBinaryOp__(functionCall.args)
                    elif functionCall.args.expression is not None:
                        self. __visitBinaryOp__(functionCall.args.expression)
            elif isinstance (functionCall, ParameterList):
                if functionCall.parameterList is not None:
                    self. __visitBinaryOp__(functionCall.parameterList)
                    if functionCall.args.expression is not None:
                        self. __visitBinaryOp__(functionCall.expression)
            else:
                if functionCall is not None:
                    self. __visitBinaryOp__(functionCall)

    def __visitClassDefinition__(self, ast):
        # TODO verify whether the class is already declared
        className = ast.className
        symbolTable = ScopedSymbolTable(className, ast)
        self.symbolTable = symbolTable
        self.stack.push(symbolTable)
        self.__parser__(ast.scope)
        self.symbolTable = self.globalScope
        self.stack.push(self.symbolTable)
        self.stack.pop()

    def __formalParameterCounter__(self,  parameterList):
        # This function counts the quantity of formal
        # parameters in afunction
        if parameterList is None:
            return 0
        else:
            if isinstance(parameterList, VarList):
                return 1 + self.__formalParameterCounter__(parameterList.varList)
            elif isinstance(parameterList, ParameterList):
                return 1 +  self.__formalParameterCounter__(parameterList.parameterList)
            else:
                return 1

    def __makeformalParameterList__(self,  parameterList):
        # This function extract the data type of function formal
        # parameters from left to right and stores it in a list
        # into the function instance
        if parameterList is None:
            return []
        else:
            if isinstance(parameterList, VarList):
                if isinstance(parameterList.varDeclaration, VarDeclaration):
                   return [parameterList.varDeclaration.dataType.dtype] + self.__makeformalParameterList__(parameterList.varList)
            elif isinstance(parameterList, VarDeclaration):
                    return [parameterList.dataType.dtype]
            return []

    def __checkFunctionCallDataTypeFormalParameters__(self, functionCall):
        # This function check whether the data type of the parameters
        # in a function call agree with the ones in the declaration
        # TODO
        functionName = functionCall.functionName
        formalParameterTypeList = self.symbolTable.lookup(functionName).instance.formalParameterTypeList

        def checkTypes(t1, t2):
            if t1 == t2:
                pass
            elif t1 == 'float' and t2 == 'int':
                pass
            else:
                m = message="Error: The argument type at function call does not agree. Passing " + t2 + " but the type is defined as " + t1
                self.errorProcedure(m, obj=functionCall)
        
        def checkIt(parameterList):
            global indexCounter
            if parameterList is None:
                pass
            else:
                if isinstance(parameterList, VarList):
                    if isinstance(parameterList.varDeclaration, VarDeclaration):
                        t1 = formalParameterTypeList[0]
                        t2 = parameterList.varDeclaration.dataType.dtype
                        checkTypes(t1, t2)
                        formalParameterTypeList[1:]
                        checkIt(parameterList.varList)
                elif isinstance(parameterList, BinaryOp):
                    resultingType = self.__visitBinaryOp__(parameterList)
                    t1 = formalParameterTypeList[0]
                    t2 = (lambda x : 'int' if x == 0 else 'float' if x == 1 else 'char or string')(resultingType)
                    checkTypes(t1, t2)
                    formalParameterTypeList[1:]
                elif isinstance(parameterList, ParameterList):
                    checkIt(parameterList.expression)
                    checkIt(parameterList.parameterList)
                elif isinstance(parameterList, str):
                    resultingType = self.__visitBinaryOp__(parameterList)
                    t1 = formalParameterTypeList[0]
                    t2 = (lambda x : 'int' if x == 0 else 'float' if x == 1 else 'char or string')(resultingType)
                    checkTypes(t1, t2)
                    formalParameterTypeList[1:]
                else:
                    return 1
        if len(formalParameterTypeList) == 0:
            pass
        else:
            checkIt(functionCall.args)

            
        
