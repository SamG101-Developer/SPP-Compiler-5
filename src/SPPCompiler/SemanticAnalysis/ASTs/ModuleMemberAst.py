from typing import Union

import SPPCompiler.SemanticAnalysis.ASTs as Asts

type ModuleMemberAst = Union[
    Asts.ClassPrototypeAst,
    Asts.FunctionPrototypeAst,
    Asts.GlobalConstantAst,
    Asts.SupPrototypeFunctionsAst,
    Asts.SupPrototypeExtensionAst,
    Asts.UseStatementAst]

__all__ = ["ModuleMemberAst"]
