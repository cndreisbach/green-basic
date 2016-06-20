from collections import deque, namedtuple
from .scanner import scan_line, scan_lineno, scan_eof, Element
from .operation import Op, execute

Line = namedtuple("Line", ("lineno", "text", "compiled"))

class Machine:
    """The virtual machine that stores and executes BASIC code."""

    def __init__(self):
        self.stack = deque()

        # The program is a list of Lines.
        self.program = []
        self.linenos = set()
        
        # Vars are in a dictionary. No current idea on scope for functions.
        self.vars = {}

        self.pidx = 0
        self.halt = False

    def _process_line(self, text):
        lineno, idx = scan_lineno(text, 0)
        compiled, _ = scan_line(text, idx)

        line = Line(lineno, text[idx:].strip(), compiled)
        return line

    def add_line(self, text):
        line = self._process_line(text) 
        if line.lineno in self.linenos:
            self.delete_line(line.lineno)
        self.linenos.add(line.lineno)
        self.program.append(line)            
        self.program.sort(key=lambda line: line.lineno)

    def delete_line(self, lineno):
        self.linenos.remove(lineno)
        self.program = [l for l in self.program if l.lineno != lineno]

    def run(self):
        self.pidx = 0
        self.halt = False

        ## TODO add preflight (data)

        while self.pidx < len(self.program) and not self.halt:
            line = self.program[self.pidx]
            for element in line.compiled:
                if not isinstance(element, tuple):
                    self.stack.append(element)
                    print(self.stack)
                elif element[0] is Element.op:
                    # run the operation
                    execute(self, element[1])
                    print(element[1])
                    print(self.stack)
                else:
                    self.stack.append(element)
                    print(self.stack)

            self.pidx += 1
                
        print(self.vars)
        print(self.stack)







