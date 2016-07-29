import re
from functools import wraps

from enum import Enum

from .operation import Op

Element = Enum('Element', 'lineno numlit strlit strvar numvar op')
MathOps = {"+": Op.ADD,
           "-": Op.SUB,
           "*": Op.MUL,
           "/": Op.DIV,
           "^": Op.POW}

keywords = {
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
}


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


def allow_ws(scanfn):
    @wraps(scanfn)
    def wrapper(text, idx):
        _, idx = scan_ws(text, idx)
        return scanfn(text, idx)

    return wrapper


def scan_ws(text, cur_idx):
    """Scans for whitespace. Whitespace is never necessary, so if we do not
    find it, return the current index instead of erroring."""

    # Return immediately if all we have is whitespace.
    if text[cur_idx:].lstrip() == '':
        return text[cur_idx:], len(text)

    try:
        idx = next(i for i in range(cur_idx, len(text))
                   if not text[i:i + 1].isspace())
        return text[cur_idx:idx], idx
    except StopIteration:
        return "", cur_idx


def check_lineno(text, idx):
    """Checks for line numbers. Line numbers must be positive integers."""
    match = re.match(r"\d+", text[idx:])
    if match:
        return match.group(0)


@allow_ws
def scan_lineno(text, idx):
    """Scans for line numbers. Line numbers must be positive integers."""
    lineno = check_lineno(text, idx)

    if lineno:
        return int(lineno), idx + len(lineno)
    else:
        raise GBasicSyntaxError(idx, "Line number expected")


@allow_ws
def scan_keyword(text, idx):
    """Scan for a keyword."""
    try:
        keyword = next(kw for kw in keywords if text.startswith(kw, idx))
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


@allow_ws
def scan_variable(text, idx):
    """Scan for a variable name."""
    var = check_variable(text, idx)
    if var:
        if var[-1] == "$":
            var = (Element.strvar, var)
        else:
            var = (Element.numvar, var)
        return var, idx + len(var[1])
    else:
        raise GBasicSyntaxError(idx, "Variable name expected")


def check_number(text, idx):
    """Check for a number. We are allowing more than the BASIC standard here.
    In BASIC, we'd only allow up to 11 digits and scientific numbers from -308 to 308."""

    match = re.match(
        r"(?i)([+\-]?(?:[1-9]\d*|0))(?:\.([0-9]*))?(?:E([+-]?\d+))?",
        text[idx:])
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


@allow_ws
def scan_number(text, idx):
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
        out_ws = check(text, idx) or ""
        if ws_ok:
            out = out_ws.lstrip()
        else:
            out = out_ws
        if out == chars:
            return chars, idx + len(out_ws)
        else:
            raise GBasicSyntaxError(idx,
                                    "Characters '{}' expected".format(chars))

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

@allow_ws
def scan_primary(text, cur_idx):
    _, idx = scan_ws(text, cur_idx)

    if check_number(text, idx):
        num, idx = scan_number(text, idx)
        return [num], idx
    elif check_variable(text, idx):
        var, idx = scan_variable(text, idx)
        return [var], idx
    elif check_chars("(")(text, idx):
        _, idx = scan_chars("(")(text, idx)
        primary, idx = scan_expression(text, idx)
        _, idx = scan_chars(")")(text, idx)
        return primary, idx

    raise GBasicSyntaxError(cur_idx, "Number, variable, or expression expected")


@allow_ws
def scan_factor(text, cur_idx):
    check_exp = check_chars("^")
    scan_exp = scan_chars("^")

    out = []
    idx = cur_idx

    primary, idx = scan_primary(text, idx)
    out.extend(primary)

    while check_exp(text, idx):
        _, idx = scan_exp(text, idx)
        primary, idx = scan_primary(text, idx)
        out.extend(primary)
        out.append((Element.op, Op.POW))

    return out, idx


