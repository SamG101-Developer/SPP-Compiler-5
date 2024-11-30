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
        from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors

        # Perform default function prototype semantic analysis.
        super().analyse_semantics(scope_manager, **kwargs)
        kwargs["function_type"] = self.tok_fun
        kwargs["function_ret_type"] = self.return_type

        # Analyse the semantics of the function body.
        self.body.analyse_semantics(scope_manager, **kwargs)

        # Check there is a return statement at the end (for non-void functions).
        non_void_return_type = not self.return_type.symbolic_eq(CommonTypes.Void(), scope_manager.current_scope)
        if non_void_return_type and not (self._non_implemented or self._abstract) and not (self.body.members and isinstance(self.body.members[-1], RetStatementAst)):
            final_member = self.body.members[-1] if self.body.members else self.body.tok_right_brace
            raise SemanticErrors.FunctionSubroutineMissingReturnStatementError().add(final_member, self.return_type)

        # Move out of the current scope.
        scope_manager.move_out_of_current_scope()


__all__ = ["SubroutinePrototypeAst"]
