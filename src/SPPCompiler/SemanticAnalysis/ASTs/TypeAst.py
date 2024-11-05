from __future__ import annotations
from convert_case import pascal_case
from dataclasses import dataclass
from typing import Iterator, Optional, TYPE_CHECKING
import hashlib

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable, InferredType
from SPPCompiler.SemanticAnalysis.MultiStage.Stage4_SemanticAnalyser import Stage4_SemanticAnalyser
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.IdentifierAst import IdentifierAst
    from SPPCompiler.SemanticAnalysis.ASTs.GenericArgumentAst import GenericArgumentAst
    from SPPCompiler.SemanticAnalysis.ASTs.GenericIdentifierAst import GenericIdentifierAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.ASTs.TypePartAst import TypePartAst
    from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope


@dataclass
class TypeAst(Ast, TypeInferrable, Stage4_SemanticAnalyser):
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
        from SPPCompiler.SemanticAnalysis import GenericIdentifierAst

        # Return the type without its generic arguments.
        match self.types[-1]:
            case GenericIdentifierAst(): return TypeAst(self.pos, self.namespace, self.types[:-1] + [self.types[-1].without_generics()])
            case _: return TypeAst(self.pos, self.namespace.copy(), self.types.copy())

    def contains_generic(self, generic_name: TypeAst) -> bool:
        from SPPCompiler.SemanticAnalysis import GenericIdentifierAst

        # Check if there is a generic name in this type (at any nested argument level)
        generic_name = GenericIdentifierAst.from_type(generic_name)
        for part in self:
            if part == generic_name: return True
        return False

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
                    type_part.generic_argument_group.arguments.for_each(lambda g: g.value.sub_generics(generic_arguments))

        # Return the modified type.
        return self

    def symbolic_eq(self, that: TypeAst, self_scope: Scope, that_scope: Optional[Scope] = None, check_variant: bool = True) -> bool:
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes

        # Get the symbols for each type, based on the scopes.
        that_scope = that_scope or self_scope
        self_symbol = self_scope.get_symbol(self)
        that_symbol = that_scope.get_symbol(that)

        # Special case for Variant types (can match any of the alternative types).
        # Todo: Tidy this up.
        if check_variant and self_symbol.fq_name.types[-1].generic_argument_group.arguments and self_symbol.fq_name.without_generics().symbolic_eq(CommonTypes.Var(), self_scope, check_variant=False):
            if Seq(self_symbol.name.generic_argument_group.arguments[0].value.types[-1].generic_argument_group.arguments).any(lambda t: t.value.symbolic_eq(that, self_scope, that_scope)):
                return True

        # Compare each type's class prototype.
        return self_symbol.type is that_symbol.type

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredType:
        return InferredType.from_type(self)

    def analyse_semantics(self, scope_manager: ScopeManager, generic_infer_source=None, generic_infer_target=None, **kwargs) -> None:
        from SPPCompiler.SemanticAnalysis import GenericIdentifierAst, TokenAst
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
        from SPPCompiler.SemanticAnalysis.Meta.AstErrors import AstErrors
        from SPPCompiler.SemanticAnalysis.Meta.AstFunctions import AstFunctions
        from SPPCompiler.SemanticAnalysis.Meta.AstTypeManagement import AstTypeManagement
        from SPPCompiler.SemanticAnalysis.Scoping.Symbols import AliasSymbol

        # Determine the scope to use for the type analysis.
        match self.namespace.length:
            case 0: type_scope = scope_manager.current_scope
            case _: type_scope = AstTypeManagement.get_namespaced_scope_with_error(scope_manager, self.namespace)

        # Move through each type, ensuring (at minimum) its non-generic form exists.
        for i, type_part in self.types.enumerate():
            if isinstance(type_part, GenericIdentifierAst):

                # Determine the type scope and type symbol.
                type_symbol = AstTypeManagement.get_type_part_symbol_with_error(type_scope, type_part.without_generics(), ignore_alias=True)
                type_scope = type_symbol.scope
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
                    scope_manager=scope_manager, owner_type=self, **kwargs)

                # Analyse the semantics of the generic arguments.
                type_part.generic_argument_group.analyse_semantics(scope_manager)

                # If the generically filled type doesn't exist (Vec[Str]), but teh base does (Vec[T]), create it.
                if not type_scope.parent.has_symbol(type_part):
                    new_scope = AstTypeManagement.create_generic_scope(scope_manager, self, type_part, type_symbol)

                    # Handle type aliasing (providing generics to the original type).
                    if isinstance(new_scope.type_symbol, AliasSymbol):
                        new_scope.type_symbol.old_type.sub_generics(type_part.generic_argument_group.arguments)
                        new_scope.type_symbol.old_type.analyse_semantics(scope_manager, **kwargs)

            elif isinstance(type_part, TokenAst):
                # Determine the type scope and type symbol.
                prev_type_part = self.types[i - 1]
                type_symbol = AstTypeManagement.get_type_part_symbol_with_error(type_scope, prev_type_part.without_generics(), ignore_alias=True)
                prev_type = TypeAst(-1, self.namespace, self.types[:i])

                # Check the lhs isn't a generic type.
                if type_symbol.is_generic:
                    raise AstErrors.INVALID_PLACE_FOR_GENERIC(prev_type, prev_type, type_part)

                # Check the lhs is a tuple (only indexable type).
                if not prev_type.without_generics().symbolic_eq(CommonTypes.Tup(), scope_manager.current_scope):
                    raise AstErrors.MEMBER_ACCESS_NON_INDEXABLE(prev_type, prev_type, type_part)

                # Check the index is within the bounds of the tuple.
                if int(type_part.token.token_metadata) >= prev_type_part.generic_argument_group.arguments.length:
                    raise AstErrors.MEMBER_ACCESS_OUT_OF_BOUNDS(prev_type, prev_type, type_part)

                new_type = prev_type_part.generic_argument_group.arguments[int(type_part.token.token_metadata)].value
                type_scope = type_scope.get_symbol(new_type).scope

            else:
                raise Exception(f"Invalid type part: {type_part} ({type(type_part)})")

        return type_scope


__all__ = ["TypeAst"]
