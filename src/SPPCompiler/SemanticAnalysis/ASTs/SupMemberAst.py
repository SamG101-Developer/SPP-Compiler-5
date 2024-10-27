from typing import Union

from SPPCompiler.SemanticAnalysis.ASTs.FunctionPrototypeAst import FunctionPrototypeAst
from SPPCompiler.SemanticAnalysis.ASTs.SupPrototypeInheritanceAst import SupPrototypeInheritanceAst
from SPPCompiler.SemanticAnalysis.ASTs.SupUseStatementAst import SupUseStatementAst

type SupMemberAst = Union[
    FunctionPrototypeAst,
    SupPrototypeInheritanceAst,
    SupUseStatementAst,
]

__all__ = ["SupMemberAst"]
