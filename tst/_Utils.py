from SPPCompiler.Compiler.Compiler import Compiler
from SPPCompiler.LexicalAnalysis.Lexer import Lexer
from SPPCompiler.SyntacticAnalysis.Parser import Parser
from SPPCompiler.Utils.Errors import ParserError, SemanticError


def should_pass_compilation(test_func):
    def wrapper(self):
        code = test_func.__doc__
        Compiler.standalone(code)
    return wrapper


def should_fail_compilation(test_func):
    def wrapper(self):
        code = test_func.__doc__
        with self.assertRaises(SemanticError):
            Compiler.standalone(code)
    return wrapper


def should_pass_parsing(parser_func):
    def parser_func_chooser(test_func):
        def wrapper(self):
            code = test_func.__doc__
            parser_func(Parser(Lexer(code).lex()))
        return wrapper
    return parser_func_chooser


def should_fail_parsing(parser_func):
    def parser_func_chooser(test_func):
        def wrapper(self):
            code = test_func.__doc__
            with self.assertRaises(ParserError):
                parser_func(Parser(Lexer(code).lex()))
        return wrapper
    return parser_func_chooser


__all__ = ["should_pass_compilation", "should_fail_compilation", "should_pass_parsing", "should_fail_parsing"]
