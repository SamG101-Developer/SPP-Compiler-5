import os.path
from argparse import Namespace
from unittest import TestCase

import json_fix

from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticError, SemanticErrors
from SPPCompiler.SyntacticAnalysis.ParserErrors import ParserErrors
from SPPCompiler.Utils.FunctionCache import FunctionCache
from spp_cli import handle_build, handle_init, handle_vcs


class CustomTestCase(TestCase):
    def setUp(self):
        FunctionCache.clear_all_caches()


def _build_temp_project_v3(code, add_main: bool = True):
    cwd = os.getcwd()
    fp = f"test_outputs"

    if add_main:
        code = "fun main(args: std::vector::Vec[std::string::Str]) -> std::void::Void { }\n" + code

    if not os.path.exists(os.path.join(cwd, fp)):
        os.makedirs(os.path.join(cwd, fp))
        os.chdir(fp)
        handle_init()
        handle_vcs()
        os.chdir(cwd)

    with open(os.path.join(cwd, fp, "src", "main.spp"), "w") as f:
        f.write(code)

    os.chdir(fp)
    handle_build(Namespace(mode="rel"), skip_vcs=True)
    os.chdir(cwd)


def should_pass_compilation(no_main: bool = False):
    def inner(test_func):
        def wrapper(self):
            code = test_func.__doc__
            _build_temp_project_v3(code, add_main=not no_main)
        return wrapper
    return inner


def should_fail_compilation(expected_error, no_main: bool = False):
    def inner(test_func):
        def wrapper(self):
            code = test_func.__doc__
            with self.assertRaises(expected_error):
                _build_temp_project_v3(code, add_main=not no_main)
        return wrapper
    return inner


__all__ = [
    "should_pass_compilation", "should_fail_compilation", "CustomTestCase",
    "ParserErrors", "SemanticError", "SemanticErrors"]
