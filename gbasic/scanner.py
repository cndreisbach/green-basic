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


def scan_keyword(text, cur_idx):
    """Scan for a keyword."""
    
    _, idx = scan_ws(text, cur_idx)
    
    try:
        keyword = next(kw for kw in KEYWORDS if text.startswith(kw, idx))
        idx += len(keyword)
        return keyword, idx
    except StopIteration:
        raise GBasicSyntaxError(idx, "Keyword expected")









