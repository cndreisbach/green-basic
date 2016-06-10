import pytest
import string
import random
from gbasic.scanner import *
from hypothesis import given, settings, Verbosity
from hypothesis import strategies as st

def test_scan_ws_finds_next_non_ws_from_start():
    text = "   PRINT"
    _, idx = scan_ws(text, 0)
    assert idx == 3

def test_scan_ws_finds_next_non_ws_from_mid():
    text = "10 PRINT"
    _, idx = scan_ws(text, 2)
    assert idx == 3

def test_scan_ws_returns_cur_idx_if_no_ws():
    text = "10 PRINT"
    _, idx = scan_ws(text, 0)
    assert idx == 0

def test_scan_ws_returns_cur_idx_if_at_end_of_line():
    text = "10 PRINT"
    _, idx = scan_ws(text, 8)
    assert idx == 8

def test_check_lineno():
    text = "10 END"
    lineno = check_lineno(text, 0)
    assert lineno == "10"

    lineno = check_lineno(text, 2)
    assert lineno is None

def test_scan_lineno():
    text = "10 END"
    lineno, idx = scan_lineno(text, 0)
    assert lineno == 10
    assert idx == 2

def test_scan_lineno_syntax_error():
    text = "10 PRINT"
    with pytest.raises(GBasicSyntaxError) as exinfo:
        lineno, idx = scan_lineno(text, 2)
    assert exinfo.value.idx == 3
    assert exinfo.value.message == "Line number expected"


def test_scan_keyword_finds_keyword():
    text = "LET A = 1"
    kw, idx = scan_keyword(text, 0)
    assert kw == "LET"
    assert idx == 3

def test_scan_keyword_finds_keyword_past_ws():
    text = "  LET A = 1"
    kw, idx = scan_keyword(text, 0)
    assert kw == "LET"
    assert idx == 5

def test_scan_keyword_errors_if_no_keyword():
    text = "A = 1"
    with pytest.raises(GBasicSyntaxError) as exinfo:
        kw, idx = scan_keyword(text, 0)
    assert exinfo.value.idx == 0
    assert exinfo.value.message == "Keyword expected"

def gen_varname(x, y, strvar):
    var = x
    if random.randint(0, 1):
        var += str(y)
    if strvar:
        var += "$"
    return var

def test_check_variable():
    text = "10 LET X1 = 1"
    assert check_variable(text, 0) is None
    assert check_variable(text, 7) == "X1"

@given(st.builds(gen_varname,
                 st.sampled_from(string.ascii_uppercase),
                 st.sampled_from(string.ascii_uppercase + string.digits),
                 st.booleans()))
def test_check_variable_generated(var):
    assert check_variable(var, 0) == var

@given(st.builds(gen_varname,
                 st.sampled_from(string.ascii_uppercase),
                 st.sampled_from(string.ascii_uppercase + string.digits),
                 st.booleans()))
def test_scan_variable_generated(var):
    tok, idx =  scan_variable(var, 0)

    assert tok[1] == var
    if var[-1] == "$":
        assert tok[0] == Token.strvar
    else:
        assert tok[0] == Token.numvar

@given(start=st.text(), num=st.integers())
def test_check_number_integers_generated(start, num):
    text = start + str(num)
    assert int(check_number(text, len(start))) == num

@given(num=st.floats(allow_infinity=False, allow_nan=False),
       start=st.text())
def test_check_number_floats_generated(start, num):
    text = start + str(num)
    cnum = float(check_number(text, len(start)))
    
    if abs(num) < 1:
        assert (cnum - num) < 0.00001
    else:
        assert cnum == num

valid_str_chars = string.ascii_uppercase + string.ascii_lowercase + \
                  string.digits + string.punctuation

def quote_text(text):
    return '"{}"'.format(text.replace('\\', '\\\\').replace('"', '\\"'))

@given(st.text(alphabet=valid_str_chars))
def test_check_string_generated(text):
    quoted = quote_text(text)
    assert check_string(quoted, 0) == quoted

@given(st.text(alphabet=valid_str_chars))
def test_scan_string_generated(text):
    quoted = quote_text(text)
    out, _ = scan_string(quoted, 0)
    assert out == text

def test_check_chars():
    check_comma = check_chars(",")
    text = "20 PRINT A$, B$"
    assert check_comma(text, 11) == ","

    check_to = check_chars("TO")
    text = "30 FOR A = 1 TO 10"
    assert check_to(text, 13) == "TO"

def test_scan_primary():
    text = "3.5"
    out, _ = scan_primary(text, 0)
    assert out == 3.5

    text = "A1"
    out, _ = scan_primary(text, 0)
    assert out == (Token.numvar, "A1")

    text = "(1 + 2)"
    out, _ = scan_primary(text, 0)
    assert out == [1, 2, (Token.operator, "+")]

def test_scan_expression():
    text = "3.5"
    out, _ = scan_expression(text, 0)
    assert out == 3.5

    text = "A1"
    out, _ = scan_expression(text, 0)
    assert out == (Token.numvar, "A1")

    text = "1 + 2"
    out, _ = scan_expression(text, 0)
    assert out == [1, 2, (Token.operator, "+")]

    text = "A1 ^ 2 + 2 * (A2 + 1)"
    out, _ = scan_expression(text, 0)
    assert out == [[(Token.numvar, "A1"), 2, (Token.operator, "^")],
                   [2, [(Token.numvar, "A2"), 1, (Token.operator, "+")], (Token.operator, "*")],
                   (Token.operator, "+")]
