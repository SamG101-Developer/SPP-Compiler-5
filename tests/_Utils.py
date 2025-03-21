import os.path
from argparse import Namespace
from unittest import TestCase

from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticError, SemanticErrors
from SPPCompiler.SyntacticAnalysis.ParserErrors import ParserErrors
from spp_cli import handle_build


class CustomTestCase(TestCase):
    ...


def _build_temp_project_v3(code):
    cwd = os.getcwd()
    fp = f"test_outputs"
    with open(f"{cwd}/{fp}/src/main.spp", "w") as f:
        f.write(code)
    os.chdir(fp)
    handle_build(Namespace(mode="rel"), skip_vcs=True)
    os.chdir(cwd)


def should_pass_compilation():
    def inner(test_func):
        def wrapper(self):
            code = test_func.__doc__
            _build_temp_project_v3(code)
        return wrapper
    return inner


def should_fail_compilation(expected_error):
    def inner(test_func):
        def wrapper(self):
            code = test_func.__doc__
            with self.assertRaises(expected_error):
                _build_temp_project_v3(code)
        return wrapper
    return inner


__all__ = [
    "should_pass_compilation", "should_fail_compilation", "CustomTestCase",
    "ParserErrors", "SemanticError", "SemanticErrors"]
