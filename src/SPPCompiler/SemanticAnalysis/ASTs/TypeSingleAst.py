from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Optional, Self, Dict, Tuple

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Meta.AstFunctions import AstFunctions
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import AstPrinter, ast_printer_method
from SPPCompiler.SemanticAnalysis.Meta.AstTypeManagement import AstTypeManagement
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable, InferredTypeInfo
from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Scoping.Symbols import AliasSymbol
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class TypeSingleAst(Asts.TypeAbstractAst, TypeInferrable):
    name: Asts.GenericIdentifierAst = field(default_factory=lambda: Asts.GenericIdentifierAst())

    def __eq__(self, other: TypeSingleAst) -> bool:
        if isinstance(other, Asts.TypeSingleAst):
            return self.name == other.name
        elif isinstance(other, Asts.IdentifierAst):
            return self.name.value == other.value
        return False

    def __hash__(self) -> int:
        return hash(self.name)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        return f"{self.name}"

    @staticmethod
    def from_identifier(ast: Asts.IdentifierAst) -> TypeSingleAst:
        return TypeSingleAst(pos=ast.pos, name=Asts.GenericIdentifierAst.from_identifier(ast))

    @staticmethod
    def from_generic_identifier(ast: Asts.GenericIdentifierAst) -> TypeSingleAst:
        return TypeSingleAst(pos=ast.pos, name=ast)

    def fq_type_parts(self) -> Seq[Asts.IdentifierAst | Asts.GenericIdentifierAst | Asts.TokenAst]:
        return Seq([self.name])

    def type_parts(self) -> Seq[Asts.GenericIdentifierAst]:
        return Seq([self.name])

    def without_generics(self) -> Self:
        return TypeSingleAst(self.pos, self.name.without_generics())

    def sub_generics(self, generic_arguments: Seq[Asts.GenericArgumentAst]) -> Self:
        name = copy.deepcopy(self.name)
        for generic_name, generic_type in generic_arguments.map(lambda a: (a.name, a.value)):
            if self == generic_name:
                return generic_type

            for g in name.generic_argument_group.type_arguments:  # comp args?
                g.value = g.value.sub_generics(generic_arguments)

        return TypeSingleAst(self.pos, name)

    def get_generic(self, generic_name: Asts.TypeSingleAst) -> Optional[Asts.TypeAst]:
        for g in self.name.generic_argument_group.named_arguments:
            if g.name == generic_name:
                return g.value
        return None

    def contains_generic(self, generic_name: Asts.TypeSingleAst) -> bool:
        for g in self.name.generic_argument_group.arguments:
            if g.value == generic_name:
                return True
        return False

    def symbolic_eq(self, that: Asts.TypeAst, self_scope: Scope, that_scope: Optional[Scope] = None, check_variant: bool = True) -> bool:
        that_scope = that_scope or self_scope
        that_scope, that = that.split_to_scope_and_type(that_scope)

        # Get the symbols of the types.
        self_symbol = self_scope.get_symbol(self.name)
        that_symbol = that_scope.get_symbol(that.name)

        # Variant type: one of the generic arguments must match the type.
        if check_variant and self_symbol.fq_name.type_parts()[0].generic_argument_group.arguments and self_symbol.fq_name.without_generics().symbolic_eq(CommonTypes.Var(), self_scope, that_scope, check_variant=False):
            composite_types = self_symbol.name.generic_argument_group.arguments[0].value.type_parts()[0].generic_argument_group.arguments
            if composite_types.any(lambda t: t.value.symbolic_eq(that, self_scope, that_scope)):
                return True

        # # Intersections type: all the generic arguments must be superimposed over the type.
        # if self_symbol.fq_name.without_generics().symbolic_eq(CommonTypes.Isc(), self_scope):
        #     composite_types = self_symbol.name.generic_argument_group.arguments[0].value.type_parts()[0].generic_argument_group.arguments
        #     superimposed_types = self_symbol.scope.sup_scopes.filter(lambda s: isinstance(s._ast, Asts.ClassPrototypeAst)).map(lambda sc: sc.type_symbol.fq_name)
        #     if not composite_types.all(lambda t: superimposed_types.any(lambda s: t.value.symbolic_eq(s, self_scope, that_scope))):
        #         return False

        # Otherwise check the symbols are equal.
        return self_symbol.type is that_symbol.type

    def analyse_semantics(self, scope_manager: ScopeManager, type_scope: Optional[Scope] = None, generic_infer_source: Optional[Dict] = None, generic_infer_target: Optional[Dict] = None, **kwargs) -> None:
        type_scope = type_scope or scope_manager.current_scope

        # Determine the type scope and type symbol.
        type_symbol = AstTypeManagement.get_type_part_symbol_with_error(type_scope, self.name.without_generics(), ignore_alias=True)
        type_symbol_2 = type_scope.get_symbol(self.name.without_generics(), ignore_alias=False)
        type_scope = type_symbol.scope
        if type_symbol.is_generic: return

        # Name all the generic arguments.
        AstFunctions.name_generic_arguments(
            self.name.generic_argument_group.arguments,
            type_symbol.type.generic_parameter_group.parameters,
            type_symbol_2.fq_name)

        # Infer generic arguments from information given from object initialization.
        self.name.generic_argument_group.arguments = AstFunctions.inherit_generic_arguments(
            generic_parameters=type_symbol.type.generic_parameter_group.get_req(),
            explicit_generic_arguments=self.name.generic_argument_group.arguments,
            infer_source=generic_infer_source or {},
            infer_target=generic_infer_target or {},
            scope_manager=scope_manager, owner=self, **kwargs)

        # Analyse the semantics of the generic arguments.
        self.name.generic_argument_group.analyse_semantics(scope_manager)

        # If the generically filled type doesn't exist (Vec[Str]), but the base does (Vec[T]), create it.
        if not type_scope.parent.has_symbol(self.name):
            new_scope = AstTypeManagement.create_generic_scope(scope_manager, type_symbol_2.fq_name, self.name, type_symbol)

            # Handle type aliasing (providing generics to the original type).
            if isinstance(new_scope.type_symbol, AliasSymbol):
                new_scope.type_symbol.old_type = copy.deepcopy(new_scope.type_symbol.old_type)
                new_scope.type_symbol.old_type = new_scope.type_symbol.old_type.sub_generics(self.name.generic_argument_group.arguments)
                new_scope.type_symbol.old_type.analyse_semantics(scope_manager, **kwargs)

    def infer_type(self, scope_manager: ScopeManager, type_scope: Optional[Scope] = None, **kwargs) -> InferredTypeInfo:
        type_scope = type_scope or scope_manager.current_scope
        type_symbol = type_scope.get_symbol(self.name, ignore_alias=False)
        return InferredTypeInfo(type_symbol.fq_name)

    def split_to_scope_and_type(self, scope: Scope) -> Tuple[Scope, Asts.TypeSingleAst]:
        return scope, self


__all__ = ["TypeSingleAst"]
