from argparse import Namespace
import os.path

from SPPCompiler.LexicalAnalysis.Lexer import Lexer
from SPPCompiler.SyntacticAnalysis.Parser import Parser
from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticError, SemanticErrors
from SPPCompiler.SyntacticAnalysis.Errors.ParserError import ParserError
from spp import handle_init, handle_build


def _build_temp_project(project_name, code):
    restore = os.getcwd()

    if not os.path.exists(f"../tmp/{project_name}"):
        os.mkdir(f"../tmp/{project_name}")
        os.chdir(f"../tmp/{project_name}")
        handle_init(Namespace())
        with open("src/main.spp", "a") as f:
            f.write(code)
        handle_build(Namespace(mode="release"))

    else:
        os.chdir(f"../tmp/{project_name}")
        handle_build(Namespace(mode="release"))

    os.chdir(restore)


def should_pass_compilation(test_func):
    def wrapper(self):
        code = test_func.__doc__
        _build_temp_project(test_func.__name__, code)
    return wrapper


def should_fail_compilation(expected_error):
    def inner(test_func):
        def wrapper(self):
            code = test_func.__doc__
            with self.assertRaises(expected_error):
                _build_temp_project(test_func.__name__, code)
        return wrapper
    return inner


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


__all__ = [
    "should_pass_compilation", "should_fail_compilation",
    "should_pass_parsing", "should_fail_parsing",
    "ParserError", "SemanticError", "SemanticErrors"]
