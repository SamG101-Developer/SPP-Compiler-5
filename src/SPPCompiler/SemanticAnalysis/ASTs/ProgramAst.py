from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.MultiStage.Stage1_PreProcessor import Stage1_PreProcessor, PreProcessingContext
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ModulePrototypeAst import ModulePrototypeAst


@dataclass
class ProgramAst(Ast, Stage1_PreProcessor):
    modules: Seq[ModulePrototypeAst]
    _current: Optional[ModulePrototypeAst] = field(default=None, init=False, repr=False)

    def pre_process(self, context: PreProcessingContext) -> None:
        super().pre_process(context)

        # Pre-process each module of this program.
        for module in self.modules:
            self._current = module
            module.body.members.for_each(lambda m: m.pre_process(module))

    def current(self) -> ModulePrototypeAst:
        return self._current


__all__ = ["ProgramAst"]