@allow_ws
def scan_term(text, cur_idx):
    check_mul = check_chars("*")
    scan_mul = scan_chars("*")
    check_div = check_chars("/")
    scan_div = scan_chars("/")

    out = []
    idx = cur_idx

    factor, idx = scan_factor(text, idx)
    out.extend(factor)

    # TODO: fix all this crap
    while check_mul(text, idx) or check_div(text, idx):
        try:
            op, idx = scan_mul(text, idx)
        except TypeError:
            op, idx = scan_div(text, idx)

        factor, idx = scan_factor(text, idx)

        out.extend(factor)
        out.append((Element.op, MathOps[op]))

    return out, idx


@allow_ws
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
    out.extend(term)
    if op and op == "-":
        out.append((Element.op, Op.NEG))

    # TODO: fix all this crap
    while check_add(text, idx) or check_sub(text, idx):
        try:
            op, idx = scan_add(text, idx)
        except TypeError:
            op, idx = scan_sub(text, idx)

        term, idx = scan_term(text, idx)

        out.extend(term)
        out.append((Element.op, MathOps[op]))

    return out, idx


# Scanning whole lines

@allow_ws
def scan_eof(text, idx):
    """At the end of a line, we need to know that it is done. This scans to
    make sure we're at the end of the line."""

    if text[idx:] == '':
        return True, idx
    else:
        raise GBasicSyntaxError(idx, "End of line expected")


@allow_ws
def scan_let(text, idx):
    """This scans a line to make sure it is a valid LET. It is assumed that
    we have already scanned the keyword LET and so idx will be placed after
    that."""

    var, idx = scan_variable(text, idx)
    _, idx = scan_chars("=")(text, idx)

    out = [var]

    if var[0] == Element.numvar:
        expression, idx = scan_expression(text, idx)
        scan_eof(text, idx)
        out.extend(expression)
        out.append((Element.op, Op.LETNUM))
    else:
        outstr, idx = scan_string(text, idx)
        scan_eof(text, idx)
        out.extend([outstr, (Element.op, Op.LETSTR)])
    return out, idx


@allow_ws
def scan_print(text, idx):
    """Scan to make sure line is a valid PRINT. It is assumed we have already
    scanned the keyword PRINT.

    PRINT will take the number on the stack beneath it to know how many items
    to print.
    """

    check_comma = check_chars(",")
    scan_comma = scan_chars(",")

    out = []
    items = 0
    item = None

    def scan_next(text, idx):
        nonlocal items

        # Try a string first, then an expression
        try:
            item, idx = scan_string(text, idx)
            item = [item]
        except GBasicSyntaxError:
            item, idx = scan_expression(text, idx)

        items += 1
        return item, idx

    item, idx = scan_next(text, idx)
    out.extend(item)

    while check_comma(text, idx):
        _, idx = scan_comma(text, idx)
        item, idx = scan_next(text, idx)
        out.extend(item)

    if check_chars(";")(text, idx):
        _, idx = scan_chars(";")(text, idx)
        op = Op.PRN
    else:
        op = Op.PRINT

    scan_eof(text, idx)

    out.append(items)
    out.append((Element.op, op))
    return out, idx


@allow_ws
def scan_goto(text, idx):
    """Scan to make sure line is a valid GOTO. It is assumed we have already
    scanned the keyword GOTO.
    """
    lineno, idx = scan_lineno(text, idx)
    scan_eof(text, idx)
    return [lineno, (Element.op, Op.GOTO)], idx


@allow_ws
def scan_end(text, idx):
    scan_eof(text, idx)
    return [(Element.op, Op.END)], idx


@allow_ws
def scan_line(text, idx):
    keyword, idx = scan_keyword(text, idx)

    keyword_map = {
        "LET": scan_let,
        "PRINT": scan_print,
        "GOTO": scan_goto,
        "END": scan_end,
    }

    if keyword in keyword_map:
        return keyword_map[keyword](text, idx)
    else:
        raise GBasicSyntaxError(idx, "{} not yet implemented".format(keyword))
