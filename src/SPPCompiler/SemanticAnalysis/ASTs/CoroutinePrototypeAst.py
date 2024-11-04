from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.ASTs.FunctionPrototypeAst import FunctionPrototypeAst
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class CoroutinePrototypeAst(FunctionPrototypeAst):
    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        from SPPCompiler.SemanticAnalysis import TypeAst
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
        from SPPCompiler.SemanticAnalysis.Meta.AstErrors import AstErrors

        # Perform default function prototype semantic analysis.
        super().analyse_semantics(scope_manager, **kwargs)

        # Check the return type is a generator type.
        # Todo: Check the type superimposes a Gen type rather that is a Gen type.
        allowed_types = Seq([CommonTypes.GenMov(), CommonTypes.GenMut(), CommonTypes.GenRef()]).map(TypeAst.without_generics)
        if not allowed_types.any(lambda t: t.symbolic_eq(self.return_type.without_generics(), scope_manager.current_scope)):
            raise AstErrors.INVALID_COROUTINE_RETURN_TYPE(self.return_type)

        # Analyse the semantics of the function body.
        self.body.analyse_semantics(scope_manager, **kwargs)

        # Move out of the current scope.
        scope_manager.move_out_of_current_scope()


__all__ = ["CoroutinePrototypeAst"]
