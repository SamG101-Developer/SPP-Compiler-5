from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast, Default
from SPPCompiler.SemanticAnalysis.Meta.AstOrdering import AstOrdering
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.MultiStage.Stage4_SemanticAnalyser import Stage4_SemanticAnalyser
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.GenericArgumentAst import GenericArgumentAst
    from SPPCompiler.SemanticAnalysis.ASTs.GenericArgumentAst import GenericArgumentNamedAst, GenericArgumentUnnamedAst
    from SPPCompiler.SemanticAnalysis.ASTs.GenericArgumentAst import GenericCompArgumentAst, GenericTypeArgumentAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class GenericArgumentGroupAst(Ast, Default, Stage4_SemanticAnalyser):
    tok_left_bracket: TokenAst
    arguments: Seq[GenericArgumentAst]
    tok_right_bracket: TokenAst

    type_arguments: Seq[GenericTypeArgumentAst] = field(default_factory=Seq, init=False, repr=False)
    comp_arguments: Seq[GenericCompArgumentAst] = field(default_factory=Seq, init=False, repr=False)

    def __post_init__(self) -> None:
        # Import the necessary classes to create default instances.
        from SPPCompiler.SemanticAnalysis.ASTs.GenericArgumentAst import GenericTypeArgumentAst, GenericCompArgumentAst

        # Convert the arguments into a sequence, and other defaults.
        self.arguments = Seq(self.arguments)
        self.type_arguments = self.arguments.filter_to_type(*GenericTypeArgumentAst.__value__.__args__)
        self.comp_arguments = self.arguments.filter_to_type(*GenericCompArgumentAst.__value__.__args__)

    def __copy__(self) -> GenericArgumentGroupAst:
        return GenericArgumentGroupAst.default(self.arguments.copy())

    def __eq__(self, other: GenericArgumentGroupAst) -> bool:
        # Check both ASTs are the same type and have the same arguments.
        return isinstance(other, GenericArgumentGroupAst) and self.arguments == other.arguments

    @staticmethod
    def default(arguments: Seq[GenericArgumentAst] = None) -> GenericArgumentGroupAst:
        from SPPCompiler.LexicalAnalysis.TokenType import TokenType
        from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
        return GenericArgumentGroupAst(-1, TokenAst.default(TokenType.TkBrackL), arguments or Seq(), TokenAst.default(TokenType.TkBrackR))

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
        from SPPCompiler.SemanticAnalysis import FunctionCallArgumentNamedAst
        from SPPCompiler.SemanticAnalysis.Meta.AstErrors import AstErrors

        # Check there are no duplicate argument names.
        generic_argument_names = self.arguments.filter_to_type(FunctionCallArgumentNamedAst).map(lambda a: a.name).flat()
        if duplicate_generic_arguments := generic_argument_names.non_unique():
            raise AstErrors.DUPLICATE_IDENTIFIER(duplicate_generic_arguments[0][0], duplicate_generic_arguments[0][1], "named generic arguments")

        # Check the generic arguments are in the correct order.
        if difference := AstOrdering.order_args(self.arguments):
            raise AstErrors.INVALID_ORDER(difference[0], difference[1], "generic argument")

        # Analyse the arguments.
        self.arguments.for_each(lambda arg: arg.analyse_semantics(scope_manager, **kwargs))


__all__ = ["GenericArgumentGroupAst"]
