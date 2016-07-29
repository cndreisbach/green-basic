from enum import Enum

Op = Enum('Op', 'ADD SUB MUL DIV POW NEG GOTO LETNUM LETSTR PRINT PRN END')

def execute(vm, op):
    operations = {
        Op.ADD: add,
        Op.LETNUM: letnum,
        Op.END: endop,
    }
    operations[op](vm)

def eval_operand(vm, operand):
    # TODO refactor to prevent circular import
    from .scanner import Element

    if not isinstance(operand, tuple):
        return operand

    if operand[0] is Element.numvar:
        return vm.vars[operand[1]]

    return operand

def add(vm):
    a = eval_operand(vm, vm.stack.pop())
    b = eval_operand(vm, vm.stack.pop())
    c = a + b
    vm.stack.append(c)

def letnum(vm):
    num = vm.stack.pop()
    varname = vm.stack.pop()
    vm.vars[varname[1]] = num

def endop(vm):
    vm.halt = True

