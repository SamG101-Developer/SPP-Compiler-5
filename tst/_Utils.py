from SPPCompiler.Compiler.Compiler import Compiler
from SPPCompiler.Utils.Errors import ParserError, SemanticError


def should_pass(test_func):
    def wrapper(self):
        code = test_func.__doc__
        Compiler.standalone(code)
    return wrapper


def should_fail(test_func):
    def wrapper(self):
        code = test_func.__doc__
        with self.assertRaises(SemanticError):
            Compiler.standalone(code)
    return wrapper


__all__ = ["should_pass", "should_fail"]
