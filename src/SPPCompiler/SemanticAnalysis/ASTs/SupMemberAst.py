from typing import Union

import SPPCompiler.SemanticAnalysis as Asts

type SupMemberAst = Union[
    Asts.FunctionPrototypeAst,
    Asts.SupPrototypeExtensionAst,
    Asts.SupUseStatementAst,
]

__all__ = ["SupMemberAst"]
