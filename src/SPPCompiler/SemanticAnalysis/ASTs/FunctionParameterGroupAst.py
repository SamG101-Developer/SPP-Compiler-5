from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast, Default
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.MultiStage.Stage4_SemanticAnalyser import Stage4_SemanticAnalyser
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.FunctionParameterAst import FunctionParameterAst
    from SPPCompiler.SemanticAnalysis.ASTs.FunctionParameterOptionalAst import FunctionParameterOptionalAst
    from SPPCompiler.SemanticAnalysis.ASTs.FunctionParameterRequiredAst import FunctionParameterRequiredAst
    from SPPCompiler.SemanticAnalysis.ASTs.FunctionParameterSelfAst import FunctionParameterSelfAst
    from SPPCompiler.SemanticAnalysis.ASTs.FunctionParameterVariadicAst import FunctionParameterVariadicAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst


@dataclass
class FunctionParameterGroupAst(Ast, Default, Stage4_SemanticAnalyser):
    tok_left_paren: TokenAst
    parameters: Seq[FunctionParameterAst]
    tok_right_paren: TokenAst

    def __post_init__(self) -> None:
        # Convert the parameters into a sequence.
        self.parameters = Seq(self.parameters)

    def __eq__(self, other: FunctionParameterGroupAst) -> bool:
        # Check both ASTs are the same type and have the same parameters.
        return isinstance(other, FunctionParameterGroupAst) and self.parameters == other.parameters

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_left_paren.print(printer),
            self.parameters.print(printer, ", "),
            self.tok_right_paren.print(printer)]
        return "".join(string)

    @staticmethod
    def default(parameters: Seq[FunctionParameterAst] = None) -> FunctionParameterGroupAst:
        from SPPCompiler.LexicalAnalysis.TokenType import TokenType
        from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
        return FunctionParameterGroupAst(-1, TokenAst.default(TokenType.TkParenL), parameters or Seq(), TokenAst.default(TokenType.TkParenR))

    def get_self(self) -> Optional[FunctionParameterSelfAst]:
        # Get the "self" function parameter (if it exists).
        from SPPCompiler.SemanticAnalysis import FunctionParameterSelfAst
        return self.parameters.filter_to_type(FunctionParameterSelfAst).first(None)

    def get_req(self) -> Seq[FunctionParameterRequiredAst]:
        # Get all the required function parameters.
        from SPPCompiler.SemanticAnalysis import FunctionParameterRequiredAst
        return self.parameters.filter_to_type(FunctionParameterRequiredAst)

    def get_opt(self) -> Seq[FunctionParameterOptionalAst]:
        # Get all the optional function parameters.
        from SPPCompiler.SemanticAnalysis import FunctionParameterOptionalAst
        return self.parameters.filter_to_type(FunctionParameterOptionalAst)

    def get_var(self) -> Optional[FunctionParameterVariadicAst]:
        # Get the variadic function parameter (if it exists).
        from SPPCompiler.SemanticAnalysis import FunctionParameterVariadicAst
        return self.parameters.filter_to_type(FunctionParameterVariadicAst).first(None)

    def get_non_self(self) -> Seq[FunctionParameterAst]:
        # Get all the function parameters that are not "self".
        from SPPCompiler.SemanticAnalysis import FunctionParameterSelfAst
        return self.parameters.filter_not_type(FunctionParameterSelfAst)

    def analyse_semantics(self, scope_handler: ScopeManager, **kwargs) -> None:
        ...


__all__ = ["FunctionParameterGroupAst"]
