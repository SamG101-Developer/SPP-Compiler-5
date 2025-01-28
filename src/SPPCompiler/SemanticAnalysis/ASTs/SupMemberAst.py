from typing import Union

from SPPCompiler.SemanticAnalysis.ASTs.FunctionPrototypeAst import FunctionPrototypeAst
from SPPCompiler.SemanticAnalysis.ASTs.SupPrototypeExtensionAst import SupPrototypeExtensionAst
from SPPCompiler.SemanticAnalysis.ASTs.SupUseStatementAst import SupUseStatementAst

type SupMemberAst = Union[
    FunctionPrototypeAst,
    SupPrototypeExtensionAst,
    SupUseStatementAst,
]

__all__ = ["SupMemberAst"]
