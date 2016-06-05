import pytest
from gbasic.scanner import scan_ws, scan_keyword, GBasicSyntaxError


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
    
