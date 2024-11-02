from __future__ import annotations

import copy
from typing import TYPE_CHECKING
import difflib

from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.IdentifierAst import IdentifierAst
    from SPPCompiler.SemanticAnalysis.ASTs.GenericIdentifierAst import GenericIdentifierAst
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
    from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope
    from SPPCompiler.SemanticAnalysis.Scoping.Symbols import TypeSymbol


class AstTypeManagement:
    @staticmethod
    def get_namespaced_scope_with_error(scope_manager: ScopeManager, namespace: Seq[IdentifierAst]) -> Scope:
        from SPPCompiler.SemanticAnalysis.Meta.AstErrors import AstErrors
        from SPPCompiler.SemanticAnalysis.Scoping.Symbols import NamespaceSymbol

        # Work through each cumulative namespace, checking if the namespace exists.
        namespace_scope = scope_manager.current_scope
        for i in range(namespace.length):
            sub_namespace = namespace[:i + 1]

            # If the namespace does not exist, raise an error.
            if not scope_manager.get_namespaced_scope(sub_namespace):
                alternatives = namespace_scope.all_symbols().filter_to_type(NamespaceSymbol).map_attr("name")
                closest_match = difflib.get_close_matches(sub_namespace[-1].value, alternatives.map_attr("value"), n=1, cutoff=0)
                raise AstErrors.UNDEFINED_IDENTIFIER(sub_namespace[-1], closest_match[0] if closest_match else None)

            # Move into the next part of the namespace.
            namespace_scope = scope_manager.get_namespaced_scope(sub_namespace)

        # Return the final namespace scope.
        return namespace_scope

    @staticmethod
    def get_type_part_symbol_with_error(scope: Scope, type_part: GenericIdentifierAst, ignore_alias: bool = False, **kwargs) -> TypeSymbol:
        from SPPCompiler.SemanticAnalysis.Meta.AstErrors import AstErrors
        from SPPCompiler.SemanticAnalysis.Scoping.Symbols import TypeSymbol

        # Get the type part's symbol, and raise an error if it does not exist.
        type_symbol = scope.get_symbol(type_part, ignore_alias=ignore_alias, **kwargs)
        if not type_symbol:
            alternatives = scope.all_symbols().filter_to_type(TypeSymbol).map_attr("name")
            closest_match = difflib.get_close_matches(type_part.value, alternatives.map_attr("value"), n=1, cutoff=0)
            raise AstErrors.UNDEFINED_IDENTIFIER(type_part, closest_match[0] if closest_match else None)

        # Return the type part's scope from the symbol.
        return type_symbol

    @staticmethod
    def create_generic_scope(scope_manager: ScopeManager, type: TypeAst, type_part: GenericIdentifierAst, base_symbol: TypeSymbol) -> Scope:
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
        from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope
        from SPPCompiler.SemanticAnalysis.Scoping.Symbols import TypeSymbol

        new_scope = Scope(type_part, base_symbol.scope.parent)
        new_cls_proto = copy.deepcopy(base_symbol.type)
        new_symbol = TypeSymbol(name=type_part, type=new_cls_proto, scope=new_scope)
        new_scope.parent.add_symbol(new_symbol)
        new_scope._ast = new_cls_proto
        new_scope._direct_sup_scopes = base_symbol.scope._direct_sup_scopes
        new_scope._direct_sub_scopes = base_symbol.scope._direct_sub_scopes

        if type.without_generics() == CommonTypes.Tup().without_generics():
            return new_scope

        for generic_argument in type_part.generic_argument_group.arguments:
            generic_class_proto = scope_manager.current_scope.get_symbol(generic_argument.value).type
            generic_symbol = TypeSymbol(name=generic_argument.name.types[-1], type=generic_class_proto, scope=new_scope)
            new_scope.add_symbol(generic_symbol)

        return new_scope
