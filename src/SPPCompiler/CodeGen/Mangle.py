from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis import Asts
    from SPPCompiler.SemanticAnalysis.Scoping.Symbols import TypeSymbol
    from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope


class Mangler:
    @staticmethod
    def mangle_type_name(symbol: TypeSymbol) -> str:
        fq_name = symbol.fq_name
        return str(fq_name)

    @staticmethod
    def mangle_module_name(scope: Scope) -> str:
        return "#".join([str(a.name) for a in reversed(scope.ancestors)])

    @staticmethod
    def mangle_function_name(scope: Scope, function: Asts.FunctionPrototypeAst) -> str:
        module_name = Mangler.mangle_module_name(scope)
        func_name = "".join([
            *[Mangler.mangle_type_name(scope.get_symbol(p.type)) for p in function.function_parameter_group.params],
            Mangler.mangle_type_name(scope.get_symbol(function.return_type))])
        return f"{module_name}#{func_name}"
