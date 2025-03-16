from __future__ import annotations

import builtins
import copy
import difflib
from typing import Generator, Optional, Tuple

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Meta.AstMutation import AstMutation
from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Scoping.Symbols import AliasSymbol, NamespaceSymbol, TypeSymbol, VariableSymbol
from SPPCompiler.SyntacticAnalysis.Parser import SppParser
from SPPCompiler.Utils.Sequence import Seq


class AstTypeManagement:
    @staticmethod
    def is_type_indexable(type: Asts.TypeAst, scope: Scope) -> bool:
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypesPrecompiled

        # Only tuple and array types are indexable.
        is_tuple = type.without_generics().symbolic_eq(CommonTypesPrecompiled.EMPTY_TUPLE, scope)
        is_array = type.without_generics().symbolic_eq(CommonTypesPrecompiled.EMPTY_ARRAY, scope)
        return is_tuple or is_array

    @staticmethod
    def is_index_within_type_bound(index: int, type: Asts.TypeAst, scope: Scope) -> bool:
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypesPrecompiled

        # Tuple type: count the number of generic arguments.
        if type.without_generics().symbolic_eq(CommonTypesPrecompiled.EMPTY_TUPLE, scope):
            return index < type.type_parts()[0].generic_argument_group.arguments.length

        # Array type: get the "n" generic comp argument.
        if type.without_generics().symbolic_eq(CommonTypesPrecompiled.EMPTY_ARRAY, scope):
            return index < int(type.type_parts()[0].generic_argument_group.arguments[1].value.value.token_data)

        raise NotImplementedError("Only tuple and array types are indexable.")

    @staticmethod
    def get_nth_type_of_indexable_type(index: int, type: Asts.TypeAst, scope: Scope) -> Asts.TypeAst:
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypesPrecompiled

        # Tuple type: get the nth generic argument.
        if type.without_generics().symbolic_eq(CommonTypesPrecompiled.EMPTY_TUPLE, scope):
            return type.type_parts()[0].generic_argument_group.arguments[index].value

        # Array type: get the first generic argument.
        if type.without_generics().symbolic_eq(CommonTypesPrecompiled.EMPTY_ARRAY, scope):
            return type.type_parts()[0].generic_argument_group.arguments[0].value

        raise NotImplementedError("Only tuple and array types are indexable.")

    @staticmethod
    def get_namespaced_scope_with_error(scope_manager: ScopeManager, namespace: Seq[Asts.IdentifierAst]) -> Scope:
        # Work through each cumulative namespace, checking if the namespace exists.
        namespace_scope = scope_manager.current_scope
        for i in range(namespace.length):
            sub_namespace = namespace[:i + 1]

            # If the namespace does not exist, raise an error.
            if not scope_manager.get_namespaced_scope(sub_namespace):
                alternatives = namespace_scope.all_symbols().filter_to_type(NamespaceSymbol).map_attr("name")
                closest_match = difflib.get_close_matches(sub_namespace[-1].value, alternatives.map_attr("value"), n=1, cutoff=0)
                raise SemanticErrors.IdentifierUnknownError().add(sub_namespace[-1], "namespace", closest_match[0] if closest_match else None).scopes(scope_manager.current_scope)

            # Move into the next part of the namespace.
            namespace_scope = scope_manager.get_namespaced_scope(sub_namespace)

        # Return the final namespace scope.
        return namespace_scope

    @staticmethod
    def get_type_part_symbol_with_error(scope: Scope, scope_manager: ScopeManager, type_part: Asts.GenericIdentifierAst, ignore_alias: bool = False, **kwargs) -> TypeSymbol:
        # Get the type part's symbol, and raise an error if it does not exist.
        type_symbol = scope.get_symbol(type_part, ignore_alias=ignore_alias, **kwargs)
        if not type_symbol:
            alternatives = scope.all_symbols().filter_to_type(TypeSymbol).map_attr("name")
            alternatives.remove_if(lambda a: a.value[0] == "$")
            closest_match = difflib.get_close_matches(type_part.value, alternatives.map_attr("value"), n=1, cutoff=0)
            raise SemanticErrors.IdentifierUnknownError().add(type_part, "type", closest_match[0] if closest_match else None).scopes(scope_manager.current_scope)

        # Return the type part's scope from the symbol.
        return type_symbol

    @staticmethod
    def create_generic_scope(
            scope_manager: ScopeManager, type: Asts.TypeAst, type_part: Asts.GenericIdentifierAst,
            base_symbol: TypeSymbol)\
            -> Scope:

        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypesPrecompiled

        # Create a new scope & symbol for the generic substituted type.
        new_scope = Scope(type_part, base_symbol.scope.parent, ast=copy.deepcopy(base_symbol.scope._ast))
        new_symbol = builtins.type(base_symbol)(
            name=type_part, type=new_scope._ast, scope=new_scope, is_copyable=base_symbol.is_copyable,
            is_abstract=base_symbol.is_abstract, visibility=base_symbol.visibility)
        if isinstance(base_symbol, AliasSymbol):
            new_symbol.old_type = base_symbol.old_type

        # Configure the new scope based on the base scope, register non-generic scope as the base scope.
        new_scope.parent.add_symbol(new_symbol)
        new_scope._children = base_symbol.scope._children
        new_scope._symbol_table = copy.deepcopy(base_symbol.scope._symbol_table)
        new_scope._direct_sup_scopes = AstTypeManagement.create_generic_sup_scopes(scope_manager, base_symbol.scope, type_part.generic_argument_group)
        new_scope._direct_sub_scopes = base_symbol.scope._direct_sub_scopes
        new_scope._non_generic_scope = base_symbol.scope

        # No more checks for the tuple type (avoid recursion, is textual because it is to do with generics).
        if type and type.without_generics() == CommonTypesPrecompiled.EMPTY_TUPLE:
            return new_scope

        # Register the generic arguments as type symbols in the new scope.
        for generic_argument in type_part.generic_argument_group.arguments:
            generic_symbol = AstTypeManagement.create_generic_symbol(scope_manager, generic_argument)
            new_scope.add_symbol(generic_symbol)

        # Substitute the generics of the attribute types in the new class prototype.
        # temp_manager = ScopeManager(global_scope=scope_manager.global_scope, current_scop=new_scope)
        # print("\tTEMP MANAGER:", temp_manager.current_scope)
        # for attribute in new_scope._ast.body.members:
        #     print("\tATTR:", attribute)
        #     attribute.type = attribute.type.sub_generics(type_part.generic_argument_group.arguments)
        #     print("\t\tSUBBED ATTR:", attribute)
        #     attribute.type.analyse_semantics(temp_manager)

        # Return the new scope.
        return new_scope

    @staticmethod
    def create_generic_sup_scopes(
            scope_manager: ScopeManager, base_scope: Scope, generic_arguments: Asts.GenericArgumentGroupAst)\
            -> Seq[Scope]:

        old_scopes = base_scope._direct_sup_scopes
        new_scopes = Seq()

        for scope in old_scopes:

            # Create the scope with the generic arguments injected. This will handle recursive scope creation.
            if isinstance(scope._ast, Asts.ClassPrototypeAst):
                # The superimposition-ext checker handles these scopes.
                continue

            # Create the scope for the new super class type. This will handle recursive sup-scope creation.
            elif isinstance(scope._ast, Asts.SupPrototypeExtensionAst):
                temp_manager = ScopeManager(scope_manager.global_scope, base_scope.parent)
                new_fq_super_type = copy.deepcopy(scope._ast.super_class)
                new_fq_super_type = new_fq_super_type.sub_generics(generic_arguments.arguments)
                new_fq_super_type.analyse_semantics(temp_manager)

                # Get the class scope generated for the super class and add it to the new scopes too.
                modified_class_scope = temp_manager.current_scope.get_symbol(new_fq_super_type).scope
                if modified_class_scope not in new_scopes:
                    new_scopes.append(modified_class_scope)

            # Create the "sup" scope that will be a replacement. The children and symbol table are copied over.
            new_scope_name = AstTypeManagement.generic_convert_sup_scope_name(scope.name, generic_arguments, scope._ast.name.pos)
            new_scope = Scope(new_scope_name, scope.parent, ast=scope._ast)
            new_scope._children = scope._children
            new_scope._symbol_table = copy.copy(scope._symbol_table)
            new_scope._non_generic_scope = scope

            # Add the generic arguments to the new scope.
            for generic_argument in generic_arguments.arguments:
                generic_symbol = AstTypeManagement.create_generic_symbol(scope_manager, generic_argument)
                new_scope.add_symbol(generic_symbol)

            # Add the new scope to the list of new scopes.
            new_scopes.append(new_scope)

        # Return the new scopes.
        return new_scopes

    @staticmethod
    def create_generic_symbol(
            scope_manager: ScopeManager, generic_argument: Asts.GenericArgumentAst)\
            -> TypeSymbol | VariableSymbol:

        true_value_symbol = scope_manager.current_scope.get_symbol(generic_argument.value)

        if isinstance(generic_argument, Asts.GenericTypeArgumentNamedAst):
            return TypeSymbol(name=generic_argument.name.type_parts()[0], type=true_value_symbol.type if true_value_symbol else None, scope=true_value_symbol.scope if true_value_symbol else None, is_generic=True)

        elif isinstance(generic_argument, Asts.GenericCompArgumentNamedAst):
            return VariableSymbol(name=Asts.IdentifierAst.from_type(generic_argument.name), type=generic_argument.value.infer_type(scope_manager), is_generic=True)

        raise Exception(f"Unknown generic argument type: {type(generic_argument).__name__}")

    @staticmethod
    def generic_convert_sup_scope_name(name: str, generics: Asts.GenericArgumentGroupAst, pos: int) -> str:
        parts = name.split(":")

        if " ext " not in parts:
            t = AstMutation.inject_code(parts[1], SppParser.parse_type, pos_adjust=pos).sub_generics(generics.arguments)
            return f"{parts[0]}:{t}:{parts[2]}"

        else:
            t = AstMutation.inject_code(parts[1].split(" ext ")[0], SppParser.parse_type, pos_adjust=pos).sub_generics(generics.arguments)
            u = AstMutation.inject_code(parts[1].split(" ext ")[1], SppParser.parse_type, pos_adjust=pos).sub_generics(generics.arguments)
            return f"{parts[0]}:#{t} ext {u}:{parts[2]}"

    @staticmethod
    def is_type_recursive(type: Asts.ClassPrototypeAst, scope_manager: ScopeManager) -> Optional[Asts.TypeAst]:

        def get_attribute_types(class_prototype: Asts.ClassPrototypeAst, class_scope: Scope) -> Generator[Tuple[Asts.ClassPrototypeAst, Asts.TypeAst]]:

            for attribute in class_prototype.body.members:
                raw_attribute_type = attribute.type
                symbol = class_scope.get_symbol(raw_attribute_type)

                # Skip generics (can never be a "recursive" type). Todo: this is a hack that works
                if symbol and symbol.type:
                    yield symbol.type, attribute.type
                    yield from get_attribute_types(symbol.type, symbol.scope)

        for attribute_cls_prototype, attribute_ast in get_attribute_types(type, scope_manager.current_scope):
            if attribute_cls_prototype is type:
                return attribute_ast
