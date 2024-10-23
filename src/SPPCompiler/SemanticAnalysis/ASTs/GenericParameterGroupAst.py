from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast, Default
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.GenericParameterAst import GenericParameterAst
    from SPPCompiler.SemanticAnalysis.ASTs.GenericParameterAst import GenericParameterRequiredAst, GenericParameterOptionalAst, GenericParameterVariadicAst
    from SPPCompiler.SemanticAnalysis.ASTs.GenericParameterAst import GenericCompParameterAst, GenericTypeParameterAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst


@dataclass
class GenericParameterGroupAst(Ast, Default):
    tok_left_bracket: TokenAst
    parameters: Seq[GenericParameterAst]
    tok_right_bracket: TokenAst

    type_parameters: Seq[GenericTypeParameterAst] = field(default_factory=Seq, init=False, repr=False)
    comp_parameters: Seq[GenericCompParameterAst] = field(default_factory=Seq, init=False, repr=False)

    def __post_init__(self) -> None:
        # Import the necessary classes to create default instances.
        from SPPCompiler.SemanticAnalysis.ASTs.GenericParameterAst import GenericTypeParameterAst, GenericCompParameterAst

        # Convert the arguments into a sequence, and other defaults.
        self.parameters = Seq(self.parameters)
        self.type_parameters = self.parameters.filter_to_type(*GenericTypeParameterAst.__value__.__args__)
        self.comp_parameters = self.parameters.filter_to_type(*GenericCompParameterAst.__value__.__args__)

    @staticmethod
    def default(parameters: Seq[GenericParameterAst] = None) -> GenericParameterGroupAst:
        from SPPCompiler.LexicalAnalysis.TokenType import TokenType
        from SPPCompiler.SemanticAnalysis import TokenAst
        return GenericParameterGroupAst(-1, TokenAst.default(TokenType.TkBrackL), parameters or Seq(), TokenAst.default(TokenType.TkBrackR))

    def get_req(self) -> Seq[GenericParameterRequiredAst]:
        # Get all the required generic parameters.
        from SPPCompiler.SemanticAnalysis import GenericCompParameterRequiredAst, GenericTypeParameterRequiredAst
        return self.parameters.filter_to_type(GenericCompParameterRequiredAst, GenericTypeParameterRequiredAst)

    def get_opt(self) -> Seq[GenericParameterOptionalAst]:
        # Get all the optional generic parameters.
        from SPPCompiler.SemanticAnalysis import GenericCompParameterOptionalAst, GenericTypeParameterOptionalAst
        return self.parameters.filter_to_type(GenericCompParameterOptionalAst, GenericTypeParameterOptionalAst)

    def get_var(self) -> Seq[GenericParameterVariadicAst]:
        # Get all the variadic generic parameters.
        from SPPCompiler.SemanticAnalysis import GenericCompParameterVariadicAst, GenericTypeParameterVariadicAst
        return self.parameters.filter_to_type(GenericCompParameterVariadicAst, GenericTypeParameterVariadicAst)


__all__ = ["GenericParameterGroupAst"]
