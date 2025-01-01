from __future__ import annotations

import copy

from convert_case import pascal_case
from dataclasses import dataclass
from typing import Iterator, Optional, TYPE_CHECKING, Any
import hashlib

from llvmlite import ir as llvm

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable, InferredType
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.IdentifierAst import IdentifierAst
    from SPPCompiler.SemanticAnalysis.ASTs.GenericArgumentAst import GenericArgumentAst
    from SPPCompiler.SemanticAnalysis.ASTs.GenericIdentifierAst import GenericIdentifierAst
    from SPPCompiler.SemanticAnalysis.ASTs.TypePartAst import TypePartAst
    from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope


@dataclass
class TypeAst(Ast, TypeInferrable, CompilerStages):
    namespace: Seq[IdentifierAst]
    types: Seq[TypePartAst]

    def __post_init__(self) -> None:
        # Convert the namespace and types into a sequence.
        self.namespace = Seq(self.namespace)
        self.types = Seq(self.types)

    def __eq__(self, other: TypeAst) -> bool:
        # Check both ASTs are the same type and have the same namespace and types.
        return isinstance(other, TypeAst) and self.namespace == other.namespace and self.types == other.types

    def __hash__(self) -> int:
        # Hash the namespace and types into a fixed string and convert it into an integer.
        return int.from_bytes(hashlib.md5("".join([str(p) for p in self.namespace + self.types]).encode()).digest())

    def __iter__(self) -> Iterator[TypePartAst]:
        from SPPCompiler.SemanticAnalysis import IdentifierAst, GenericIdentifierAst

        # Iterate over the type parts and generics.
        def internal_iteration(t: TypeAst):
            if isinstance(t, IdentifierAst):
                yield GenericIdentifierAst.from_identifier(t)
            for part in t.types:
                yield part
                for g in part.generic_argument_group.arguments:  # .filter_to_type(*GenericTypeArgumentAst.__value__.__args__):
                    yield from internal_iteration(g.value)
        return internal_iteration(self)

    def __json__(self) -> str:
        return f"cls {self.print(AstPrinter())}"

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.namespace.print(printer, "::") + "::" if self.namespace else "",
            self.types.print(printer, "::")]
        return "".join(string)

    @staticmethod
    def from_identifier(identifier: IdentifierAst) -> TypeAst:
        # Create a TypeAst from an IdentifierAst.
        from SPPCompiler.SemanticAnalysis import GenericIdentifierAst, TypeAst
        return TypeAst(identifier.pos, Seq(), Seq([GenericIdentifierAst.from_identifier(identifier)]))

    @staticmethod
    def from_generic_identifier(identifier: GenericIdentifierAst) -> TypeAst:
        # Create a TypeAst from a GenericIdentifierAst.
        return TypeAst(identifier.pos, Seq(), Seq([identifier]))

    @staticmethod
    def from_function_identifier(identifier: IdentifierAst) -> TypeAst:
        # Create a TypeAst from a function IdentifierAst ($PascalCase mapping too).
        from SPPCompiler.SemanticAnalysis import IdentifierAst
        mock_type_name = IdentifierAst(identifier.pos, f"${pascal_case(identifier.value.replace("_", " "))}")
        return TypeAst.from_identifier(mock_type_name)

    def without_namespace(self) -> TypeAst:
        return TypeAst(self.pos, Seq(), self.types.copy())

    def without_generics(self) -> TypeAst:
        # Return the type without its generic arguments.
        return TypeAst(self.pos, self.namespace, self.types[:-1] + [self.types[-1].without_generics()])

    def contains_generic(self, generic_name: TypeAst) -> bool:
        from SPPCompiler.SemanticAnalysis import GenericIdentifierAst

        # Check if there is a generic name in this type (at any nested argument level)
        generic_name = GenericIdentifierAst.from_type(generic_name)
        for part in self:
            if part == generic_name: return True
        return False

    def get_generic(self, generic_name: TypeAst) -> Optional[TypeAst]:
        # Custom iterator to iterate over the type parts and their generic arguments.
        def custom_iterate(t: TypeAst) -> Iterator[GenericArgumentAst]:
            for p in t.types:
                for g in p.generic_argument_group.type_arguments:
                    yield g
                    yield from custom_iterate(g.value)

        # Check if there is a generic name in this type (at any nested argument level)
        for generic in custom_iterate(self):
            if generic.name == generic_name: return generic.value
        return None

    def get_generic_parameter_for_argument(self, generic_argument: TypeAst) -> Optional[TypeAst]:

        # Custom iterator to iterate over the type parts and their generic arguments.
        def custom_iterate(t: TypeAst) -> Iterator[GenericArgumentAst]:
            for p in t.types:
                for g in p.generic_argument_group.type_arguments:
                    yield g
                    yield from custom_iterate(g.value)

        # Check if there is a generic name in this type (at any nested argument level)
        for generic in custom_iterate(self):
            if generic.value == generic_argument:
                if not hasattr(generic, "name"):
                    return generic_argument
                else:
                    return generic.name
        return None

    def sub_generics(self, generic_arguments: Seq[GenericArgumentAst]) -> TypeAst:
        from SPPCompiler.SemanticAnalysis import GenericIdentifierAst

        # Get all the substitutable parts of this type (GenericIdentifierAst parts)
        type_parts = self.types.filter_to_type(GenericIdentifierAst)

        # Iterate over the generic parameters, and substitute the generic arguments into the type parts.
        for generic_name, generic_type in generic_arguments.map(lambda a: (a.name, a.value)):

            # Direct match => change "T" to "U32" for example. Todo: Does these need to be deep-copied?
            if self.without_generics() == generic_name.without_generics():
                self.namespace = generic_type.namespace.copy()
                self.types = generic_type.types.copy()

            # Otherwise, iterate over the type parts and substitute their generic arguments.
            else:
                for type_part in type_parts:
                    for g in type_part.generic_argument_group.type_arguments:
                        g.value.sub_generics(generic_arguments)

        # Return the modified type.
        return self

    def symbolic_eq(self, that: TypeAst, self_scope: Scope, that_scope: Optional[Scope] = None, check_variant: bool = True) -> bool:
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes

        # Get the symbols for each type, based on the scopes.
        that_scope = that_scope or self_scope
        self_symbol = self_scope.get_symbol(self)
        that_symbol = that_scope.get_symbol(that)

        # Special case for Variant types (can match any of the alternative types).
        # Todo: Tidy this up?
        if check_variant and self_symbol.fq_name.types[-1].generic_argument_group.arguments and self_symbol.fq_name.without_generics().symbolic_eq(CommonTypes.Var(), self_scope, check_variant=False):
            if Seq(self_symbol.name.generic_argument_group.arguments[0].value.types[-1].generic_argument_group.arguments).any(lambda t: t.value.symbolic_eq(that, self_scope, that_scope)):
                return True

        # Compare each type's class prototype.
        return self_symbol.type is that_symbol.type

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredType:
        return InferredType.from_type(self)

    # todo: remove "force" parameter - should be safe?
    def analyse_semantics(self, scope_manager: ScopeManager, generic_infer_source=None, generic_infer_target=None, force: bool = False, **kwargs) -> None:
        from SPPCompiler.SemanticAnalysis.Meta.AstFunctions import AstFunctions
        from SPPCompiler.SemanticAnalysis.Meta.AstTypeManagement import AstTypeManagement
        from SPPCompiler.SemanticAnalysis.Scoping.Symbols import AliasSymbol

        # Determine the scope to use for the type analysis.
        match self.namespace.length:
            case 0: type_scope = scope_manager.current_scope
            case _: type_scope = AstTypeManagement.get_namespaced_scope_with_error(scope_manager, self.namespace)

        # Move through each type, ensuring (at minimum) its non-generic form exists.
        for i, type_part in self.types.enumerate():

            # Determine the type scope and type symbol.
            type_symbol = AstTypeManagement.get_type_part_symbol_with_error(type_scope, type_part.without_generics(), ignore_alias=True)
            type_symbol_alias_bypass = type_scope.get_symbol(type_part.without_generics(), ignore_alias=False)
            type_scope = type_symbol.scope
            type_scope_alias_bypass = type_symbol_alias_bypass.scope
            if type_symbol.is_generic: continue

            # Name all the generic arguments.
            AstFunctions.name_generic_arguments(
                type_part.generic_argument_group.arguments,
                type_symbol.type.generic_parameter_group.parameters,
                self)

            # Infer generic arguments from information given from object initialization.
            type_part.generic_argument_group.arguments = AstFunctions.inherit_generic_arguments(
                generic_parameters=type_symbol.type.generic_parameter_group.get_req(),
                explicit_generic_arguments=type_part.generic_argument_group.arguments,
                infer_source=generic_infer_source or {},
                infer_target=generic_infer_target or {},
                scope_manager=scope_manager, owner=self, **kwargs)

            # Analyse the semantics of the generic arguments.
            type_part.generic_argument_group.analyse_semantics(scope_manager)

            # If the generically filled type doesn't exist (Vec[Str]), but teh base does (Vec[T]), create it.
            if force or not type_scope.parent.has_symbol(type_part):
                new_scope = AstTypeManagement.create_generic_scope(scope_manager, self, type_part, type_symbol)

                # Handle type aliasing (providing generics to the original type).
                if isinstance(new_scope.type_symbol, AliasSymbol):
                    new_scope.type_symbol.old_type = copy.deepcopy(new_scope.type_symbol.old_type)
                    new_scope.type_symbol.old_type.sub_generics(type_part.generic_argument_group.arguments)
                    new_scope.type_symbol.old_type.analyse_semantics(scope_manager, **kwargs)

                type_scope = new_scope

        # Unfortunately this code is required to extend namespaces of generic arguments (for variants especially)
        if all([
                not type_symbol.is_generic,
                not isinstance(type_symbol, AliasSymbol),
                not self.types[-1].value.startswith("$"),
                not self.types[-1].value == "Self"]):
            self.namespace = type_scope_alias_bypass.to_namespace()

    def generate_llvm_definitions(self, scope_handler: ScopeManager, llvm_module: llvm.Module = None, builder: llvm.IRBuilder = None, block: llvm.Block = None, **kwargs) -> Any:
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes

        type_symbol = scope_handler.current_scope.get_symbol(self)
        if self.without_generics().symbolic_eq(CommonTypes.Box().without_generics(), scope_handler.current_scope):
            type_symbol.llvm_info.llvm_type = llvm.PointerType()
        return type_symbol.llvm_info.llvm_type


__all__ = ["TypeAst"]
