from typing import Union

from SPPCompiler.SemanticAnalysis.ClassPrototypeAst import ClassPrototypeAst
from SPPCompiler.SemanticAnalysis.GlobalConstantAst import GlobalConstantAst
from SPPCompiler.SemanticAnalysis.FunctionPrototypeAst import FunctionPrototypeAst
from SPPCompiler.SemanticAnalysis.SupPrototypeInheritanceAst import SupPrototypeInheritanceAst
from SPPCompiler.SemanticAnalysis.SupUseStatementAst import SupUseStatementAst

SupMemberAst = Union[
    ClassPrototypeAst,
    FunctionPrototypeAst,
    GlobalConstantAst,
    SupPrototypeInheritanceAst,
    SupUseStatementAst
]

__all__ = ["SupMemberAst"]
