from __future__ import annotations

import ctypes
import os.path

from llvmlite import binding as llvm
from llvmlite import ir

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors


def register_external_functions(
        function_prototype: Asts.FunctionPrototypeAst, dll_path: str, sm: ScopeManager) -> None:
    """
    Register an external function with LLVM.
    """

    # Create a target machine and LLVM module.
    module = ir.Module(name="test_ffi")
    target = llvm.Target.from_default_triple()
    target_machine = target.create_target_machine()

    # Get the function symbol fom the DLL and register it with LLVM.
    try:
        dll = ctypes.CDLL(dll_path)
        name = function_prototype.name.value
        check = ctypes.cast(dll[name], ctypes.c_void_p).value

    except AttributeError:
        dll_name = os.path.basename(dll_path)
        raise SemanticErrors.InvalidFfiFunctionError().add(function_prototype.name, dll_name).scopes(sm.current_scope)
