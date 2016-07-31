from enum import Enum

Op = Enum('Op', 'ADD SUB MUL DIV POW NEG GOTO LETNUM LETSTR PRINT PRN END')


def execute(vm, op):
    operations = {
        Op.ADD: add,
        Op.SUB: sub,
        Op.MUL: mul,
        Op.DIV: div,
        Op.POW: pow,
        Op.NEG: neg,
        Op.LETNUM: letnum,
        Op.END: endop,
        Op.GOTO: goto,
        Op.PRN: prn,
        Op.PRINT: printop,
    }
    operations[op](vm)


def add(vm):
    a = vm.pop_and_resolve()
    b = vm.pop_and_resolve()
    vm.stack.append(b + a)


def sub(vm):
    a = vm.pop_and_resolve()
    b = vm.pop_and_resolve()
    vm.stack.append(b - a)


def mul(vm):
    a = vm.pop_and_resolve()
    b = vm.pop_and_resolve()
    vm.stack.append(b * a)


def div(vm):
    a = vm.pop_and_resolve()
    b = vm.pop_and_resolve()
    vm.stack.append(b / a)


def pow(vm):
    a = vm.pop_and_resolve()
    b = vm.pop_and_resolve()
    vm.stack.append(b ** a)


def neg(vm):
    a = vm.pop_and_resolve()
    vm.stack.append(-a)


def letnum(vm):
    num = vm.pop_and_resolve()
    varname = vm.stack.pop()
    vm.vars[varname[1]] = num


def endop(vm):
    vm.halt = True


def goto(vm):
    lineno = vm.stack.pop()
    vm.goto(lineno)


def prn(vm):
    item_count = vm.stack.pop()
    items = [vm.pop_and_resolve() for _ in range(item_count)]
    print(*items, sep=' ', end='')


def printop(vm):
    prn(vm)
    print()
