from __future__ import annotations

from dataclasses import dataclass

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypesPrecompiled
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors


@dataclass(slots=True)
class SubroutinePrototypeAst(Asts.FunctionPrototypeAst):
    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # Perform default function prototype semantic analysis.
        Asts.FunctionPrototypeAst.analyse_semantics(self, sm, **kwargs)

        kwargs["function_type"] = self.tok_fun
        kwargs["function_ret_type"] = [sm.current_scope.get_symbol(self.return_type).fq_name]

        # Analyse the semantics of the function body.
        self.body.analyse_semantics(sm, **kwargs)

        # Check there is a return statement at the end (for non-void functions).
        non_void_return_type = not self.return_type.symbolic_eq(CommonTypesPrecompiled.VOID, sm.current_scope)
        if non_void_return_type and not (self._non_implemented or self._abstract) and not (self.body.members and isinstance(self.body.members[-1], Asts.RetStatementAst)):
            final_member = self.body.members[-1] if self.body.members else self.body.tok_r
            raise SemanticErrors.FunctionSubroutineMissingReturnStatementError().add(
                final_member, self.return_type).scopes(sm.current_scope)

        # Move out of the current scope.
        if "no_scope" not in kwargs:
            sm.move_out_of_current_scope()


__all__ = [
    "SubroutinePrototypeAst"]
