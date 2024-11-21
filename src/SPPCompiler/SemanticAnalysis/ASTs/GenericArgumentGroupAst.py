from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast, Default
from SPPCompiler.SemanticAnalysis.Meta.AstOrdering import AstOrdering
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.GenericArgumentAst import GenericArgumentAst
    from SPPCompiler.SemanticAnalysis.ASTs.GenericArgumentAst import GenericArgumentNamedAst, GenericArgumentUnnamedAst
    from SPPCompiler.SemanticAnalysis.ASTs.GenericArgumentAst import GenericCompArgumentAst, GenericTypeArgumentAst
    from SPPCompiler.SemanticAnalysis.ASTs.GenericParameterAst import GenericParameterAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class GenericArgumentGroupAst(Ast, Default, CompilerStages):
    tok_left_bracket: TokenAst
    arguments: Seq[GenericArgumentAst]
    tok_right_bracket: TokenAst

    def __post_init__(self) -> None:
        # Convert the arguments into a sequence, and other defaults.
        self.arguments = Seq(self.arguments)

    def __copy__(self) -> GenericArgumentGroupAst:
        return GenericArgumentGroupAst.default(self.arguments.copy())

    def __eq__(self, other: GenericArgumentGroupAst) -> bool:
        # Check both ASTs are the same type and have the same arguments.
        return isinstance(other, GenericArgumentGroupAst) and self.arguments == other.arguments

    def __getitem__(self, item: str) -> Optional[GenericArgumentAst]:
        from SPPCompiler.SemanticAnalysis import IdentifierAst
        assert isinstance(item, str)
        return self.arguments.find(lambda a: IdentifierAst.from_type(a.name).value == item)

    @property
    def type_arguments(self) -> Seq[GenericTypeArgumentAst]:
        from SPPCompiler.SemanticAnalysis import GenericTypeArgumentAst
        return self.arguments.filter_to_type(*GenericTypeArgumentAst.__value__.__args__)

    @property
    def comp_arguments(self) -> Seq[GenericCompArgumentAst]:
        from SPPCompiler.SemanticAnalysis import GenericCompArgumentAst
        return self.arguments.filter_to_type(*GenericCompArgumentAst.__value__.__args__)

    @staticmethod
    def default(arguments: Seq[GenericArgumentAst] = None) -> GenericArgumentGroupAst:
        from SPPCompiler.LexicalAnalysis.TokenType import TokenType
        from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
        return GenericArgumentGroupAst(-1, TokenAst.default(TokenType.TkBrackL), arguments or Seq(), TokenAst.default(TokenType.TkBrackR))

    @staticmethod
    def from_parameter_group(parameters: Seq[GenericParameterAst]) -> GenericArgumentGroupAst:
        from SPPCompiler.SemanticAnalysis import GenericCompArgumentNamedAst, GenericCompParameterAst
        from SPPCompiler.SemanticAnalysis import GenericTypeArgumentNamedAst, GenericTypeParameterAst

        GenericArgumentCTor = {
            **{g: GenericCompArgumentNamedAst for g in GenericCompParameterAst.__value__.__args__},
            **{g: GenericTypeArgumentNamedAst for g in GenericTypeParameterAst.__value__.__args__}}

        arguments = Seq(parameters).map(lambda p: GenericArgumentCTor[type(p)].from_name_value(p.name, p.name))
        return GenericArgumentGroupAst.default(arguments)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        if self.arguments:
            string = [
                self.tok_left_bracket.print(printer),
                self.arguments.print(printer, ", "),
                self.tok_right_bracket.print(printer)]
        else:
            string = []
        return "".join(string)

    def get_named(self) -> Seq[GenericArgumentNamedAst]:
        from SPPCompiler.SemanticAnalysis import GenericCompArgumentNamedAst, GenericTypeArgumentNamedAst
        return self.arguments.filter_to_type(GenericCompArgumentNamedAst, GenericTypeArgumentNamedAst)

    def get_unnamed(self) -> Seq[GenericArgumentUnnamedAst]:
        from SPPCompiler.SemanticAnalysis import GenericCompArgumentUnnamedAst, GenericTypeArgumentUnnamedAst
        return self.arguments.filter_to_type(GenericCompArgumentUnnamedAst, GenericTypeArgumentUnnamedAst)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # Code that is run before the overload is selected.
        from SPPCompiler.SemanticAnalysis import GenericArgumentNamedAst
        from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors

        # Check there are no duplicate argument names.
        generic_argument_names = self.arguments.filter_to_type(*GenericArgumentNamedAst.__value__.__args__).map(lambda a: a.name).flat()
        if duplicates := generic_argument_names.non_unique():
            raise SemanticErrors.IdentifierDuplicationError().add(duplicates[0][0], duplicates[0][1], "named generic argument")

        # Check the generic arguments are in the correct order.
        if difference := AstOrdering.order_args(self.arguments):
            raise SemanticErrors.OrderInvalidError().add(difference[0][0], difference[0][1], difference[1][0], difference[1][1], "generic argument")

        # Analyse the arguments.
        self.arguments.for_each(lambda arg: arg.analyse_semantics(scope_manager, **kwargs))


__all__ = ["GenericArgumentGroupAst"]
