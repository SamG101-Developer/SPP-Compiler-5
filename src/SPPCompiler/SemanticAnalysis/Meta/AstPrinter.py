import functools


class AstPrinter:
    _indent_size: int
    _current_indent: int

    def __init__(self, indent_size: int = 4) -> None:
        self._indent_size = indent_size // 2
        self._current_indent = 0

    def increase_indent(self) -> None:
        self._current_indent += self._indent_size

    def decrease_indent(self) -> None:
        self._current_indent -= self._indent_size

    def format_code(self, code: str) -> str:
        return code.replace("\n", "\n" + " " * self._indent_size, code.count("\n") - 2)


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
            if len(line.split("\n")) > 1 and line.split("\n")[-2].strip() == "}":
                lines, last, _ = line.rsplit("\n", 2)
                last = last.replace(" " * printer._indent_size * 2, "", 1)
                line = f"{lines}\n{last}\n{_}"
            printer.decrease_indent()

        else:
            line = func(self, *args)
            line = printer.format_code(line)

        return line
    return wrapper


__all__ = [
    "AstPrinter",
    "ast_printer_method"]
