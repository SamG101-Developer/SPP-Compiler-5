from argparse import Namespace
import os.path

from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticError, SemanticErrors
from SPPCompiler.SyntacticAnalysis.Errors.ParserError import ParserError
from spp import handle_init, handle_build


def _build_temp_project_2(project_dir_name, project_name, code):
    restore = os.getcwd()
    fp = f"C:/Users/samue/PycharmProjects/SPP-Compiler-5/tmp/{project_dir_name}/{project_name}"

    try:
        if not os.path.exists(fp):
            os.makedirs(os.path.abspath(fp))
            os.chdir(fp)
            handle_init(Namespace())
            with open("src/main.spp", "a") as f:
                f.write(code)
            handle_build(Namespace(mode="release"))

        else:
            os.chdir(fp)
            handle_build(Namespace(mode="release"))

    finally:
        os.chdir(restore)


def should_pass_compilation():
    def inner(test_func):
        def wrapper(self):
            code = test_func.__doc__
            enclosing_dir = test_func.__code__.co_filename.split(os.path.sep)[-1].split(".")[0]
            _build_temp_project_2(enclosing_dir, test_func.__name__, code)
        return wrapper
    return inner


def should_fail_compilation(expected_error):
    def inner(test_func):
        def wrapper(self):
            code = test_func.__doc__
            with self.assertRaises(expected_error):
                enclosing_dir = test_func.__code__.co_filename.split(os.path.sep)[-1].split(".")[0]
                _build_temp_project_2(enclosing_dir, test_func.__name__, code)
        return wrapper
    return inner


__all__ = [
    "should_pass_compilation", "should_fail_compilation",
    "ParserError", "SemanticError", "SemanticErrors"]
