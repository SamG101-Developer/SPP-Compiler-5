import functools
import re


class AstPrinter:
    """!
    The AstPrinter class is used to print code with indentation for brace-contained blocks. It maintains a fixed
    indentation size, and the current indentation level.
    """

    _indent_size: int
    _current_indent: int

    def __init__(self, indent_size: int = 4) -> None:
        self._indent_size = indent_size
        self._current_indent = 0

    def increase_indent(self) -> None:
        self._current_indent += self._indent_size

    def decrease_indent(self) -> None:
        self._current_indent -= self._indent_size

    def format_code(self, code: str) -> str:
        return re.sub(r"\n", "\n" + " " * self._current_indent, code)


def ast_printer_method(func):
    """!
    This function is used as a decorator to use the AstPrinter's utility methods when printing ASTs. Certain ASTs
    require indentation (for pretty-printing), and this decorator handles that.

    @param func The function to decorate (called "print" in the ASTs).
    @return The decorated function.
    """

    @functools.wraps(func)
    def wrapper(self=None, *args):
        from SPPCompiler.SemanticAnalysis import Asts

        # All brace-contained blocks are marked as needing indentation.
        indent = isinstance(self, (
            Asts.InnerScopeAst, Asts.ClassImplementationAst, Asts.FunctionImplementationAst, Asts.SupImplementationAst))
        printer = args[0]

        # Handle the indentation and formatting of the code.
        if indent:
            printer.increase_indent()
            line = func(self, *args)
            line = printer.format_code(line)
            line = "\n".join([x for x in line.split("\n") if x.strip()])
            printer.decrease_indent()
            if line.split("\n") and line.split("\n")[-1].strip() == "}":
                lines, last = line.rsplit("\n", 1)
                last = last.lstrip().replace("}", " " * printer._current_indent + "}")
                line = f"{lines}\n{last}"
        else:
            line = func(self, *args)
            line = printer.format_code(line)

        # Return the formatted code.
        return line

    # Return the decorated function.
    return wrapper


__all__ = [
    "AstPrinter",
    "ast_printer_method"]
