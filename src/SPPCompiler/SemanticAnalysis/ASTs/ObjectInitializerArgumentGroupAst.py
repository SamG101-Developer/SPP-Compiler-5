from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.MultiStage.Stage4_SemanticAnalyser import Stage4_SemanticAnalyser
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ObjectInitializerArgumentAst import ObjectInitializerArgumentAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class ObjectInitializerArgumentGroupAst(Ast, Stage4_SemanticAnalyser):
    tok_left_paren: TokenAst
    arguments: Seq[ObjectInitializerArgumentAst]
    tok_right_paren: TokenAst

    def __post_init__(self) -> None:
        # Convert the arguments into a sequence.
        self.arguments = Seq(self.arguments)

    def __copy__(self) -> ObjectInitializerArgumentGroupAst:
        # Create a shallow copy of the AST.
        return ObjectInitializerArgumentGroupAst.default(self.arguments.copy())

    def __eq__(self, other: ObjectInitializerArgumentGroupAst) -> bool:
        # Check both ASTs are the same type and have the same arguments.
        return isinstance(other, ObjectInitializerArgumentGroupAst) and self.arguments == other.arguments

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_left_paren.print(printer),
            self.arguments.print(printer, ", "),
            self.tok_right_paren.print(printer)]
        return "".join(string)

    @staticmethod
    def default(arguments: Seq[ObjectInitializerArgumentAst]) -> ObjectInitializerArgumentGroupAst:
        from SPPCompiler.LexicalAnalysis.TokenType import TokenType
        from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
        return ObjectInitializerArgumentGroupAst(-1, TokenAst.default(TokenType.TkParenL), arguments or Seq(), TokenAst.default(TokenType.TkParenR))

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        self.arguments.for_each(lambda arg: arg.analyse_semantics(scope_manager, **kwargs))


__all__ = ["ObjectInitializerArgumentGroupAst"]
