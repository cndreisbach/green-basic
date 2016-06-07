import re

KEYWORDS = (
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
)

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
        keyword = next(kw for kw in KEYWORDS if text.startswith(kw, idx))
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
