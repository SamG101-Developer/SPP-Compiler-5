from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Optional, Self, Dict, Tuple, Iterator, TYPE_CHECKING

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstFunctionUtils import AstFunctionUtils
from SPPCompiler.SemanticAnalysis.AstUtils.AstTypeUtils import AstTypeUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Scoping.Symbols import AliasSymbol
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import AstPrinter, ast_printer_method
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypes, CommonTypesPrecompiled
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope


@dataclass
class TypeSingleAst(Asts.Ast, Asts.Mixins.AbstractTypeAst, Asts.Mixins.TypeInferrable):
    name: Asts.GenericIdentifierAst = field(default_factory=lambda: Asts.GenericIdentifierAst())

    def __eq__(self, other: TypeSingleAst) -> bool:
        if isinstance(other, Asts.TypeSingleAst):
            return self.name == other.name
        elif isinstance(other, Asts.IdentifierAst):
            return self.name.value == other.value
        return False

    def __hash__(self) -> int:
        return hash(self.name)

    def __iter__(self) -> Iterator[Asts.GenericIdentifierAst]:
        yield self.name
        for g in self.name.generic_argument_group.arguments:
            if isinstance(g.value, Asts.IdentifierAst):
                yield Asts.GenericIdentifierAst.from_identifier(g.value)
            else:
                yield from g.value

    def __json__(self) -> str:
        return self.name.value

    @staticmethod
    def from_identifier(ast: Asts.IdentifierAst) -> TypeSingleAst:
        return TypeSingleAst(pos=ast.pos, name=Asts.GenericIdentifierAst.from_identifier(ast))

    @staticmethod
    def from_generic_identifier(ast: Asts.GenericIdentifierAst) -> TypeSingleAst:
        return TypeSingleAst(pos=ast.pos, name=ast)

    @staticmethod
    def from_token(ast: Asts.TokenAst) -> TypeSingleAst:
        return TypeSingleAst.from_identifier(ast=Asts.IdentifierAst(pos=ast.pos, value=ast.token_data))

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        return f"{self.name}"

    @property
    def pos_end(self) -> int:
        return self.name.pos_end

    def convert(self) -> Asts.TypeAst:
        return self

    def fq_type_parts(self) -> Seq[Asts.IdentifierAst | Asts.GenericIdentifierAst | Asts.TokenAst]:
        return Seq([self.name])

    def type_parts(self) -> Seq[Asts.GenericIdentifierAst]:
        return Seq([self.name])

    def without_generics(self) -> Self:
        return TypeSingleAst(self.pos, self.name.without_generics())

    def sub_generics(self, generic_arguments: Seq[Asts.GenericArgumentAst]) -> Asts.TypeAst:
        name = copy.deepcopy(self.name)
        for generic_name, generic_type in generic_arguments.map(lambda a: (a.name, a.value)):
            if self == generic_name:
                return generic_type

            for g in name.generic_argument_group.get_type_args():  # comp args?
                g.value = g.value.sub_generics(generic_arguments)

            for g in name.generic_argument_group.get_comp_args().filter(lambda gg: isinstance(gg.value, Asts.TypeAst)):
                g.value = g.value.sub_generics(generic_arguments)

        return TypeSingleAst(self.pos, name)

    def get_corresponding_generic(self, that: Asts.TypeAst, generic_name: Asts.TypeSingleAst) -> Optional[Asts.TypeAst]:
        """
        GenericAttrClass[AA=testing::nested_generic_attr::GenericAttrClass[P=BB, AA=std::array::Arr[T=CC, n = 3, A=std::allocator::GlobalAlloc[E=CC]]]]
        GenericAttrClass[AA=testing::nested_generic_attr::GenericAttrClass[P=std::vector::Vec[T=std::string::Str], AA=std::array::Arr[T=std::number::bigint::BigInt, n = 3, A=std::allocator::GlobalAlloc[E=std::number::bigint::BigInt]]]]

        Given these two types, find a way to iterate through them to match CC against std::number::bigint::BigInt.
        Note that it is not guaranteed that the generic arguments are in the same order per type.

        :param that: The other type to compare against.
        :param generic_name: The target generic name to find.
        :return: The corresponding generic value on the other type, or None if not found.
        """

        def custom_iterate(t: Asts.TypeAst, depth: int) -> Iterator[Tuple[Asts.GenericArgumentAst, int]]:
            for g in t.type_parts()[-1].generic_argument_group.get_type_args():
                yield g, depth
                yield from custom_iterate(g.value, depth + 1)

        self_parts = custom_iterate(self, 0)
        that_parts = custom_iterate(that, 0)

        while True:
            try:
                # Get the next parts in the types.
                s, sd = next(self_parts)
                t, td = next(that_parts)

                # Align in the type-tree (nested generics).
                while td != sd:
                    t, td = next(that_parts)

                # Check for target generic.
                if str(t.value) == str(generic_name):
                    return s.value
            except StopIteration:
                break

        return None

    def contains_generic(self, generic_name: Asts.TypeSingleAst) -> bool:
        # todo: change this to use a custom iterator as-well.
        return any(g == Asts.GenericIdentifierAst.from_type(generic_name) for g in self)

    def symbolic_eq(self, that: Asts.TypeAst, self_scope: Scope, that_scope: Optional[Scope] = None, check_variant: bool = True, debug: bool = False) -> bool:
        that_scope = that_scope or self_scope
        that_scope, that = that.split_to_scope_and_type(that_scope)

        # Get the symbols of the types.
        self_symbol = self_scope.get_symbol(self.name)
        that_symbol = that_scope.get_symbol(that.name)

        if debug:
            print("-" * 100)
            print("SELF", self, self_scope, self_symbol)
            print("THAT", that, that_scope, that_symbol)

        # Variant type: one of the generic arguments must match the type.
        if check_variant and self_symbol.fq_name.type_parts()[0].generic_argument_group.arguments and self_symbol.fq_name.without_generics().symbolic_eq(CommonTypes.Var(0), self_scope, that_scope, check_variant=False):
            composite_types = self_symbol.name.generic_argument_group.arguments[0].value.type_parts()[0].generic_argument_group.arguments
            if composite_types.any(lambda t: t.value.symbolic_eq(that, self_scope, that_scope, debug=debug)):
                return True

        # Otherwise check the symbols are equal.
        return self_symbol.type is that_symbol.type

    def analyse_semantics(self, sm: ScopeManager, type_scope: Optional[Scope] = None, generic_infer_source: Optional[Dict] = None, generic_infer_target: Optional[Dict] = None, **kwargs) -> None:

        type_scope = type_scope or sm.current_scope
        original_type_scope = type_scope

        # Determine the type scope and type symbol.
        type_symbol = AstTypeUtils.get_type_part_symbol_with_error(original_type_scope, sm, self.name.without_generics(), ignore_alias=True)
        type_scope = type_symbol.scope
        if type_symbol.is_generic: return

        # Name all the generic arguments.
        is_tuple = type_symbol.fq_name.without_generics() == CommonTypesPrecompiled.EMPTY_TUPLE
        AstFunctionUtils.name_generic_arguments(
            self.name.generic_argument_group.arguments,
            type_symbol.type.generic_parameter_group.parameters,
            sm, is_tuple_owner=is_tuple)

        # If there is a directive to skip generic checks, then return.
        if "skip_generic_check" in kwargs:
            return

        # Infer generic arguments from information given from object initialization.
        self.name.generic_argument_group.arguments = AstFunctionUtils.infer_generic_arguments(
            generic_parameters=type_symbol.type.generic_parameter_group.parameters,
            optional_generic_parameters=type_symbol.type.generic_parameter_group.get_optional_params(),
            explicit_generic_arguments=self.name.generic_argument_group.arguments,
            infer_source=generic_infer_source or {},
            infer_target=generic_infer_target or {},
            sm=sm, owner=type_symbol.fq_name)

        # Analyse the semantics of the generic arguments.
        self.name.generic_argument_group.analyse_semantics(sm, **kwargs)

        # If the generically filled type doesn't exist (Vec[Str]), but the base does (Vec[T]), create it.
        if not type_scope.parent.has_symbol(self.name):
            new_scope = AstTypeUtils.create_generic_scope(sm, self.name, type_symbol, is_tuple=is_tuple)

            # Handle type aliasing (providing generics to the original type).
            if isinstance(type_symbol, AliasSymbol):
                # Substitute the old type: "Opt[Str]" => "Var[Some[Str], None]"
                generics = original_type_scope.generics + self.name.generic_argument_group.arguments
                old_type = type_symbol.old_sym.fq_name.sub_generics(generics)
                old_type.analyse_semantics(sm, type_scope=type_scope.parent, **kwargs)
                new_scope.type_symbol.old_sym = sm.current_scope.get_symbol(old_type)

                # Create a new aliasing symbol for the substituted new type.
                new_alias_symbol = AliasSymbol(
                    name=new_scope.type_symbol.name, type=new_scope.type_symbol.type, scope=new_scope,
                    scope_defined_in=new_scope.type_symbol.scope_defined_in,
                    is_generic=new_scope.type_symbol.is_generic, is_copyable=new_scope.type_symbol.is_copyable,
                    old_sym=sm.current_scope.get_symbol(old_type))

                new_scope.parent.rem_symbol(new_scope.type_symbol.name)
                new_scope.parent.add_symbol(new_alias_symbol)
                new_scope.type_symbol = new_alias_symbol

            type_symbol = new_scope.type_symbol

        else:
            type_symbol = type_scope.parent.get_symbol(self.name)

        # Check for the std::variant type, there are no types with conventions.
        # type_symbol = AstTypeUtils.get_type_part_symbol_with_error(type_scope.parent, sm, self.name)
        # print("Scopes:", type_scope, original_type_scope)
        # if type_symbol.fq_name.without_generics().symbolic_eq(CommonTypesPrecompiled.EMPTY_VARIANT, original_type_scope, debug=True):
        #     for generic_argument in type_symbol.fq_name.type_parts()[-1].generic_argument_group["Variants"].value.type_parts()[-1].generic_argument_group.arguments:
        #         if c := generic_argument.value.get_convention():
        #             raise SemanticErrors.InvalidConventionLocationError().add(
        #                 c, generic_argument.value, "variant composite type").scopes(sm.current_scope)

    def split_to_scope_and_type(self, scope: Scope) -> Tuple[Scope, Asts.TypeSingleAst]:
        return scope, self

    def get_convention(self) -> Optional[Asts.ConventionAst]:
        return None

    def without_conventions(self) -> Asts.TypeAst:
        return self

    def infer_type(self, sm: ScopeManager, type_scope: Optional[Scope] = None, **kwargs) -> Asts.TypeAst:
        type_scope  = type_scope or sm.current_scope
        type_symbol = type_scope.get_symbol(self.name)
        return type_symbol.fq_name


__all__ = [
    "TypeSingleAst"]
