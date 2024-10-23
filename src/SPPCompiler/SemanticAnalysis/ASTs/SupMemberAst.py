from typing import Union

from SPPCompiler.SemanticAnalysis.ASTs.ClassPrototypeAst import ClassPrototypeAst
from SPPCompiler.SemanticAnalysis.ASTs.GlobalConstantAst import GlobalConstantAst
from SPPCompiler.SemanticAnalysis.ASTs.FunctionPrototypeAst import FunctionPrototypeAst
from SPPCompiler.SemanticAnalysis.ASTs.SupPrototypeInheritanceAst import SupPrototypeInheritanceAst
from SPPCompiler.SemanticAnalysis.ASTs.SupUseStatementAst import SupUseStatementAst

SupMemberAst = Union[
    ClassPrototypeAst,
    FunctionPrototypeAst,
    GlobalConstantAst,
    SupPrototypeInheritanceAst,
    SupUseStatementAst
]

__all__ = ["SupMemberAst"]
