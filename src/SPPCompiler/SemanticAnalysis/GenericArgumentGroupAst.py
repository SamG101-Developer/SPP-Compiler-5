from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast, Default
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.GenericArgumentAst import GenericArgumentAst
    from SPPCompiler.SemanticAnalysis.GenericArgumentAst import GenericArgumentNamedAst, GenericArgumentUnnamedAst
    from SPPCompiler.SemanticAnalysis.GenericArgumentAst import GenericCompArgumentAst, GenericTypeArgumentAst
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst


@dataclass
class GenericArgumentGroupAst(Ast, Default):
    tok_left_bracket: TokenAst
    arguments: Seq[GenericArgumentAst]
    tok_right_bracket: TokenAst

    type_arguments: Seq[GenericTypeArgumentAst] = field(default_factory=Seq, init=False, repr=False)
    comp_arguments: Seq[GenericCompArgumentAst] = field(default_factory=Seq, init=False, repr=False)

    def __post_init__(self) -> None:
        self.arguments = Seq(self.arguments)
        self.type_arguments = self.arguments.filter_to_type(*GenericTypeArgumentAst.__value__.__args__)
        self.comp_arguments = self.arguments.filter_to_type(*GenericCompArgumentAst.__value__.__args__)

    @staticmethod
    def default(arguments: Seq[GenericArgumentAst] = None) -> GenericArgumentGroupAst:
        from SPPCompiler.LexicalAnalysis.TokenType import TokenType
        from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst
        return GenericArgumentGroupAst(-1, TokenAst.default(TokenType.TkBrackL), arguments or Seq(), TokenAst.default(TokenType.TkBrackR))

    def get_named(self) -> Seq[GenericArgumentNamedAst]:
        from SPPCompiler.SemanticAnalysis import GenericCompArgumentNamedAst, GenericTypeArgumentNamedAst
        return self.arguments.filter_to_type(GenericCompArgumentNamedAst, GenericTypeArgumentNamedAst)

    def get_unnamed(self) -> Seq[GenericArgumentUnnamedAst]:
        from SPPCompiler.SemanticAnalysis import GenericCompArgumentUnnamedAst, GenericTypeArgumentUnnamedAst
        return self.arguments.filter_to_type(GenericCompArgumentUnnamedAst, GenericTypeArgumentUnnamedAst)

    def __eq__(self, other: GenericArgumentGroupAst) -> bool:
        return isinstance(other, GenericArgumentGroupAst) and self.arguments == other.arguments


__all__ = ["GenericArgumentGroupAst"]
