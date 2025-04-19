from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Optional

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstOrderingUtils import AstOrderingUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class GenericArgumentGroupAst(Asts.Ast):
    tok_l: Asts.TokenAst = field(default=None)
    arguments: Seq[Asts.GenericArgumentAst] = field(default_factory=Seq)
    tok_r: Asts.TokenAst = field(default=None)

    def __post_init__(self) -> None:
        self.tok_l = self.tok_l or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkLeftSquareBracket)
        self.tok_r = self.tok_r or Asts.TokenAst.raw(pos=self.arguments[-1].pos_end if self.arguments else self.pos, token_type=SppTokenType.TkRightSquareBracket)

    def __copy__(self) -> GenericArgumentGroupAst:
        return GenericArgumentGroupAst(arguments=self.arguments.copy())

    def __eq__(self, other: GenericArgumentGroupAst) -> bool:
        # Check both ASTs are the same type and have the same arguments.
        return self.arguments == other.arguments

    def __getitem__(self, item: str) -> Optional[Asts.GenericArgumentAst]:
        assert isinstance(item, str), type(item)
        return self.arguments.find(lambda a: Asts.IdentifierAst.from_type(a.name).value == item)

    @staticmethod
    def from_parameter_group(parameters: Seq[Asts.GenericParameterAst], use_default: bool = False) -> GenericArgumentGroupAst:

        GenericArgumentCTor = {
            **{g: Asts.GenericCompArgumentNamedAst for g in Asts.GenericCompParameterAst.__args__},
            **{g: Asts.GenericTypeArgumentNamedAst for g in Asts.GenericTypeParameterAst.__args__}}

        if not use_default:
            arguments = Seq(parameters).map(lambda p: GenericArgumentCTor[type(p)](name=copy.deepcopy(p.name), value=p.name))
        else:
            arguments = Seq(parameters).map(lambda p: GenericArgumentCTor[type(p)](name=copy.deepcopy(p.name), value=p.default if isinstance(p, Asts.GenericParameterOptionalAst) else p.name))

        return GenericArgumentGroupAst(arguments=arguments)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        if self.arguments:
            string = [
                self.tok_l.print(printer),
                self.arguments.print(printer, ", "),
                self.tok_r.print(printer)]
        else:
            string = []
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.tok_r.pos_end

    def get_type_args(self) -> Seq[Asts.GenericTypeArgumentAst]:
        return self.arguments.filter_to_type(*Asts.GenericTypeArgumentAst.__args__)

    def get_comp_args(self) -> Seq[Asts.GenericCompArgumentAst]:
        return self.arguments.filter_to_type(*Asts.GenericCompArgumentAst.__args__)

    def get_named_args(self) -> Seq[Asts.GenericArgumentNamedAst]:
        return self.arguments.filter_to_type(*Asts.GenericArgumentNamedAst.__args__)

    def get_unnamed_args(self) -> Seq[Asts.GenericArgumentUnnamedAst]:
        return self.arguments.filter_to_type(*Asts.GenericArgumentUnnamedAst.__args__)

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # Check there are no duplicate argument names.
        generic_argument_names = self.arguments.filter_to_type(*Asts.GenericArgumentNamedAst.__args__).map(lambda a: a.name.name)
        if duplicates := generic_argument_names.non_unique():
            raise SemanticErrors.IdentifierDuplicationError().add(
                duplicates[0][0], duplicates[0][1], "named generic argument").scopes(sm.current_scope)

        # Check the generic arguments are in the correct order.
        if dif := AstOrderingUtils.order_args(self.arguments):
            raise SemanticErrors.OrderInvalidError().add(
                dif[0][0], dif[0][1], dif[1][0], dif[1][1], "generic argument").scopes(sm.current_scope)

        # Analyse the arguments.
        for a in self.arguments:
            a.analyse_semantics(sm, **kwargs)


__all__ = [
    "GenericArgumentGroupAst"]
