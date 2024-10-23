from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.MultiStage.Stage1_PreProcessor import Stage1_PreProcessor, PreProcessingContext

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ModulePrototypeAst import ModulePrototypeAst
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst


@dataclass
class ProgramAst(Ast, Stage1_PreProcessor):
    module: ModulePrototypeAst
    tok_eof: TokenAst

    def pre_process(self, context: PreProcessingContext) -> None:
        super().pre_process(context)

        # Pre-process the module of this program.
        self.module.body.members.for_each(lambda m: m.pre_process(context))


__all__ = ["ProgramAst"]
