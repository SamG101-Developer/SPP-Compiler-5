from typing import Union

from SPPCompiler.SemanticAnalysis.ASTs.ClassPrototypeAst import ClassPrototypeAst
from SPPCompiler.SemanticAnalysis.ASTs.FunctionPrototypeAst import FunctionPrototypeAst
from SPPCompiler.SemanticAnalysis.ASTs.GlobalConstantAst import GlobalConstantAst
from SPPCompiler.SemanticAnalysis.ASTs.SupPrototypeFunctionsAst import SupPrototypeFunctionsAst
from SPPCompiler.SemanticAnalysis.ASTs.SupPrototypeInheritanceAst import SupPrototypeInheritanceAst
from SPPCompiler.SemanticAnalysis.ASTs.UseStatementAst import UseStatementAst

type ModuleMemberAst = Union[
    ClassPrototypeAst,
    FunctionPrototypeAst,
    GlobalConstantAst,
    SupPrototypeFunctionsAst,
    SupPrototypeInheritanceAst,
    UseStatementAst]

__all__ = ["ModuleMemberAst"]
