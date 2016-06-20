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
