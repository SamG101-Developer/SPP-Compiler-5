from __future__ import annotations

import copy
import difflib
import types
from typing import Generator, Optional, TYPE_CHECKING

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.Symbols import AliasSymbol, NamespaceSymbol, Symbol, TypeSymbol, \
    VariableSymbol
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypesPrecompiled
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors
from SPPCompiler.Utils.FastDeepcopy import fast_deepcopy
from SPPCompiler.Utils.FunctionCache import FunctionCache
from SPPCompiler.Utils.Sequence import SequenceUtils

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
    def is_type_indexable(type: Asts.TypeAst, scope: Scope) -> bool:
        # Test for "Tup" type.
        if AstTypeUtils.is_type_tuple(type.without_generics, scope):
            return True

        # Test for "Arr" type.
        if AstTypeUtils.is_type_array(type.without_generics, scope):
            return True

        # No match for indexable types.
        return False

    @staticmethod
    def is_type_functional(type: Asts.TypeAst, scope: Scope) -> bool:
        # Test for "FunMov" type.
        if AstTypeUtils.symbolic_eq(type.without_generics, CommonTypesPrecompiled.EMPTY_FUN_MOV, scope, scope):
            return True

        # Test for "FunMut" type.
        if AstTypeUtils.symbolic_eq(type.without_generics, CommonTypesPrecompiled.EMPTY_FUN_MUT, scope, scope):
            return True

        # Test for "FunRef" type.
        if AstTypeUtils.symbolic_eq(type.without_generics, CommonTypesPrecompiled.EMPTY_FUN_REF, scope, scope):
            return True

        # No match for functional types.
        return False

    @staticmethod
    def is_type_generator(type: Asts.TypeAst, scope: Scope) -> bool:
        # Test for "Gen" type.
        if AstTypeUtils.symbolic_eq(type.without_generics, CommonTypesPrecompiled.EMPTY_GEN, scope, scope):
            return True

        # Test for "GenOnce" type.
        if AstTypeUtils.symbolic_eq(type.without_generics, CommonTypesPrecompiled.EMPTY_GEN_ONCE, scope, scope):
            return True

        # Test for "GenOpt" type.
        if AstTypeUtils.symbolic_eq(type.without_generics, CommonTypesPrecompiled.EMPTY_GEN_OPT, scope, scope):
            return True

        # Test for "GenRes" type.
        if AstTypeUtils.symbolic_eq(type.without_generics, CommonTypesPrecompiled.EMPTY_GEN_RES, scope, scope):
            return True

        # No match for generator types.
        return False

    @staticmethod
    def is_type_tuple(type: Asts.TypeAst, scope: Scope) -> bool:
        # Check if a type is a tuple type.
        is_tuple = AstTypeUtils.symbolic_eq(type.without_generics, CommonTypesPrecompiled.EMPTY_TUP, scope, scope, check_variant=False)
        return is_tuple

    @staticmethod
    def is_type_array(type: Asts.TypeAst, scope: Scope) -> bool:
        # Check if a type is an array type.
        is_array = AstTypeUtils.symbolic_eq(type.without_generics, CommonTypesPrecompiled.EMPTY_ARR, scope, scope, check_variant=False)
        return is_array

    @staticmethod
    def is_type_variant(type: Asts.TypeAst, scope: Scope) -> bool:
        # Check if a type is a variant type.
        is_variant = AstTypeUtils.symbolic_eq(type.without_generics, CommonTypesPrecompiled.EMPTY_VAR, scope, scope)
        return is_variant

    @staticmethod
    def is_index_within_type_bound(index: int, type: Asts.TypeAst, scope: Scope) -> bool:
        # Tuple type: count the number of generic arguments.
        if AstTypeUtils.is_type_tuple(type.without_generics, scope):
            return index < len(type.type_parts[0].generic_argument_group.arguments)

        # Array type: get the "n" generic comp argument.
        if AstTypeUtils.is_type_array(type.without_generics, scope):
            return index < int(type.type_parts[0].generic_argument_group.arguments[1].value.value.token_data)

        raise NotImplementedError("Only tuple and array types are indexable.")

    @staticmethod
    def get_nth_type_of_indexable_type(sm: ScopeManager, index: int, type: Asts.TypeAst) -> Asts.TypeAst:
        # Tuple type: get the nth generic argument.
        if AstTypeUtils.is_type_tuple(type.without_generics, sm.current_scope):
            return type.type_parts[0].generic_argument_group.arguments[index].value

        # Array type: get the first generic argument as an "Opt[T]" type (safety check).
        if AstTypeUtils.is_type_array(type.without_generics, sm.current_scope):
            return type.type_parts[0].generic_argument_group.arguments[0].value

        raise NotImplementedError("Only tuple and array types are indexable.")

    @staticmethod
    def get_namespaced_scope_with_error(sm: ScopeManager, namespace: list[Asts.IdentifierAst]) -> Scope:
        # Work through each cumulative namespace, checking if the namespace exists.
        namespace_scope = sm.current_scope
        for i in range(len(namespace)):
            sub_namespace = namespace[:i + 1]

            # If the namespace does not exist, raise an error.
            if not sm.get_namespaced_scope(sub_namespace):
                alternatives = [a.name.value for a in namespace_scope.all_symbols(sup_scope_search=True) if type(a) is NamespaceSymbol]
                closest_match = difflib.get_close_matches(sub_namespace[-1].value, alternatives, n=1, cutoff=0)
                raise SemanticErrors.IdentifierUnknownError().add(
                    sub_namespace[-1], "namespace", closest_match[0] if closest_match else None).scopes(sm.current_scope)

            # Move into the next part of the namespace.
            namespace_scope = sm.get_namespaced_scope(sub_namespace)

        # Return the final namespace scope.
        return namespace_scope

    @staticmethod
    def get_type_part_symbol_with_error(
            scope: Scope, sm: ScopeManager, type_part: Asts.TypeIdentifierAst, ignore_alias: bool = False,
            **kwargs) -> TypeSymbol | AliasSymbol:

        # Get the type part's symbol, and raise an error if it does not exist.
        type_symbol = scope.get_symbol(type_part, ignore_alias=ignore_alias, **kwargs)
        if not type_symbol:
            alternatives = [a.name.value for a in scope.all_symbols(sup_scope_search=True) if type(a) in [TypeSymbol, AliasSymbol]]
            SequenceUtils.remove_if(alternatives, lambda a: a[0] == "$")
            closest_match = difflib.get_close_matches(type_part.value, alternatives, n=1, cutoff=0)
            raise SemanticErrors.IdentifierUnknownError().add(
                type_part.without_generics, "type", closest_match[0] if closest_match else None).scopes(sm.current_scope)

        # Return the type part's scope from the symbol.
        return type_symbol

    @staticmethod
    def create_generic_cls_scope(
            sm: ScopeManager, type_part: Asts.TypeIdentifierAst, old_cls_symbol: TypeSymbol,
            external_generic_symbols: list[Symbol], is_tuple: bool, **kwargs) -> Scope:

        from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope

        # Create a new scope & symbol for the generic substituted type.
        # Todo: issue here is when using type statements in super blocks, because the base type of the type statement
        #  may be defined in a different block to where the specialization is being used, so it adds the specialization
        #  in the wrong sup scope, and it can't be accessed from where it needs to be accessed.
        new_cls_scope = Scope(
            name=fast_deepcopy(type_part), parent=old_cls_symbol.scope.parent, ast=old_cls_symbol.scope._ast)

        new_cls_symbol = TypeSymbol(
            name=type_part, type=new_cls_scope._ast, scope=new_cls_scope,
            is_generic=old_cls_symbol.is_generic, visibility=old_cls_symbol.visibility, scope_defined_in=sm.current_scope)
        new_cls_symbol.is_copyable = types.MethodType(lambda self: old_cls_symbol.is_copyable(), new_cls_symbol)

        # Configure the new scope based on the base scope, register non-generic scope as the base scope.
        new_cls_scope.parent.add_symbol(new_cls_symbol)
        new_cls_scope._children = old_cls_symbol.scope.children
        new_cls_scope._symbol_table = fast_deepcopy(old_cls_symbol.scope._symbol_table)
        new_cls_scope._non_generic_scope = old_cls_symbol.scope
        if type(new_cls_scope.parent.name) is not str:
            new_cls_scope.parent.children.append(new_cls_scope)

        if kwargs["stage"] > 7:
            sm.attach_super_scopes_helper(new_cls_scope, **kwargs)

        # No more checks for the tuple type (avoid recursion).
        if is_tuple: return new_cls_scope

        for e in external_generic_symbols:
            new_cls_scope.add_symbol(e)

        # Register the generic arguments as type symbols in the new scope.
        for generic_argument in type_part.generic_argument_group.arguments:
            generic_symbol = AstTypeUtils.create_generic_symbol(sm, generic_argument)
            new_cls_scope.add_symbol(generic_symbol)

        # Run generic substitution on the symbols in the new scope. (todo: analyse new types?)
        for scoped_sym in new_cls_scope.all_symbols(exclusive=True):
            if type(scoped_sym) is VariableSymbol:
                scoped_sym.type = scoped_sym.type.substituted_generics(type_part.generic_argument_group.arguments)

        # Duplicate the ast to validate the type substituted attributes (no borrows etc).
        new_ast = fast_deepcopy(new_cls_scope._ast)
        for attribute in new_ast.body.members:
            attribute.type = attribute.type.substituted_generics(type_part.generic_argument_group.arguments)
            attribute.analyse_semantics(sm, **kwargs)

        # Return the new scope.
        return new_cls_scope

    @staticmethod
    def create_generic_fun_scope(
            sm: ScopeManager, old_fun_scope: Scope, generic_arguments: Asts.GenericArgumentGroupAst,
            external_generic_symbols: list[Symbol], **kwargs) -> Scope:

        from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope
        from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager

        # Create the "fun" scope that will be a replacement. The children and symbol table are copied over.
        new_fun_scope_name = fast_deepcopy(old_fun_scope.name)
        new_fun_scope = Scope(new_fun_scope_name, old_fun_scope.parent, ast=old_fun_scope._ast)
        new_fun_scope._children = [copy.copy(c) for c in old_fun_scope.children]
        for c in new_fun_scope._children:
            c._parent = new_fun_scope
        sm = ScopeManager(sm.global_scope, new_fun_scope, nsbs=sm.normal_sup_blocks, gsbs=sm.generic_sup_blocks)

        for e in external_generic_symbols:
            new_fun_scope.add_symbol(e)

        # Add the generic arguments to the new scope.
        for generic_argument in generic_arguments.arguments:
            generic_symbol = AstTypeUtils.create_generic_symbol(sm, generic_argument)
            new_fun_scope.add_symbol(generic_symbol)

        return new_fun_scope

    @staticmethod
    def create_generic_sup_scope(
            sm: ScopeManager, old_sup_scope: Scope, new_cls_scope: Scope, generic_arguments: Asts.GenericArgumentGroupAst,
            external_generic_symbols: list[Symbol], **kwargs) -> tuple[Scope, Scope]:

        from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope
        from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager

        # Create the "sup" scope that will be a replacement. The children and symbol table are copied over.
        # self_type, new_sup_scope_name = AstTypeUtils.generic_convert_sup_scope_name(old_sup_scope.name, generic_arguments, old_sup_scope._ast.name.pos)
        self_type = old_sup_scope._ast.name.substituted_generics(generic_arguments.arguments)
        new_sup_scope_name = old_sup_scope.name

        new_sup_scope = Scope(new_sup_scope_name, old_sup_scope.parent, ast=old_sup_scope._ast)
        new_sup_scope._children = [copy.copy(c) for c in old_sup_scope.children]
        for c in new_sup_scope._children:
            c._parent = new_sup_scope
        new_sup_scope._symbol_table = fast_deepcopy(old_sup_scope._symbol_table)
        new_sup_scope.parent.children.append(new_sup_scope)
        sm = ScopeManager(sm.global_scope, new_sup_scope, nsbs=sm.normal_sup_blocks, gsbs=sm.generic_sup_blocks)

        # Add external generic arguments into the new scope.
        for e in external_generic_symbols:
            new_sup_scope.add_symbol(e)

        # Add the generic arguments to the new scope.
        for generic_argument in generic_arguments.arguments:
            generic_symbol = AstTypeUtils.create_generic_symbol(sm, generic_argument)
            new_sup_scope.add_symbol(generic_symbol)

        # Add the "Self" symbol into the new scope.
        self_type.analyse_semantics(sm, **kwargs)
        old_self_sym = new_sup_scope.get_symbol(self_type)
        assert old_self_sym is not None
        new_sup_scope.add_symbol(AliasSymbol(
            name=Asts.TypeIdentifierAst(value="Self"),
            type=None,
            scope=new_cls_scope,
            scope_defined_in=new_sup_scope,
            old_sym=old_self_sym))

        # Run generic substitution on the aliases in the new scope.
        for scoped_sym in new_sup_scope.all_symbols(exclusive=True):

            # Defined as "type X = Y"
            if type(scoped_sym) is AliasSymbol and not scoped_sym.is_generic:
                old_type_sub = scoped_sym.old_sym.fq_name.substituted_generics(generic_arguments.arguments)
                scoped_sym.old_sym = old_sup_scope.get_symbol(old_type_sub) or scoped_sym.old_sym
                if scoped_sym.scope in old_sup_scope.children:
                    scoped_sym.scope = new_sup_scope.children[old_sup_scope.children.index(scoped_sym.scope)]

            # Defined as "cmp var = n"
            # Todo: filter these because it is collecting non-cmp variable symbols too.
            # Todo: iterate the generic arguments and substitute the type for the variable symbol.
            if type(scoped_sym) is VariableSymbol:
                old_type_sub = scoped_sym.type.substituted_generics(generic_arguments.arguments)
                scoped_sym.type = old_type_sub

        # Create the scope for the new super class type. This will handle recursive sup-scope creation.
        super_cls_scope = None
        if type(old_sup_scope._ast) is Asts.SupPrototypeExtensionAst:
            new_fq_super_type = fast_deepcopy(old_sup_scope._ast.super_class)
            new_fq_super_type = new_fq_super_type.substituted_generics(generic_arguments.arguments)
            new_fq_super_type.analyse_semantics(sm, **kwargs)
            super_cls_scope = new_cls_scope.get_symbol(new_fq_super_type).scope

        return new_sup_scope, super_cls_scope

    @staticmethod
    def create_generic_symbol(
            sm: ScopeManager, generic_argument: Asts.GenericArgumentAst,
            tm: Optional[ScopeManager] = None) -> TypeSymbol | VariableSymbol:

        # Get the type symbol of the generic argument's value.
        true_value_symbol = sm.current_scope.get_symbol(generic_argument.value)

        # For type generic arguments, create a new type symbol with the generic argument's name and value.
        if type(generic_argument) is Asts.GenericTypeArgumentNamedAst:
            return TypeSymbol(
                name=generic_argument.name.type_parts[0],
                type=true_value_symbol.type if true_value_symbol else None,
                scope=true_value_symbol.scope if true_value_symbol else None,
                is_generic=True,
                convention=generic_argument.value.convention,
                scope_defined_in=sm.current_scope)

        # For comp generic arguments, create a new variable symbol with the generic argument's name and value.
        elif type(generic_argument) is Asts.GenericCompArgumentNamedAst:
            v = VariableSymbol(
                name=Asts.IdentifierAst.from_type(generic_argument.name),
                type=(tm or sm).current_scope.get_symbol(generic_argument.value.infer_type(tm or sm)).fq_name,
                is_generic=True)

            # Mark the memory info as a compile-time constant.
            v.memory_info.ast_comptime_const = generic_argument
            return v

        raise Exception(f"Unknown generic argument type '{type(generic_argument).__name__}': {generic_argument}")

    @staticmethod
    def generic_convert_sup_scope_name(name: str, generics: Asts.GenericArgumentGroupAst, pos: int) -> tuple[Asts.TypeAst, str]:
        parts = name.split("#")

        # Replace the generics in the "sup Here" part of the name.
        if " ext " not in parts[1]:
            t = Asts.TypeIdentifierAst.from_string(parts[1].strip()).substituted_generics(generics.arguments)  # , copy=False)
            return t, f"{parts[0]}#{t}#{parts[2]}"

        # Replace the generics in the "sup Here1 ext Here2" parts of the name.
        else:
            t = Asts.TypeIdentifierAst.from_string(parts[1].split(" ext ")[0].strip()).substituted_generics(generics.arguments)  # , copy=False)
            u = Asts.TypeIdentifierAst.from_string(parts[1].split(" ext ")[1].strip()).substituted_generics(generics.arguments)  # , copy=False)
            return t, f"{parts[0]}#{t} ext {u}#{parts[2]}"

    @staticmethod
    def is_type_recursive(type: Asts.ClassPrototypeAst, sm: ScopeManager) -> Optional[Asts.TypeAst]:

        # Define the internal function to recursively search for attribute types.
        def get_attribute_types(
                class_prototype: Asts.ClassPrototypeAst,
                class_scope: Scope) -> Generator[tuple[Asts.ClassPrototypeAst, Asts.TypeAst]]:

            for attribute in class_prototype.body.members:
                symbol = class_scope.get_symbol(attribute.type)

                # Skip generics (can never be a "recursive" type). Todo: this is a hack that works
                if symbol and symbol.type:
                    yield symbol.type, attribute.type
                    yield from get_attribute_types(symbol.type, symbol.scope)

        # Get the attribute types recursively from the class prototype, and check for a match with the class prototype.
        for attribute_cls_prototype, attribute_ast in get_attribute_types(type, sm.current_scope):
            if attribute_cls_prototype is type:
                return attribute_ast

        # If the type isn't recursive, return None.
        return None

    @staticmethod
    def get_generator_and_yielded_type(
            type: Asts.TypeAst, sm: ScopeManager, expr: Asts.ExpressionAst,
            what: str) -> tuple[Asts.TypeAst, Asts.TypeAst, bool, bool, bool, Asts.TypeAst]:

        """
        Get the generator type, and the yielded type from a type. Search the super types of the input type for a
        generator type, and return it along with the extracted `Yield` type.
        """

        # Generic types are not generators, so raise an error.
        if sm.current_scope.get_symbol(type).scope is None:
            raise SemanticErrors.ExpressionNotGeneratorError().add(
                expr, type, what).scopes(sm.current_scope)

        # Initialize the generic type to None, and get all the super types.
        gen_type = None
        sup_types = sm.current_scope.get_symbol(type).scope.sup_types + [type]

        # Search through the type and supertypes for a generator type.
        for sup_type in sup_types:
            if AstTypeUtils.is_type_generator(sup_type.without_generics, sm.current_scope):
                gen_type = sup_type
                break

        # If no generator type was found associated with the type, raise an error.
        if gen_type is None:
            raise SemanticErrors.ExpressionNotGeneratorError().add(
                expr, type, what).scopes(sm.current_scope)

        # Extract the "Yield" generic argument's value from the generator type.
        yield_type = gen_type.type_parts[-1].generic_argument_group["Yield"].value

        # Extract the multiplicity, optionality and fallibility from the generator type.
        is_once     = AstTypeUtils.symbolic_eq(CommonTypesPrecompiled.EMPTY_GEN_ONCE, gen_type, sm.current_scope, sm.current_scope)
        is_optional = AstTypeUtils.symbolic_eq(CommonTypesPrecompiled.EMPTY_GEN_OPT, gen_type, sm.current_scope, sm.current_scope)
        is_fallible = AstTypeUtils.symbolic_eq(CommonTypesPrecompiled.EMPTY_GEN_RES, gen_type, sm.current_scope, sm.current_scope)
        if is_fallible:
            error_type = gen_type.type_parts[-1].generic_argument_group["Err"].value
        else:
            error_type = CommonTypesPrecompiled.VOID

        # Return all the information about the generator type.
        return gen_type, yield_type, is_once, is_optional, is_fallible, error_type

    @staticmethod
    def deduplicate_composite_types(type: Asts.TypeIdentifierAst, scope: Scope) -> list[Asts.TypeAst]:
        """
        Given a variant type, such as "Str or Bool or Bool or U32", create a list of the composite types, including
        nested variants. This example will return [Str, Bool, Bool, U32]. Semantic analysis will collapse any
        duplicates.

        :param type: The incoming variant type.
        :param scope: The scope for comparing the type against "Var".
        :return: The list of composite types.
        """

        out = []
        if not type.type_parts[-1].generic_argument_group.arguments:
            return out

        for generic_arg in type.type_parts[-1].generic_argument_group.arguments[0].value.type_parts[-1].generic_argument_group.arguments:
            # Inspect inner variant types by extending the composite type list.
            if AstTypeUtils.is_type_variant(generic_arg.value.without_generics, scope):
                out.extend(AstTypeUtils.deduplicate_composite_types(generic_arg.value, scope))

            # Ensure there are no borrowed types inside the variant type.
            elif (c := generic_arg.value.convention) is not None:
                raise SemanticErrors.InvalidConventionLocationError().add(c, generic_arg, "variant type argument").scopes(scope)

            # Inspect a non-variant type, and if it hasn't been added to the list, add it.
            elif not any(AstTypeUtils.symbolic_eq(generic_arg.value, a, scope, scope) for a in out):
                out.append(generic_arg.value)
        return out

    @staticmethod
    @FunctionCache.cache
    def symbolic_eq(
            lhs_type: Asts.TypeAst, rhs_type: Asts.TypeAst, lhs_scope: Scope, rhs_scope: Scope,
            check_variant: bool = True, lhs_ignore_alias: bool = False) -> bool:

        """
        Compare the two types for symbolic equality. This ensures that they are the exact same type, and not just
        textually the same.

        :param lhs_type: The left-hand side type to compare.
        :param rhs_type: The right-hand side type to compare.
        :param lhs_scope: The scope to get the left-hand side type from.
        :param rhs_scope: The scope to get the right-hand side type from.
        :param check_variant: Whether to allow variant type matching.
        :param lhs_ignore_alias: Whether to ignore alias types on the left-hand side.
        :return: Whether the two types are equal.

        TODO: Need to add a function checker. So if the lhs_type is like FunRef[...], and the RHS is a collection of
            function overloads,then as long as one overload matches, it should be accepted. Something like iterate the
            function overloads for the $Func type, and use AstFunctionUtils to check for an overload conflict =>
            complete match?
        """

        # Handle generic comp arguments (simple value comparison).
        if not lhs_type.is_type_ast:
            return lhs_type == rhs_type

        # Handle the "!" never type.
        if rhs_type.is_never_type():
            return True
        if lhs_type.is_never_type():
            return rhs_type.is_never_type()

        # Do a convention-match check.
        if type(lhs_type.convention) is not type(rhs_type.convention):
            if not (type(lhs_type.convention) is Asts.ConventionRefAst and type(rhs_type.convention) is Asts.ConventionMutAst):
                return False

        # Strip the generics from the types.
        stripped_lhs = lhs_type.without_generics
        stripped_rhs = rhs_type.without_generics

        # First step is to get the symbols for the non-generic versions of both types.
        stripped_lhs_symbol = lhs_scope.get_symbol(stripped_lhs, ignore_alias=lhs_ignore_alias)
        stripped_rhs_symbol = rhs_scope.get_symbol(stripped_rhs)

        # If the left-hand-side is a Variant type, then check the composite types first.
        if check_variant and AstTypeUtils.symbolic_eq(stripped_lhs_symbol.fq_name.without_generics, CommonTypesPrecompiled.EMPTY_VAR, lhs_scope, lhs_scope, check_variant=False):
            lhs_composite_types = AstTypeUtils.deduplicate_composite_types(lhs_scope.get_symbol(lhs_type).fq_name, lhs_scope)

            # Check each composite type against the other.
            for lhs_composite_type in lhs_composite_types:
                if AstTypeUtils.symbolic_eq(lhs_composite_type, rhs_type, lhs_scope, rhs_scope):
                    return True

        # If the stripped types are not equal, return false.
        if stripped_lhs_symbol.type is not stripped_rhs_symbol.type:
            return False

        # The next step is to get the generic arguments for both types.
        lhs_type_fq = lhs_scope.get_symbol(lhs_type, ignore_alias=lhs_ignore_alias).fq_name
        rhs_type_fq = rhs_scope.get_symbol(rhs_type).fq_name

        lhs_generics = lhs_type_fq.type_parts[-1].generic_argument_group.arguments
        rhs_generics = rhs_type_fq.type_parts[-1].generic_argument_group.arguments

        # Special case for variadic parameter types.
        shared_generic_parameters = lhs_scope.get_symbol(lhs_type).type.generic_parameter_group.parameters if lhs_scope.get_symbol(lhs_type).type else []
        if shared_generic_parameters and isinstance(shared_generic_parameters[-1], Asts.GenericParameterVariadicAst):
            if len(lhs_generics) != len(rhs_generics):
                return False

        # Ensure each generic argument is symbolically equal to the other.
        for lhs_generic, rhs_generic in zip(lhs_generics, rhs_generics):
            if not AstTypeUtils.symbolic_eq(lhs_generic.value, rhs_generic.value, lhs_scope, rhs_scope):
                return False

        # If all the generic arguments are equal, return true.
        return True

    @staticmethod
    # @FunctionCache.cache
    def relaxed_symbolic_eq(
            lhs_type: Asts.TypeAst, rhs_type: Asts.TypeAst, lhs_scope: Scope, rhs_scope: Scope,
            generics: Optional[dict] = None) -> bool:

        """
        The relaxed version of the symbolic equality check is the same as normal symbolic matching, but it allows a
        generic to be matched against any type. For example, `Vec[Str]` will match `[T] Vec[T]`. This is required in
        superimpositions, for fallthrough generic types to have the correct sup-ext blocks applied. Similarly,
        `Vec[Str]` will also match against `[T] T` (blanket superimpositions), because `T` itself would be a generic.

        Notably, `check_variant` is not present in this function, because "Str | Bool" cannot have the methods of `Str`
        and `Bool` (use pattern matching to extract), and both Str and Bool can't have methods attached to the variant,
        as they are different types (Str vs Var[Str, Bool] etc).

        :param lhs_type: The left-hand side type to compare.
        :param rhs_type: The right-hand side type to compare.
        :param lhs_scope: The scope to get the left-hand side type from.
        :param rhs_scope: The scope to get the right-hand side type from.
        :param generics: The generics that have been accepted as relaxed comparative (value = generic).
        :return: Whether the two types are equal.
        """

        from SPPCompiler.SemanticAnalysis.Asts import TypeIdentifierAst

        generics = generics if generics is not None else {}

        # If the rhs scope is None, then the scope itself is generic, so auto match it.
        if rhs_scope is None:
            return True

        # Handle generic comp arguments (simple value comparison).
        if not lhs_type.is_type_ast:
            if type(rhs_type) is Asts.IdentifierAst:
                generics[TypeIdentifierAst.from_identifier(rhs_type)] = lhs_type
                return True
            return lhs_type == rhs_type

        # Strip the generics from the rhs type (possibly generic).
        stripped_rhs = rhs_type.without_generics

        # If the right hand side is generic, then return a match: "sup [T] T { ... }" matches all types.
        stripped_rhs_symbol = rhs_scope.get_symbol(stripped_rhs)
        if stripped_rhs_symbol.is_generic:
            generics[stripped_rhs] = lhs_type
            return True

        # Strip the generics from the lhs type.
        stripped_lhs = lhs_type.without_generics

        # If the stripped types are not equal, return false.
        stripped_lhs_symbol = lhs_scope.get_symbol(stripped_lhs)
        if stripped_lhs_symbol.type is not stripped_rhs_symbol.type:
            return False

        # The next step is to get the generic arguments for both types.
        lhs_sym = lhs_scope.get_symbol(lhs_type)
        rhs_sym = rhs_scope.get_symbol(rhs_type)

        lhs_type_fq = lhs_sym.fq_name
        rhs_type_fq = rhs_sym.fq_name

        lhs_generics = lhs_type_fq.type_parts[-1].generic_argument_group.arguments
        rhs_generics = rhs_type_fq.type_parts[-1].generic_argument_group.arguments

        # Special case for variadic parameter types.
        shared_generic_parameters = lhs_sym.type.generic_parameter_group
        if shared_generic_parameters.parameters and shared_generic_parameters.get_variadic_params():
            if len(lhs_generics) != len(rhs_generics):
                return False

        # Ensure each generic argument is symbolically equal to the other.
        for lhs_generic, rhs_generic in zip(lhs_generics, rhs_generics):
            if not AstTypeUtils.relaxed_symbolic_eq(lhs_generic.value, rhs_generic.value, lhs_scope, rhs_scope, generics):
                return False

        # If all the generic arguments are equal, return true.
        return True


__all__ = [
    "AstTypeUtils",
]
