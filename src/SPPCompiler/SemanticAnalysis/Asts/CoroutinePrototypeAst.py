from __future__ import annotations

from dataclasses import dataclass

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypesPrecompiled
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors


@dataclass(slots=True)
class CoroutinePrototypeAst(Asts.FunctionPrototypeAst):
    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # Perform default function prototype semantic analysis.
        Asts.FunctionPrototypeAst.analyse_semantics(self, sm, **kwargs)

        return_type_symbol = sm.current_scope.get_symbol(self.return_type)
        kwargs["function_type"] = self.tok_fun
        kwargs["function_ret_type"] = [return_type_symbol.fq_name]
        kwargs["function_scope"] = sm.current_scope

        # Check the return type superimposes the generator type.
        # Todo: use AstUtils.get_generator_and_yield_type here (+ try/except for error mod).
        superimposed_types = [t.without_generics() for t in return_type_symbol.scope.sup_types]
        superimposed_types.append(return_type_symbol.fq_name.without_generics())
        if not any(t.without_generics().symbolic_eq(CommonTypesPrecompiled.EMPTY_GENERATOR, sm.current_scope, sm.current_scope) for t in superimposed_types):
            raise SemanticErrors.FunctionCoroutineInvalidReturnTypeError().add(
                self.return_type).scopes(sm.current_scope)

        # Analyse the semantics of the function body.
        self.body.analyse_semantics(sm, **kwargs)

        # Move out of the current scope.
        sm.move_out_of_current_scope()


__all__ = [
    "CoroutinePrototypeAst"]
