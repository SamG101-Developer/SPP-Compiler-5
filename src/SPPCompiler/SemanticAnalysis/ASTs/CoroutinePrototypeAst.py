from __future__ import annotations

from dataclasses import dataclass

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.Utils.Sequence import Seq


# Todo:
#  - Relax return type to superimpose a GenXXX type, rather than exactly match it


@dataclass
class CoroutinePrototypeAst(Asts.FunctionPrototypeAst):
    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # Perform default function prototype semantic analysis.
        super().analyse_semantics(scope_manager, **kwargs)
        kwargs["function_type"] = self.tok_fun
        kwargs["function_ret_type"] = scope_manager.current_scope.get_symbol(self.return_type).fq_name

        # Check the return type is a generator type.
        allowed_types = Seq([CommonTypes.GenMov(), CommonTypes.GenMut(), CommonTypes.GenRef()]).map(lambda t: t.without_generics())
        if not allowed_types.any(lambda t: t.symbolic_eq(self.return_type.without_generics(), scope_manager.current_scope)):
            raise SemanticErrors.FunctionCoroutineInvalidReturnTypeError().add(self.return_type)

        # Analyse the semantics of the function body.
        self.body.analyse_semantics(scope_manager, **kwargs)

        # Move out of the current scope.
        scope_manager.move_out_of_current_scope()


__all__ = ["CoroutinePrototypeAst"]
