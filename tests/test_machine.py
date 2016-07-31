from gbasic.machine import Machine

def test_letnum():
    m = Machine()
    m.add_line("10 LET A = 1")
    m.add_line("20 LET B = 0.9")
    m.add_line("30 LET C = -1")
    m.run()

    assert m.vars["A"] == 1
    assert m.vars["B"] == 0.9
    assert m.vars["C"] == -1

def test_arithmetic():
    m = Machine()
    m.add_line("10 LET A = 1 + 2")
    m.add_line("20 LET B = 1 - 2")
    m.add_line("30 LET C = 2 * 2")
    m.add_line("40 LET D = 6 / 2")
    m.add_line("50 LET E = 1 / 2")
    m.add_line("60 LET F = 2 ^ 10")
    m.run()

    assert m.vars["A"] == 3
    assert m.vars["B"] == -1
    assert m.vars["C"] == 4
    assert m.vars["D"] == 3
    assert m.vars["E"] == 0.5
    assert m.vars["F"] == 1024

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

def test_goto():
    m = Machine()
    m.add_line("20 GOTO 40")
    m.add_line("30 LET A = 2")
    m.add_line("40 LET B = 3")
    m.run()

    assert m.vars.get("A") is None
    assert m.vars["B"] == 3

def test_print(capsys):
    m = Machine()
    m.add_line("10 LET A = 1")
    m.add_line('20 PRINT "THIS PROGRAM IS NUMBER", A')
    m.run()

    out, err = capsys.readouterr()
    assert out == "THIS PROGRAM IS NUMBER 1\n"

    # semicolon prevents newline
    m.add_line('20 PRINT "THIS PROGRAM IS NUMBER", A;')
    m.run()

    out, err = capsys.readouterr()
    assert out == "THIS PROGRAM IS NUMBER 1"

