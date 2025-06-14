from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterator, List, Optional, TYPE_CHECKING, Tuple

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstFunctionUtils import AstFunctionUtils
from SPPCompiler.SemanticAnalysis.AstUtils.AstTypeUtils import AstTypeUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Scoping.Symbols import AliasSymbol, TypeSymbol
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import AstPrinter, ast_printer_method
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypes, CommonTypesPrecompiled
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors
from SPPCompiler.Utils.FastDeepcopy import fast_deepcopy
from SPPCompiler.Utils.FunctionCache import FunctionCache

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope


@dataclass(slots=True)
class TypeSingleAst(Asts.Ast, Asts.Mixins.AbstractTypeAst, Asts.Mixins.TypeInferrable):
    name: Asts.GenericIdentifierAst = field(default=None)

    def __eq__(self, other: TypeSingleAst | Asts.IdentifierAst) -> bool:
        if other.__class__ is Asts.TypeSingleAst:
            return self.name == other.name
        elif other.__class__ is Asts.IdentifierAst:
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

    def __deepcopy__(self, memodict=None) -> TypeSingleAst:
        return TypeSingleAst(pos=self.pos, name=fast_deepcopy(self.name))

    def __json__(self) -> str:
        return self.name.value

    def __str__(self) -> str:
        return f"{self.name}"

    @staticmethod
    def from_identifier(ast: Asts.IdentifierAst) -> TypeSingleAst:
        return TypeSingleAst(pos=ast.pos, name=Asts.GenericIdentifierAst.from_identifier(ast))

    @staticmethod
    def from_generic_identifier(ast: Asts.GenericIdentifierAst) -> TypeSingleAst:
        return TypeSingleAst(pos=ast.pos, name=ast)

    @staticmethod
    def from_token(ast: Asts.TokenAst) -> TypeSingleAst:
        return TypeSingleAst.from_generic_identifier(ast=Asts.GenericIdentifierAst(pos=ast.pos, value=ast.token_data))

    @staticmethod
    def from_string(ast: str) -> TypeSingleAst:
        from SPPCompiler.SemanticAnalysis.Utils.CodeInjection import CodeInjection
        from SPPCompiler.SyntacticAnalysis.Parser import SppParser
        return CodeInjection.inject_code(ast, SppParser.parse_type, pos_adjust=0)

    @property
    def fq_type_parts(self) -> List[Asts.IdentifierAst | Asts.GenericIdentifierAst | Asts.TokenAst]:
        return [self.name]

    @FunctionCache.cache_property
    def without_generics(self) -> Optional[Asts.TypeAst]:
        return TypeSingleAst(self.pos, self.name.without_generics)

    @property
    def without_conventions(self) -> Optional[Asts.TypeAst]:
        return self

    @property
    def convention(self) -> Optional[Asts.TypeAst]:
        return None

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        return f"{self.name.print(printer)}"

    @property
    def pos_end(self) -> int:
        return self.name.pos_end

    def convert(self) -> Asts.TypeAst:
        return self

    def substituted_generics(self, generic_arguments: List[Asts.GenericArgumentAst]) -> Asts.TypeAst:
        name = fast_deepcopy(self.name)
        for generic_name, generic_type in [(a.name, a.value) for a in generic_arguments]:
            if self == generic_name:
                return generic_type

            for g in name.generic_argument_group.get_comp_args():
                if isinstance(g.value, Asts.IdentifierAst):
                    if g.value == Asts.IdentifierAst.from_type(generic_name):
                        g.value = generic_type

        for g in name.generic_argument_group.get_type_args():
            g.value = g.value.substituted_generics(generic_arguments)

        return TypeSingleAst(pos=self.pos, name=name)

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
            for g in t.type_parts[-1].generic_argument_group.get_type_args():
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

    def contains_generic(self, generic_type: Asts.TypeSingleAst) -> bool:
        # todo: change this to use a custom iterator as-well.
        return any(g == Asts.GenericIdentifierAst.from_type(generic_type) for g in self)

    def get_symbol(self, scope: Scope) -> TypeSymbol:
        return scope.get_symbol(self.name.without_generics, exclusive=True)

    def qualify_types(self, sm: ScopeManager, **kwargs) -> None:
        for g in self.name.generic_argument_group.get_type_args():
            g.value.qualify_types(sm, **kwargs)
            try:
                g.value.analyse_semantics(sm, skip_generic_check=True, **kwargs)
            except SemanticErrors.IdentifierUnknownError:
                continue
            g.value = sm.current_scope.get_symbol(g.value.without_generics).fq_name.set_generics(g.value.type_parts[-1].generic_argument_group).with_convention(g.value.convention)

    def analyse_semantics(
            self, sm: ScopeManager, type_scope: Optional[Scope] = None, generic_infer_source: Optional[Dict] = None,
            generic_infer_target: Optional[Dict] = None, **kwargs) -> None:

        type_scope = type_scope or sm.current_scope
        original_scope = type_scope

        # Determine the type scope and type symbol.
        type_symbol = AstTypeUtils.get_type_part_symbol_with_error(original_scope, sm, self.name.without_generics, ignore_alias=True)
        type_scope = type_symbol.scope
        if type_symbol.is_generic: return

        # Name all the generic arguments.
        is_tuple = type_symbol.fq_name.without_generics == CommonTypesPrecompiled.EMPTY_TUPLE  # Think this is ok...
        AstFunctionUtils.name_generic_arguments(
            self.name.generic_argument_group.arguments,
            type_symbol.type.generic_parameter_group.parameters,
            sm, self, is_tuple_owner=is_tuple)

        # If there is a directive to skip generic checks, then return.
        if "skip_generic_check" in kwargs:
            return

        # Analyse the semantics of the generic arguments.
        self.name.generic_argument_group.analyse_semantics(sm, **kwargs)

        # Infer generic arguments from information given from object initialization.
        self.name.generic_argument_group.arguments = AstFunctionUtils.infer_generic_arguments(
            generic_parameters=type_symbol.type.generic_parameter_group.parameters,
            optional_generic_parameters=type_symbol.type.generic_parameter_group.get_optional_params(),
            explicit_generic_arguments=self.name.generic_argument_group.arguments,
            infer_source=generic_infer_source or {},
            infer_target=generic_infer_target or {},
            sm=sm,
            owner=AstTypeUtils.get_type_part_symbol_with_error(original_scope, sm, self.name.without_generics).fq_name,
            **kwargs)

        # For variant types, collapse any duplicate generic arguments.
        if AstTypeUtils.symbolic_eq(self.without_generics, CommonTypesPrecompiled.EMPTY_VARIANT, type_scope, sm.current_scope, check_variant=False, lhs_ignore_alias=True):
            composite_types = AstTypeUtils.deduplicate_composite_types(self, sm.current_scope)
            composite_types = CommonTypes.Tup(self.pos, composite_types)
            composite_types.analyse_semantics(sm, type_scope=type_scope, **kwargs)
            self.name.generic_argument_group.arguments[0].value = composite_types

        # If the generically filled type doesn't exist (Vec[Str]), but the base does (Vec[T]), create it.
        if not type_scope.parent.has_symbol(self.name):
            new_scope = AstTypeUtils.create_generic_scope(sm, self.name, type_symbol, is_tuple=is_tuple, **kwargs)

            # Handle type aliasing (providing generics to the original type).
            if type_symbol.__class__ is AliasSymbol:

                # Substitute the old type: "Opt[Str]" => "Var[Some[Str], None]"
                generics = self.name.generic_argument_group.arguments + original_scope.generics
                old_type = type_symbol.old_sym.fq_name.substituted_generics(generics)
                old_type.analyse_semantics(sm, type_scope=type_scope.parent, **kwargs)

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

    def infer_type(self, sm: ScopeManager, type_scope: Optional[Scope] = None, **kwargs) -> Asts.TypeAst:
        type_scope  = type_scope or sm.current_scope
        type_symbol = type_scope.get_symbol(self.name)
        return type_symbol.fq_name


__all__ = [
    "TypeSingleAst"]
