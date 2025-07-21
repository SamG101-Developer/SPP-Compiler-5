from __future__ import annotations

from dataclasses import dataclass

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstTypeUtils import AstTypeUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypesPrecompiled
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors


@dataclass(slots=True)
class SubroutinePrototypeAst(Asts.FunctionPrototypeAst):
    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # Perform default function prototype semantic analysis.
        Asts.FunctionPrototypeAst.analyse_semantics(self, sm, **kwargs)

        return_type_symbol = sm.current_scope.get_symbol(self.return_type)
        kwargs["function_type"] = self.tok_fun
        kwargs["function_ret_type"] = [return_type_symbol.fq_name]
        kwargs["function_scope"] = sm.current_scope

        # Analyse the semantics of the function body.
        self.body.analyse_semantics(sm, **kwargs)

        # Handle the "abort() => !" type.
        is_never = False
        if self.body.members and AstTypeUtils.symbolic_eq(self.body.members[-1].infer_type(sm, **(kwargs | {"ignore_else": True})), CommonTypesPrecompiled.NEVER, sm.current_scope, sm.current_scope):
            is_never = True

        # Check there is a return statement at the end (for non-void functions).
        not_void = not AstTypeUtils.symbolic_eq(self.return_type, CommonTypesPrecompiled.VOID, sm.current_scope, sm.current_scope)
        if not_void and not is_never and not (self._non_implemented or self._abstract) and not (self.body.members and type(self.body.members[-1]) is Asts.RetStatementAst):
            final_member = self.body.members[-1] if self.body.members else self.body.tok_r
            raise SemanticErrors.FunctionSubroutineMissingReturnStatementError().add(
                final_member, self.return_type).scopes(sm.current_scope)

        # Move out of the current scope.
        sm.move_out_of_current_scope()


__all__ = [
    "SubroutinePrototypeAst"]
