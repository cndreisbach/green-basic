from gbasic.machine import Machine

def test_letnum():
    m = Machine()
    m.add_line("10 LET A = 1")
    m.run()

    assert m.vars["A"] == 1

def test_addition():
    m = Machine()
    m.add_line("10 LET A = 1 + 2")
    m.run()

    assert m.vars["A"] == 3

def test_using_vars_in_let():
    m = Machine()
    m.add_line("10 LET A = 1")
    m.add_line("20 LET B = A + 1")
    m.run()

    assert m.vars["B"] == 2

def test_end():
    m = Machine()
    m.add_line("10 LET A = 1")
    m.add_line("20 END")
    m.add_line("30 LET B = 2")
    m.run()

    assert m.vars["A"] == 1
    assert m.vars.get("B") is None
