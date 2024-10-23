from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.MultiStage.Stage1_PreProcessor import PreProcessingContext
from SPPCompiler.SemanticAnalysis.ASTs.SupPrototypeFunctionsAst import SupPrototypeFunctionsAst

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst


@dataclass
class SupPrototypeInheritanceAst(SupPrototypeFunctionsAst):
    tok_ext: TokenAst
    super_class: TypeAst

    def pre_process(self, context: PreProcessingContext) -> None:
        if self.super_class.types[-1].value in ["FunMov", "FunMut", "FunRef"]:  # Todo: more solid check
            return
        super().pre_process(context)


__all__ = ["SupPrototypeInheritanceAst"]
