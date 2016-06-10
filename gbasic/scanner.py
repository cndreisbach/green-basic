import re
from enum import Enum

Token = Enum('Token', 'number string operator keyword variable')
Keyword = Enum('Keyword', " ".join((
    'LET',
    'READ',
    'DATA',
    'RESTORE',
    'PRINT',
    'GOTO',
    'IF',
    'ON',
    'FOR',
    'DIM',
    'END',
    'RANDOM',
    'GOSUB',
    'RETURN',
    'DEF',
    'INPUT',
    'REM',
    'STOP',
)))


# A scan function should:
# - take text and cur_idx
# - and move cur_idx past any whitespace, if any is allowed
# - and return what it was looking for and the new cur_idx

# A check function should:
# - take text and cur_idx
# - and return the matched text or None
# and should not:
# - move past whitespace

class GBasicSyntaxError(Exception):
    def __init__(self, idx, message=None):
        self.idx = idx
        self.message = message
        super().__init__(idx, message)
        

def scan_ws(text, cur_idx):
    """Scans for whitespace. Whitespace is never necessary, so if we do not
    find it, return the current index instead of erroring."""
    
    try:
        idx = next(i for i in range(cur_idx, len(text))
                   if not text[i:i+1].isspace())
        return text[cur_idx:idx], idx
    except StopIteration:
        return "", cur_idx


def check_lineno(text, idx):
    """Checks for line numbers. Line numbers must be positive integers."""
    match = re.match(r"\d+", text[idx:])
    if match:
        return match.group(0)

def scan_lineno(text, cur_idx):
    """Scans for line numbers. Line numbers must be positive integers."""

    _, idx = scan_ws(text, cur_idx)
    lineno = check_lineno(text, idx)

    if lineno:
        return int(lineno), idx + len(lineno)
    else:
        raise GBasicSyntaxError(idx, "Line number expected")


def scan_keyword(text, cur_idx):
    """Scan for a keyword."""
    
    _, idx = scan_ws(text, cur_idx)
    
    try:
        keyword = next(kw.name for kw in Keyword if text.startswith(kw.name, idx))
        idx += len(keyword)
        return keyword, idx
    except StopIteration:
        raise GBasicSyntaxError(idx, "Keyword expected")


def check_variable(text, idx):
    """Check for a variable name.
    Variable names must start with a character then can optionally have
    one more character or number. String variables end with $."""
    match = re.match(r"[A-Z][A-Z0-9]?\$?", text[idx:])
    if match:
        return match.group(0)

def scan_variable(text, cur_idx):
    """Scan for a variable name."""
    _, idx = scan_ws(text, cur_idx)
    var = check_variable(text, idx)
    if var:
        return var, idx + len(var)
    else:
        raise GBasicSyntaxError(idx, "Variable name expected")


def check_number(text, idx):
    """Check for a number. We are allowing more than the BASIC standard here.
    In BASIC, we'd only allow up to 11 digits and scientific numbers from -308 to 308."""

    match = re.match(r"(?i)([+\-]?(?:[1-9]\d*|0))(?:\.([0-9]*))?(?:E([+-]?\d+))?", text[idx:])
    if match:
        whole = match.group(1)
        decimal = match.group(2)
        scientific = match.group(3)

        if scientific:
            num = "{}.{}e{}".format(whole, decimal or 0, scientific)
        elif decimal:
            num = "{}.{}".format(whole, decimal)
        else:
            num = whole

        return num

def scan_number(text, cur_idx):
    _, idx = scan_ws(text, cur_idx)
    numstr = check_number(text, idx)
    if numstr is not None:
        if "." in numstr or 'e' in numstr:
            num = float(numstr)
        else:
            num = int(numstr)

        return num, idx + len(numstr)
    else:
        raise GBasicSyntaxError(idx, "Number expected")


def check_string(text, idx):
    """Checks for a quoted string. All strings are quoted with double quotes."""
    str_regex = re.compile(r"\"(?:[^\"\\]|\\.)*\"")
    match = str_regex.match(text[idx:])
    if match:
        return match.group(0)

def unquote_string(quoted_str):
    return quoted_str[1:-1].replace('\\"', '"').replace('\\\\', '\\')

def scan_string(text, cur_idx):
    _, idx = scan_ws(text, cur_idx)
    quoted_str = check_string(text, idx)
    if quoted_str is not None:
        string = unquote_string(quoted_str)
        return string, idx + len(quoted_str)
    else:
        raise GBasicSyntaxError(idx, "String expected")


