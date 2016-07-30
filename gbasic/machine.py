from collections import deque, namedtuple
from .scanner import scan_line, scan_lineno, scan_eof, Element
from .operation import Op, execute

Line = namedtuple("Line", ("lineno", "text", "compiled"))


class GBasicRuntimeError(Exception):
    def __init__(self, idx, message=None):
        self.idx = idx
        self.message = message
        super().__init__(idx, message)


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

    def resolve(self, element):
        """
        Resolve an element. If it is a literal, just return that literal.
        If it is a variable, resolve it for the current value.
        Otherwise, return the element.
        """

        if not isinstance(element, tuple):
            return element

        if element[0] is Element.numvar:
            return self.vars[element[1]]

        return element

    def pop_and_resolve(self):
        """
        Pop the top element off the stack. If it is a variable, resolve it for
        the current value.
        """
        element = self.stack.pop()
        return self.resolve(element)

    def goto(self, lineno):
        """
        Goto the line number.
        """
        if not lineno in self.linenos:
            raise GBasicRuntimeError(
                ("Cannot GOTO line number {}: "
                 "line number does not exist").format(lineno))

        # Obviously, this is not the best way.
        for idx, line in enumerate(self.program):
            if line.lineno == lineno:
                self.pidx = idx
                break

    def run(self):
        self.pidx = 0
        self.halt = False

        ## TODO add preflight (data)

        while self.pidx < len(self.program) and not self.halt:
            cur_pidx = self.pidx

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
            
            # We check this to make sure our current line number didn't change,
            # as it would on a GOTO.
            if cur_pidx == self.pidx:
                self.pidx += 1
                
        print(self.vars)
        print(self.stack)







