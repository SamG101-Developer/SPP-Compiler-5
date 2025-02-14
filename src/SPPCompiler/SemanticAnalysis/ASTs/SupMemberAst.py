from typing import Union

import SPPCompiler.SemanticAnalysis as Asts

SupMemberAst = Union[
    Asts.FunctionPrototypeAst,
    Asts.SupPrototypeExtensionAst,
    Asts.SupUseStatementAst,
]

__all__ = ["SupMemberAst"]
