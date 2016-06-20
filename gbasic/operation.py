from enum import Enum

Op = Enum('Op', 'ADD SUB MUL DIV POW NEG LETNUM LETSTR PRINT PRN END')

def execute(vm, op):
    operations = {
        Op.ADD: add,
        Op.LETNUM: letnum
    }
    operations[op](vm)

def add(vm):
    a = vm.stack.pop()
    b = vm.stack.pop()
    c = a + b
    vm.stack.append(c)

def letnum(vm):
    num = vm.stack.pop()
    varname = vm.stack.pop()
    vm.vars[varname[1]] = num


