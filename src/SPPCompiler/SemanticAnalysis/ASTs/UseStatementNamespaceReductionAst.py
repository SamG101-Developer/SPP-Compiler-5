from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, Optional, TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.MultiStage.Stage2_SymbolGenerator import Stage2_SymbolGenerator
from SPPCompiler.SemanticAnalysis.MultiStage.Stage3_SupScopeLoader import Stage3_SupScopeLoader
from SPPCompiler.SemanticAnalysis.MultiStage.Stage4_SemanticAnalyser import Stage4_SemanticAnalyser
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.IdentifierAst import IdentifierAst
    from SPPCompiler.SemanticAnalysis.ASTs.UseStatementNamespaceReductionBodyAst import UseStatementNamespaceReductionBodyAst
    from SPPCompiler.SemanticAnalysis.ASTs.UseStatementTypeAliasAst import UseStatementTypeAliasAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class UseStatementNamespaceReductionAst(Ast, Stage2_SymbolGenerator, Stage3_SupScopeLoader, Stage4_SemanticAnalyser):
    body: UseStatementNamespaceReductionBodyAst

    _generated: bool = field(default=False, init=False, repr=False)
    _new_asts: Seq[UseStatementTypeAliasAst] = field(default_factory=Seq, init=False, repr=False)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        return self.body.print(printer)

    def _convert_to_type_aliases(self, scope_manager: ScopeManager) -> None:
        from SPPCompiler.SemanticAnalysis import UseStatementNamespaceReductionTypesMultipleAst, TypeAst, IdentifierAst
        from SPPCompiler.SemanticAnalysis import UseStatementNamespaceReductionTypesSingleAst, UseStatementTypeAliasAst
        from SPPCompiler.SemanticAnalysis import GenericCompParameterAst, GenericCompArgumentNamedAst
        from SPPCompiler.SemanticAnalysis import GenericTypeParameterAst, GenericTypeArgumentNamedAst
        from SPPCompiler.SemanticAnalysis import GenericArgumentGroupAst

        types = {}

        def merge_layers(ast: UseStatementNamespaceReductionBodyAst, current_ns: Seq[IdentifierAst]) -> None:
            if isinstance(ast.type, UseStatementNamespaceReductionTypesSingleAst):
                # Save the original length of the namespace, and add the next nested namespace.
                original_ns_len = current_ns.length
                current_ns += ast.type.namespace

                # Create a new type with the current namespace and the types from the import.
                new_type = TypeAst(-1, namespace=current_ns.copy(), types=ast.type.types)

                # Remove the nested namespace from the current namespace.
                for _ in range(current_ns.length - original_ns_len):
                    current_ns.pop()

                # Add the new type to the list of types.
                type_alias = TypeAst(-1, Seq(), ast.type.alias.type.types.copy()) if ast.type.alias else None
                types[new_type] = type_alias

            elif isinstance(ast.type, UseStatementNamespaceReductionTypesMultipleAst):
                # Save the original length of the namespace, and add the next nested namespace.
                original_ns_len = current_ns.length
                current_ns += ast.type.namespace

                # For each type in the import, recursively combine the layers.
                for inner_type in ast.type.types:
                    merge_layers(inner_type, current_ns)

                # Remove the nested namespace from the current namespace.
                for _ in range(current_ns.length - original_ns_len):
                    current_ns.pop()

        merge_layers(self.body, Seq())

        GenericArgumentCTor = {
            **{g: GenericCompArgumentNamedAst for g in GenericCompParameterAst.__value__.__args__},
            **{g: GenericTypeArgumentNamedAst for g in GenericTypeParameterAst.__value__.__args__}}

        for new_type, alias in types.items():
            generic_parameters = scope_manager.current_scope.get_symbol(new_type).type.generic_parameter_group
            generic_arguments = generic_parameters.parameters.map(lambda p: GenericArgumentCTor[type(p)].from_name_value(p.name, p.name))
            generic_arguments = GenericArgumentGroupAst.default(generic_arguments)
            new_type.types[-1].generic_argument_group = generic_arguments
            new_ast = UseStatementTypeAliasAst.from_types(IdentifierAst.from_type(alias or new_type), generic_parameters, new_type)
            self._new_asts.append(new_ast)
        self._generated = True

    def generate_symbols(self, scope_manager: ScopeManager) -> None:
        # Convert the import aliases to type aliases: "use std::Str" => "use std::Str as Str".
        self._convert_to_type_aliases(scope_manager)
        self._new_asts.for_each(lambda ast: ast.generate_symbols(scope_manager))

    def load_sup_scopes(self, scope_manager: ScopeManager) -> None:
        # Load the sup scopes of the new type aliases.
        self._new_asts.for_each(lambda ast: ast.load_sup_scopes(scope_manager))

    def inject_sup_scopes(self, scope_manager: ScopeManager) -> None:
        # Inject the sup scopes of the new type aliases.
        self._new_asts.for_each(lambda ast: ast.inject_sup_scopes(scope_manager))

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # Analyse the new type aliases.
        self._new_asts.for_each(lambda ast: ast.analyse_semantics(scope_manager, **kwargs))


__all__ = ["UseStatementNamespaceReductionAst"]
