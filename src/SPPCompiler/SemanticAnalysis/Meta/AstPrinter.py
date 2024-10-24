import functools
import re


class AstPrinter:
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
        # return code.replace("\n", "\n" + " " * self._indent_size, code.count("\n") - 1)


# Decorators for the printer methods
def ast_printer_method(func):
    @functools.wraps(func)
    def wrapper(self=None, *args):
        from SPPCompiler.SemanticAnalysis import InnerScopeAst
        indent = isinstance(self, InnerScopeAst)
        printer = args[0]

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

        return line
    return wrapper


__all__ = [
    "AstPrinter",
    "ast_printer_method"]
