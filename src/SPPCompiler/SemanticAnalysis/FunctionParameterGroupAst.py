from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast, Default
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.FunctionParameterAst import FunctionParameterAst
    from SPPCompiler.SemanticAnalysis.FunctionParameterOptionalAst import FunctionParameterOptionalAst
    from SPPCompiler.SemanticAnalysis.FunctionParameterRequiredAst import FunctionParameterRequiredAst
    from SPPCompiler.SemanticAnalysis.FunctionParameterSelfAst import FunctionParameterSelfAst
    from SPPCompiler.SemanticAnalysis.FunctionParameterVariadicAst import FunctionParameterVariadicAst
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst


@dataclass
class FunctionParameterGroupAst(Ast, Default):
    tok_left_paren: TokenAst
    parameters: Seq[FunctionParameterAst]
    tok_right_paren: TokenAst

    def __post_init__(self) -> None:
        self.parameters = Seq(self.parameters)

    @staticmethod
    def default(parameters: Seq[FunctionParameterAst] = None) -> FunctionParameterGroupAst:
        from SPPCompiler.LexicalAnalysis.TokenType import TokenType
        from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst
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

    def __eq__(self, other: FunctionParameterGroupAst) -> bool:
        return isinstance(other, FunctionParameterGroupAst) and self.parameters == other.parameters


__all__ = ["FunctionParameterGroupAst"]
