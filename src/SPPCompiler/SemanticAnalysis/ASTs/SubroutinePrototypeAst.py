from __future__ import annotations

from dataclasses import dataclass

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class SubroutinePrototypeAst(Asts.FunctionPrototypeAst):
    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # Perform default function prototype semantic analysis.
        super().analyse_semantics(scope_manager, **kwargs)
        kwargs["function_type"] = self.tok_fun
        kwargs["function_ret_type"] = scope_manager.current_scope.get_symbol(self.return_type).fq_name

        # Analyse the semantics of the function body.
        self.body.analyse_semantics(scope_manager, **kwargs)

        # Check there is a return statement at the end (for non-void functions).
        non_void_return_type = not self.return_type.symbolic_eq(CommonTypes.Void(), scope_manager.current_scope)
        if non_void_return_type and not (self._non_implemented or self._abstract) and not (self.body.members and isinstance(self.body.members[-1], Asts.RetStatementAst)):
            final_member = self.body.members[-1] if self.body.members else self.body.tok_right_brace
            raise SemanticErrors.FunctionSubroutineMissingReturnStatementError().add(final_member, self.return_type)

        # Move out of the current scope.
        scope_manager.move_out_of_current_scope()


__all__ = ["SubroutinePrototypeAst"]
