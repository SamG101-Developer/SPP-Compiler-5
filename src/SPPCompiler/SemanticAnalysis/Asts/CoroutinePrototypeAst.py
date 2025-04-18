from __future__ import annotations

from dataclasses import dataclass

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypesPrecompiled
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors


@dataclass
class CoroutinePrototypeAst(Asts.FunctionPrototypeAst):
    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # Perform default function prototype semantic analysis.
        super().analyse_semantics(sm, **kwargs)
        return_type_symbol = sm.current_scope.get_symbol(self.return_type)
        kwargs["function_type"] = self.tok_fun
        kwargs["function_ret_type"] = return_type_symbol.fq_name

        # Check the return type superimposes the generator type.
        superimposed_types = return_type_symbol.scope.sup_types.map(lambda t: t.without_generics())
        superimposed_types.append(return_type_symbol.fq_name.without_generics())
        if not superimposed_types.any(lambda t: t.without_generics().symbolic_eq(CommonTypesPrecompiled.EMPTY_GENERATOR, sm.current_scope)):
            raise SemanticErrors.FunctionCoroutineInvalidReturnTypeError().add(
                self.return_type).scopes(sm.current_scope)

        # Analyse the semantics of the function body.
        self.body.analyse_semantics(sm, **kwargs)

        # Move out of the current scope.
        if "no_scope" not in kwargs:
            sm.move_out_of_current_scope()


__all__ = [
    "CoroutinePrototypeAst"]