def check_chars(chars, ws_ok=True):
    """Check for any particular characters."""
    def check(text, idx):
        if ws_ok:
            ws, idx = scan_ws(text, idx)
        else:
            ws = ""
        if text[idx:].startswith(chars):
            return ws + chars

    return check

def scan_chars(chars, ws_ok=True):
    check = check_chars(chars, ws_ok)

    def scan(text, idx):
        out_ws = check(text, idx)
        if ws_ok:
            out = out_ws.lstrip()
        else:
            out = out_ws
        if out == chars:
            return chars, idx + len(out_ws)

    return scan


# How to best represent each type of token?
# I could use classes or named tuples, like so:
#
# Add(3, Mult(2, 3))
#
# or I could use reverse Polish and only strings and numbers, like so:
#
# 2 3 MULT 3 ADD
#
# Since I do have strings in my language, I may have to at least have
# an indicator for the operators. Example:
#
# LET A$ = "HELLO"
#
# A$ HELLO LETSTR won't work, as A$ is a variable and LETSTR is an
# internal command.
#
# Commands could be enums.
# Variables and user-defined functions could be namedtuples or
# objects.
#
# Another option, more low-level, is to have each token represented
# internally by a tuple with an opcode to say what it is (variable,
# operator, keyword, number, etc) and the second element being it.

# To scan an expression, we use the following recursive descent grammar
#
# expression = (+|-)? term ((+|-) term)*
# term = factor (("/"|"*") factor)*
# factor = primary (^ primary)*
# primary = variable | constant | "(" expression ")"

def sqz(a_list):
    """Squeeze a list that has only one element, removing the outer list."""
    while type(a_list) is list and len(a_list) == 1:
        a_list = a_list[0]
    return a_list

def scan_primary(text, cur_idx):
    _, idx = scan_ws(text, cur_idx)

    if check_number(text, idx):
        return scan_number(text, idx)
    elif check_variable(text, idx):
        return scan_variable(text, idx)
    elif check_chars("(")(text, idx):
        _, idx = scan_chars("(")(text, idx)
        primary, idx = scan_expression(text, idx)
        _, idx = scan_chars(")")(text, idx)
        return primary, idx

    raise GBasicSyntaxError(cur_idx, "Number, variable, or expression expected")

def scan_factor(text, cur_idx):
    check_exp = check_chars("^")
    scan_exp = scan_chars("^")

    out = []
    idx = cur_idx

    primary, idx = scan_primary(text, idx)
    out.append(primary)

    while check_exp(text, idx):
        _, idx = scan_exp(text, idx)
        primary, idx = scan_primary(text, idx)
        out.append(primary)
        out.append((Token.operator, "^"))

    return sqz(out), idx

def scan_term(text, cur_idx):
    check_mul = check_chars("*")
    scan_mul = scan_chars("*")
    check_div = check_chars("/")
    scan_div = scan_chars("/")

    out = []
    idx = cur_idx

    factor, idx = scan_factor(text, idx)
    out.append(factor)

    # TODO: fix all this crap
    while check_mul(text, idx) or check_div(text, idx):
        try:
            op, idx = scan_mul(text, idx)
        except TypeError:
            op, idx = scan_div(text, idx)

        factor, idx = scan_factor(text, idx)

        out.append(factor)
        out.append((Token.operator, op))

    return sqz(out), idx

def scan_expression(text, cur_idx):
    check_add = check_chars("+")
    scan_add = scan_chars("+")
    check_sub = check_chars("-")
    scan_sub = scan_chars("-")

    out = []
    idx = cur_idx

    # Unary +/-
    if check_add(text, idx):
        op, idx = scan_add(text, idx)
    elif check_sub(text, idx):
        op, idx = scan_sub(text, idx)
    else:
        op = None

    term, idx = scan_term(text, idx)
    out.append(term)
    if op:
        out.append((Token.operator, op))

    # TODO: fix all this crap
    while check_add(text, idx) or check_sub(text, idx):
        try:
            op, idx = scan_add(text, idx)
        except TypeError:
            op, idx = scan_sub(text, idx)

        term, idx = scan_term(text, idx)

        out.append(term)
        out.append((Token.operator, op))

    return sqz(out), idx
