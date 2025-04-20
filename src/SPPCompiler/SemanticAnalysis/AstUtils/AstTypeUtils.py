from __future__ import annotations

import copy
import difflib
from typing import Generator, Optional, Tuple, TYPE_CHECKING

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.Symbols import AliasSymbol, NamespaceSymbol, TypeSymbol, VariableSymbol
from SPPCompiler.SemanticAnalysis.Utils.CodeInjection import CodeInjection
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypesPrecompiled
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors
from SPPCompiler.SyntacticAnalysis.Parser import SppParser
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


class AstTypeUtils:
    """!
    Type utility methods that mostly revolve around generic types, creating new scopes and synbols for them, and#
    organising the super-scopes for generic substitutions. This is one of the most complex set of helper functions in
    the compiler, and uses detailed scoping and symbol checks.
    """

    @staticmethod
    def get_generics_in_scope(scope: Scope) -> Asts.GenericArgumentGroupAst:
        generic_argument_ctor = {VariableSymbol: Asts.GenericCompArgumentNamedAst, TypeSymbol: Asts.GenericTypeArgumentNamedAst}
        generics = scope._symbol_table.all().filter(lambda s: s.is_generic)
        generics = generics.map(lambda s: generic_argument_ctor[type(s)].from_symbol(s))
        generics = Asts.GenericArgumentGroupAst(arguments=generics)
        return generics

    @staticmethod
    def is_type_indexable(type: Asts.TypeAst, scope: Scope) -> bool:
        # Only tuple and array types are indexable.
        is_tuple = type.without_generics().symbolic_eq(CommonTypesPrecompiled.EMPTY_TUPLE, scope)
        is_array = type.without_generics().symbolic_eq(CommonTypesPrecompiled.EMPTY_ARRAY, scope)
        return is_tuple or is_array

    @staticmethod
    def is_index_within_type_bound(index: int, type: Asts.TypeAst, scope: Scope) -> bool:
        # Tuple type: count the number of generic arguments.
        if type.without_generics().symbolic_eq(CommonTypesPrecompiled.EMPTY_TUPLE, scope):
            return index < type.type_parts()[0].generic_argument_group.arguments.length

        # Array type: get the "n" generic comp argument.
        if type.without_generics().symbolic_eq(CommonTypesPrecompiled.EMPTY_ARRAY, scope):
            return index < int(type.type_parts()[0].generic_argument_group.arguments[1].value.value.token_data)

        raise NotImplementedError("Only tuple and array types are indexable.")

    @staticmethod
    def get_nth_type_of_indexable_type(sm: ScopeManager, index: int, type: Asts.TypeAst) -> Asts.TypeAst:
        # Tuple type: get the nth generic argument.
        if type.without_generics().symbolic_eq(CommonTypesPrecompiled.EMPTY_TUPLE, sm.current_scope):
            return type.type_parts()[0].generic_argument_group.arguments[index].value

        # Array type: get the first generic argument as an "Opt[T]" type (safety check).
        if type.without_generics().symbolic_eq(CommonTypesPrecompiled.EMPTY_ARRAY, sm.current_scope):
            return type.type_parts()[0].generic_argument_group.arguments[0].value

        # Array type: get the first generic argument as an "Opt[T]" type (safety check).
        # if type.without_generics().symbolic_eq(CommonTypesPrecompiled.EMPTY_ARRAY, sm.current_scope):
        #     safe_type = CommonTypes.Opt(type.pos, type.type_parts()[0].generic_argument_group.arguments[0].value)
        #     safe_type.analyse_semantics(sm)
        #     return safe_type

        raise NotImplementedError("Only tuple and array types are indexable.")

    @staticmethod
    def get_namespaced_scope_with_error(sm: ScopeManager, namespace: Seq[Asts.IdentifierAst]) -> Scope:
        # Work through each cumulative namespace, checking if the namespace exists.
        namespace_scope = sm.current_scope
        for i in range(namespace.length):
            sub_namespace = namespace[:i + 1]

            # If the namespace does not exist, raise an error.
            if not sm.get_namespaced_scope(sub_namespace):
                alternatives = namespace_scope.all_symbols().filter_to_type(NamespaceSymbol).map_attr("name")
                closest_match = difflib.get_close_matches(sub_namespace[-1].value, alternatives.map_attr("value"), n=1, cutoff=0)
                raise SemanticErrors.IdentifierUnknownError().add(
                    sub_namespace[-1], "namespace", closest_match[0] if closest_match else None).scopes(sm.current_scope)

            # Move into the next part of the namespace.
            namespace_scope = sm.get_namespaced_scope(sub_namespace)

        # Return the final namespace scope.
        return namespace_scope

    @staticmethod
    def get_type_part_symbol_with_error(
            scope: Scope, sm: ScopeManager, type_part: Asts.GenericIdentifierAst, ignore_alias: bool = False, **kwargs)\
            -> TypeSymbol | AliasSymbol:

        # Get the type part's symbol, and raise an error if it does not exist.
        type_symbol = scope.get_symbol(type_part, ignore_alias=ignore_alias, **kwargs)
        if not type_symbol:
            alternatives = scope.all_symbols().filter_to_type(TypeSymbol).map_attr("name")
            alternatives.remove_if(lambda a: a.value[0] == "$")
            closest_match = difflib.get_close_matches(type_part.value, alternatives.map_attr("value"), n=1, cutoff=0)
            raise SemanticErrors.IdentifierUnknownError().add(
                type_part, "type", closest_match[0] if closest_match else None).scopes(sm.current_scope)

        # Return the type part's scope from the symbol.
        return type_symbol

    @staticmethod
    def create_generic_scope(
            sm: ScopeManager, type_part: Asts.GenericIdentifierAst, base_symbol: TypeSymbol, is_tuple: bool) -> Scope:

        from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope
        from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager

        # Create a new scope & symbol for the generic substituted type.
        new_cls_prototype = copy.deepcopy(base_symbol.scope._ast)
        new_scope = Scope(type_part, base_symbol.scope.parent, ast=new_cls_prototype)
        new_symbol = TypeSymbol(
            name=type_part, type=new_scope._ast, scope=new_scope, is_copyable=base_symbol.is_copyable,
            visibility=base_symbol.visibility, scope_defined_in=sm.current_scope)

        # Configure the new scope based on the base scope, register non-generic scope as the base scope.
        new_scope.parent.add_symbol(new_symbol)
        new_scope._children = base_symbol.scope._children
        new_scope._symbol_table = copy.deepcopy(base_symbol.scope._symbol_table)

        # No more checks for the tuple type (avoid recursion, is textual because it is to do with generics).
        if is_tuple: return new_scope

        # Register the generic arguments as type symbols in the new scope.
        for generic_argument in type_part.generic_argument_group.arguments:
            generic_symbol = AstTypeUtils.create_generic_symbol(sm, generic_argument)
            new_scope.add_symbol(generic_symbol)

        new_scope._direct_sup_scopes = AstTypeUtils.create_generic_sup_scopes(sm, base_symbol.scope, new_scope, type_part.generic_argument_group)
        new_scope._direct_sub_scopes = base_symbol.scope._direct_sub_scopes
        new_scope._non_generic_scope = base_symbol.scope

        tm = ScopeManager(sm.global_scope, new_scope)
        for attribute in new_scope._ast.body.members:
            attribute.type = attribute.type.sub_generics(type_part.generic_argument_group.arguments)
            attribute.analyse_semantics(tm)

        # Return the new scope.
        return new_scope

    @staticmethod
    def create_generic_sup_scopes(
            sm: ScopeManager, base_scope: Scope, true_scope: Scope,
            generic_arguments: Asts.GenericArgumentGroupAst) -> Seq[Scope]:

        from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope

        old_scopes = base_scope._direct_sup_scopes
        new_scopes = Seq()

        for scope in old_scopes:

            # Create the scope with the generic arguments injected. This will handle recursive scope creation.
            if isinstance(scope._ast, Asts.ClassPrototypeAst):
                # The superimposition-ext checker handles these scopes.
                continue

            # Create the scope for the new super class type. This will handle recursive sup-scope creation.
            elif isinstance(scope._ast, Asts.SupPrototypeExtensionAst):
                new_fq_super_type = copy.deepcopy(scope._ast.super_class)
                new_fq_super_type = new_fq_super_type.sub_generics(generic_arguments.arguments)
                new_fq_super_type.analyse_semantics(sm)

                # Get the class scope generated for the super class and add it to the new scopes too.
                modified_class_scope = true_scope.get_symbol(new_fq_super_type).scope
                if modified_class_scope not in new_scopes:
                    new_scopes.append(modified_class_scope)

            # Create the "sup" scope that will be a replacement. The children and symbol table are copied over.
            new_scope_name = AstTypeUtils.generic_convert_sup_scope_name(scope.name, generic_arguments, scope._ast.name.pos)
            new_scope = Scope(new_scope_name, scope.parent, ast=scope._ast)
            new_scope._children = scope._children
            new_scope._symbol_table = copy.copy(scope._symbol_table)
            new_scope._non_generic_scope = scope

            # Add the generic arguments to the new scope.
            for generic_argument in generic_arguments.arguments:
                generic_symbol = AstTypeUtils.create_generic_symbol(sm, generic_argument)
                new_scope.add_symbol(generic_symbol)

            # Add the new scope to the list of new scopes.
            new_scopes.append(new_scope)

        # Return the new scopes.
        return new_scopes

    @staticmethod
    def create_generic_symbol(sm: ScopeManager, generic_argument: Asts.GenericArgumentAst) -> TypeSymbol | VariableSymbol:

        true_value_symbol = sm.current_scope.get_symbol(generic_argument.value)

        if isinstance(generic_argument, Asts.GenericTypeArgumentNamedAst):
            return TypeSymbol(
                name=generic_argument.name.type_parts()[0], type=true_value_symbol.type if true_value_symbol else None,
                scope=true_value_symbol.scope if true_value_symbol else None, is_generic=True,
                convention=generic_argument.value.get_convention())

        elif isinstance(generic_argument, Asts.GenericCompArgumentNamedAst):
            return VariableSymbol(
                name=Asts.IdentifierAst.from_type(generic_argument.name), type=generic_argument.value.infer_type(sm),
                is_generic=True)

        raise Exception(f"Unknown generic argument type '{type(generic_argument).__name__}': {generic_argument}")

    @staticmethod
    def generic_convert_sup_scope_name(name: str, generics: Asts.GenericArgumentGroupAst, pos: int) -> str:
        parts = name.split(":")

        if " ext " not in parts:
            t = CodeInjection.inject_code(parts[1], SppParser.parse_type, pos_adjust=pos).sub_generics(generics.arguments)
            return f"{parts[0]}:{t}:{parts[2]}"

        else:
            t = CodeInjection.inject_code(parts[1].split(" ext ")[0], SppParser.parse_type, pos_adjust=pos).sub_generics(generics.arguments)
            u = CodeInjection.inject_code(parts[1].split(" ext ")[1], SppParser.parse_type, pos_adjust=pos).sub_generics(generics.arguments)
            return f"{parts[0]}:#{t} ext {u}:{parts[2]}"

    @staticmethod
    def is_type_recursive(type: Asts.ClassPrototypeAst, sm: ScopeManager) -> Optional[Asts.TypeAst]:

        def get_attribute_types(class_prototype: Asts.ClassPrototypeAst, class_scope: Scope) -> Generator[Tuple[Asts.ClassPrototypeAst, Asts.TypeAst]]:

            for attribute in class_prototype.body.members:
                raw_attribute_type = attribute.type
                symbol = class_scope.get_symbol(raw_attribute_type)

                # Skip generics (can never be a "recursive" type). Todo: this is a hack that works
                if symbol and symbol.type:
                    yield symbol.type, attribute.type
                    yield from get_attribute_types(symbol.type, symbol.scope)

        for attribute_cls_prototype, attribute_ast in get_attribute_types(type, sm.current_scope):
            if attribute_cls_prototype is type:
                return attribute_ast
            return None
        return None
