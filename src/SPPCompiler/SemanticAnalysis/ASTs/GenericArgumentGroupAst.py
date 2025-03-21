from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Optional


import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstOrdering import AstOrdering
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class GenericArgumentGroupAst(Ast):
    tok_left_bracket: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.TkLeftSquareBracket))
    arguments: Seq[Asts.GenericArgumentAst] = field(default_factory=Seq)
    tok_right_bracket: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.TkRightSquareBracket))

    def __post_init__(self) -> None:
        self.tok_left_bracket.pos = self.tok_left_bracket.pos or self.pos
        self.tok_right_bracket.pos = self.tok_right_bracket.pos or (self.arguments[-1].pos_end if self.arguments else self.pos)

    def __copy__(self) -> GenericArgumentGroupAst:
        return GenericArgumentGroupAst(arguments=self.arguments.copy())

    def __eq__(self, other: GenericArgumentGroupAst) -> bool:
        # Check both ASTs are the same type and have the same arguments.
        return self.arguments == other.arguments

    def __getitem__(self, item: str) -> Optional[Asts.GenericArgumentAst]:
        assert isinstance(item, str)
        return self.arguments.find(lambda a: Asts.IdentifierAst.from_type(a.name).value == item)

    @staticmethod
    def from_parameter_group(parameters: Seq[Asts.GenericParameterAst]) -> GenericArgumentGroupAst:

        GenericArgumentCTor = {
            **{g: Asts.GenericCompArgumentNamedAst for g in Asts.GenericCompParameterAst.__args__},
            **{g: Asts.GenericTypeArgumentNamedAst for g in Asts.GenericTypeParameterAst.__args__}}

        arguments = Seq(parameters).map(lambda p: GenericArgumentCTor[type(p)](name=copy.deepcopy(p.name), value=p.name))
        return GenericArgumentGroupAst(arguments=arguments)

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

    @property
    def pos_end(self) -> int:
        return self.tok_right_bracket.pos_end

    @property
    def type_arguments(self) -> Seq[Asts.GenericTypeArgumentAst]:
        return self.arguments.filter_to_type(*Asts.GenericTypeArgumentAst.__args__)

    @property
    def comp_arguments(self) -> Seq[Asts.GenericCompArgumentAst]:
        return self.arguments.filter_to_type(*Asts.GenericCompArgumentAst.__args__)

    @property
    def named_arguments(self) -> Seq[Asts.GenericArgumentNamedAst]:
        return self.arguments.filter_to_type(*Asts.GenericArgumentNamedAst.__args__)

    @property
    def unnamed_arguments(self) -> Seq[Asts.GenericArgumentUnnamedAst]:
        return self.arguments.filter_to_type(*Asts.GenericArgumentUnnamedAst.__args__)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # Check there are no duplicate argument names.
        generic_argument_names = self.arguments.filter_to_type(*Asts.GenericArgumentNamedAst.__args__).map(lambda a: a.name.name)
        if duplicates := generic_argument_names.non_unique():
            raise SemanticErrors.IdentifierDuplicationError().add(duplicates[0][0], duplicates[0][1], "named generic argument").scopes(scope_manager.current_scope)

        # Check the generic arguments are in the correct order.
        if difference := AstOrdering.order_args(self.arguments):
            raise SemanticErrors.OrderInvalidError().add(difference[0][0], difference[0][1], difference[1][0], difference[1][1], "generic argument").scopes(scope_manager.current_scope)

        # Analyse the arguments.
        for a in self.arguments:
            a.analyse_semantics(scope_manager, **kwargs)


__all__ = ["GenericArgumentGroupAst"]
