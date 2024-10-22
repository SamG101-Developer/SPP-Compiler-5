from typing import Union

from SPPCompiler.SemanticAnalysis.ClassPrototypeAst import ClassPrototypeAst
from SPPCompiler.SemanticAnalysis.FunctionPrototypeAst import FunctionPrototypeAst
from SPPCompiler.SemanticAnalysis.GlobalConstantAst import GlobalConstantAst
from SPPCompiler.SemanticAnalysis.SupPrototypeFunctionsAst import SupPrototypeFunctionsAst
from SPPCompiler.SemanticAnalysis.SupPrototypeInheritanceAst import SupPrototypeInheritanceAst
from SPPCompiler.SemanticAnalysis.UseStatementAst import UseStatementAst

type ModuleMemberAst = Union[
    ClassPrototypeAst,
    FunctionPrototypeAst,
    GlobalConstantAst,
    SupPrototypeFunctionsAst,
    SupPrototypeInheritanceAst,
    UseStatementAst]

__all__ = ["ModuleMemberAst"]
