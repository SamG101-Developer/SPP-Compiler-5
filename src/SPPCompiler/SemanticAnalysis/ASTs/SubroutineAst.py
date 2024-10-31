from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.ASTs.FunctionPrototypeAst import FunctionPrototypeAst

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class SubroutinePrototypeAst(FunctionPrototypeAst):
    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        from SPPCompiler.SemanticAnalysis import RetStatementAst
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
        from SPPCompiler.SemanticAnalysis.Meta.AstErrors import AstErrors

        # Perform default function prototype semantic analysis.
        super().analyse_semantics(scope_manager, **kwargs)

        # Analyse the semantics of the function body.
        self.body.analyse_semantics(scope_manager, **kwargs)

        # Check there is a return statement at the end (for non-void functions).
        if not self.return_type.symbolic_eq(CommonTypes.Void(), scope_manager.current_scope) and not isinstance(self.body.members[-1], RetStatementAst):
            raise AstErrors.MISSING_RETURN_STATEMENT(self.body.members[-1], self.return_type)

        # Move out of the current scope.
        scope_manager.move_out_of_current_scope()


__all__ = ["SubroutinePrototypeAst"]
