from __future__ import annotations

from typing import Union

from SPPCompiler.SemanticAnalysis import Asts

ModuleMemberAst = Union[
    Asts.ClassPrototypeAst,
    Asts.FunctionPrototypeAst,
    Asts.GlobalConstantAst,
    Asts.SupPrototypeFunctionsAst,
    Asts.SupPrototypeExtensionAst,
    Asts.UseStatementAst]

__all__ = [
    "ModuleMemberAst"]
