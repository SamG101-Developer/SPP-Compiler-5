from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterator, Optional, TYPE_CHECKING

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstFunctionUtils import AstFunctionUtils
from SPPCompiler.SemanticAnalysis.AstUtils.AstTypeUtils import AstTypeUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Scoping.Symbols import AliasSymbol, NamespaceSymbol, TypeSymbol
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import AstPrinter, ast_printer_method
from SPPCompiler.SemanticAnalysis.Utils.CodeInjection import CodeInjection
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypes, CommonTypesPrecompiled
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors
from SPPCompiler.SyntacticAnalysis.Parser import SppParser
from SPPCompiler.Utils.FastDeepcopy import fast_deepcopy
from SPPCompiler.Utils.FunctionCache import FunctionCache

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope


@dataclass(slots=True, repr=False)
class TypeIdentifierAst(Asts.Ast, Asts.Mixins.AbstractTypeAst, Asts.Mixins.TypeInferrable):
    value: str = field(default="")
    generic_argument_group: Asts.GenericArgumentGroupAst = field(default=None)
    is_never: bool = field(default=False, repr=False)

    def __post_init__(self) -> None:
        self.generic_argument_group = self.generic_argument_group or Asts.GenericArgumentGroupAst(pos=0)
        self.is_type_ast = True

    def __eq__(self, other: TypeIdentifierAst | Asts.IdentifierAst) -> bool:
        if type(other) is TypeIdentifierAst:
            return self.value == other.value and self.generic_argument_group == other.generic_argument_group
        elif type(other) is Asts.IdentifierAst:
            return self.value == other.value
        return False

    def __hash__(self) -> int:
        return hash(self.value)

    def __iter__(self) -> Iterator[Asts.TypeIdentifierAst]:
        yield self
        for g in self.generic_argument_group.arguments:
            if type(g.value) is Asts.IdentifierAst:
                yield Asts.TypeIdentifierAst.from_identifier(g.value)
            else:
                yield from g.value

    def __deepcopy__(self, memodict=None) -> TypeIdentifierAst:
        return TypeIdentifierAst(
            pos=self.pos, value=self.value, generic_argument_group=fast_deepcopy(self.generic_argument_group),
            is_never=self.is_never)

    def __json__(self) -> str:
        return self.value

    def __str__(self) -> str:
        string = [
            self.value,
            str(self.generic_argument_group)]
        return "".join(string)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.value,
            self.generic_argument_group.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.pos + len(self.value)

    @staticmethod
    def from_identifier(ast: Asts.IdentifierAst) -> TypeIdentifierAst:
        return TypeIdentifierAst(pos=ast.pos, value=ast.value)

    @staticmethod
    def from_token(ast: Asts.TokenAst) -> TypeIdentifierAst:
        return TypeIdentifierAst(pos=ast.pos, value=ast.token_data)

    @staticmethod
    def from_string(value: str) -> TypeIdentifierAst:
        return CodeInjection.inject_code(value, SppParser.parse_type, pos_adjust=0)

    @staticmethod
    def never_type(pos: int = 0) -> TypeIdentifierAst:
        return TypeIdentifierAst(pos=pos, value="Never", is_never=True)

    def convert(self) -> Asts.TypeAst:
        return self

    def is_never_type(self) -> bool:
        return self.is_never

    @property
    def fq_type_parts(self) -> list[Asts.IdentifierAst | Asts.TypeIdentifierAst | Asts.TokenAst]:
        return [self]

    @property
    def namespace_parts(self) -> list[Asts.IdentifierAst]:
        return []

    @property
    def type_parts(self) -> list[Asts.TypeIdentifierAst | Asts.TokenAst]:
        return [self]

    @property
    def without_convention(self) -> Optional[Asts.TypeAst]:
        return self

    @property
    def convention(self) -> Optional[Asts.ConventionAst]:
        return None

    @FunctionCache.cache_property
    def without_generics(self) -> Optional[Asts.TypeAst]:
        return TypeIdentifierAst(self.pos, self.value)

    def substituted_generics(self, generic_arguments: list[Asts.GenericArgumentAst]) -> Asts.TypeAst:
        name = fast_deepcopy(self)
        for generic_arg_name, generic_arg_value in [(a.name, a.value) for a in generic_arguments]:
            if self == generic_arg_name:
                return generic_arg_value

            for g in name.generic_argument_group.get_comp_args():
                if type(g.value) is Asts.IdentifierAst:
                    if g.value == Asts.IdentifierAst.from_type(generic_arg_name):
                        g.value = generic_arg_value

        # Recursively substitute the type args. Todo: types on comp args?
        for g in name.generic_argument_group.get_type_args():
            g.value = g.value.substituted_generics(generic_arguments)

        return name

    def match_generic(self, that: Asts.TypeAst, generic_name: Asts.TypeIdentifierAst) -> Optional[Asts.TypeAst]:
        """
        GenericAttrClass[AA=testing::nested_generic_attr::GenericAttrClass[P=BB, AA=std::array::Arr[T=CC, n = 3, A=std::allocator::GlobalAlloc[E=CC]]]]
        GenericAttrClass[AA=testing::nested_generic_attr::GenericAttrClass[P=std::vector::Vec[T=std::string::Str], AA=std::array::Arr[T=std::number::bigint::BigInt, n = 3, A=std::allocator::GlobalAlloc[E=std::number::bigint::BigInt]]]]

        Given these two types, find a way to iterate through them to match CC against std::number::bigint::BigInt.
        Note that it is not guaranteed that the generic arguments are in the same order per type.

        :param that: The other type to compare against.
        :param generic_name: The target generic name to find.
        :return: The corresponding generic value on the other type, or None if not found.
        """

        # Early return if this type is the generic directly.
        if str(that) == str(generic_name):
            return self

        # Todo: comp args will probably fail here?
        def custom_iterate(t: Asts.TypeAst, depth: int) -> Iterator[tuple[Asts.GenericArgumentAst, int]]:
            for g in t.type_parts[-1].generic_argument_group.arguments:
                yield g, depth
                if isinstance(g, Asts.GenericTypeArgumentAst):
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

    def contains_generic(self, generic_type: Asts.TypeIdentifierAst) -> bool:
        # Todo: change this to use a custom iterator as-well?
        return generic_type in self

    def qualify_types(self, sm: ScopeManager, **kwargs) -> None:
        # todo: qualify the types on the comp args? like "cmp a: X"
        for g in self.generic_argument_group.get_type_args():
            g.value.qualify_types(sm, **kwargs)
            try:
                g.value.analyse_semantics(sm, skip_generic_check=True, **kwargs)
            except SemanticErrors.IdentifierUnknownError:
                continue

            try:
                generics = sm.current_scope.get_symbol(g.value).fq_name.type_parts[-1].generic_argument_group
            except AttributeError:
                generics = g.value.type_parts[-1].generic_argument_group
            g.value = sm.current_scope.get_symbol(g.value.without_generics).fq_name.with_generics(generics).with_convention(g.value.convention)

    def analyse_semantics(
            self, sm: ScopeManager, type_scope: Optional[Scope] = None, generic_infer_source: Optional[dict] = None,
            generic_infer_target: Optional[dict] = None, **kwargs) -> None:

        type_scope = type_scope or sm.current_scope
        original_scope = type_scope

        # Determine the type scope and type symbol.
        type_symbol = AstTypeUtils.get_type_part_symbol_with_error(original_scope, sm, self.without_generics, ignore_alias=True)
        type_scope = type_symbol.scope
        if type_symbol.is_generic: return
        if self.value == "Self": return

        # Name all the generic arguments.
        is_tuple = type_symbol.fq_name.without_generics == CommonTypesPrecompiled.EMPTY_TUP
        AstFunctionUtils.name_generic_arguments(
            self.generic_argument_group.arguments,
            type_symbol.type.generic_parameter_group.parameters,
            sm, self, is_tuple_owner=is_tuple)

        # If there is a directive to skip generic checks, then return.
        if "skip_generic_check" in kwargs:
            return

        # Analyse the semantics of the generic arguments.
        self.generic_argument_group.analyse_semantics(sm, **kwargs)

        # Infer generic arguments from information given from object initialization.
        owner = AstTypeUtils.get_type_part_symbol_with_error(original_scope, sm, self.without_generics).fq_name
        self.generic_argument_group.arguments = AstFunctionUtils.infer_generic_arguments(
            generic_parameters=type_symbol.type.generic_parameter_group.parameters,
            optional_generic_parameters=type_symbol.type.generic_parameter_group.get_optional_params(),
            explicit_generic_arguments=self.generic_argument_group.arguments,
            infer_source=generic_infer_source or {}, infer_target=generic_infer_target or {},
            sm=sm, owner=owner, owner_scope=x.scope if (x := sm.current_scope.get_symbol(owner)) else None,
            owner_ast=self, is_tuple_owner=is_tuple,
            **kwargs)

        # For variant types, collapse any duplicate generic arguments.
        if AstTypeUtils.symbolic_eq(self.without_generics, CommonTypesPrecompiled.EMPTY_VAR, type_scope, sm.current_scope, check_variant=False, lhs_ignore_alias=True):
            composite_types = AstTypeUtils.deduplicate_composite_types(self, sm.current_scope)
            composite_types = CommonTypes.Tup(self.pos, composite_types)
            composite_types.analyse_semantics(sm, type_scope=type_scope, **kwargs)
            self.generic_argument_group.arguments[0].value = composite_types

        # If the generically filled type doesn't exist (Vec[Str]), but the base does (Vec[T]), create it.
        if not type_scope.parent.has_symbol(self):
            external_generics = sm.current_scope.generics_extended_for(self.generic_argument_group.arguments)
            new_scope = AstTypeUtils.create_generic_cls_scope(sm, self, type_symbol, external_generics, is_tuple=is_tuple, **kwargs)

            # Handle type aliasing (providing generics to the original type).
            if type(type_symbol) is AliasSymbol:

                # Substitute the old type: "Opt[Str]" => "Var[Some[Str], None]"
                generics = self.generic_argument_group.arguments + original_scope.generics
                old_type = type_symbol.old_sym.fq_name.substituted_generics(generics)
                old_type.analyse_semantics(sm, type_scope=type_scope.parent, **kwargs)

                # Create a new aliasing symbol for the substituted new type.
                new_alias_symbol = AliasSymbol(
                    name=new_scope.type_symbol.name, type=new_scope.type_symbol.type, scope=new_scope,
                    scope_defined_in=new_scope.type_symbol.scope_defined_in,
                    is_generic=new_scope.type_symbol.is_generic, is_direct_copyable=new_scope.type_symbol.is_copyable(),
                    old_sym=sm.current_scope.get_symbol(old_type))

                new_scope.parent.rem_symbol(new_scope.type_symbol.name)
                new_scope.parent.add_symbol(new_alias_symbol)
                new_scope.type_symbol = new_alias_symbol

            type_symbol = new_scope.type_symbol

        else:
            type_symbol = type_scope.parent.get_symbol(self)

    def infer_type(self, sm: ScopeManager, type_scope: Optional[Scope] = None, **kwargs) -> Asts.TypeAst:
        type_scope  = type_scope or sm.current_scope
        type_symbol = type_scope.get_symbol(self)
        return type_symbol.fq_name


__all__ = [
    "TypeIdentifierAst"]
