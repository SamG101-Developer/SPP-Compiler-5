from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.SupPrototypeFunctionsAst import SupPrototypeFunctionsAst

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.TypeAst import TypeAst


@dataclass
class SupPrototypeInheritanceAst(SupPrototypeFunctionsAst):
    tok_ext: TokenAst
    super_class: TypeAst


__all__ = ["SupPrototypeInheritanceAst"]
