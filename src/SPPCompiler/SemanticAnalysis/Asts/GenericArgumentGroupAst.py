from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstOrderingUtils import AstOrderingUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors
from SPPCompiler.Utils.FastDeepcopy import fast_deepcopy
from SPPCompiler.Utils.Sequence import SequenceUtils


@dataclass(slots=True, repr=False)
class GenericArgumentGroupAst(Asts.Ast):
    tok_l: Asts.TokenAst = field(default=None)
    arguments: list[Asts.GenericArgumentAst] = field(default_factory=list)
    tok_r: Asts.TokenAst = field(default=None)

    def __post_init__(self) -> None:
        self.tok_l = self.tok_l or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkLeftSquareBracket)
        self.tok_r = self.tok_r or Asts.TokenAst.raw(pos=self.arguments[-1].pos_end if self.arguments else self.pos, token_type=SppTokenType.TkRightSquareBracket)

    def __copy__(self) -> GenericArgumentGroupAst:
        return GenericArgumentGroupAst(arguments=self.arguments.copy())

    def __deepcopy__(self, memodict=None) -> GenericArgumentGroupAst:
        return GenericArgumentGroupAst(tok_l=self.tok_l, arguments=fast_deepcopy(self.arguments), tok_r=self.tok_r)

    def __eq__(self, other: GenericArgumentGroupAst) -> bool:
        return self.arguments == other.arguments

    def __hash__(self) -> int:
        return id(self)

    def __getitem__(self, item: str) -> Optional[Asts.GenericArgumentAst]:
        # assert isinstance(item, str), type(item)
        args = [a for a in self.arguments if Asts.IdentifierAst.from_type(a.name).value == item]
        return args[0] if args else None

    def __str__(self) -> str:
        if self.arguments:
            string = [
                str(self.tok_l),
                ", ".join([str(a) for a in self.arguments]),
                str(self.tok_r)]
            return "".join(string)
        return ""

    @staticmethod
    def from_parameter_group(param_group: Asts.GenericParameterGroupAst) -> GenericArgumentGroupAst:

        GenericArgumentCTor = {
            **{g: Asts.GenericCompArgumentNamedAst for g in Asts.GenericCompParameterAst.__args__},
            **{g: Asts.GenericTypeArgumentNamedAst for g in Asts.GenericTypeParameterAst.__args__}}

        val = lambda p: p.name if isinstance(p, Asts.GenericTypeParameterAst) else Asts.IdentifierAst.from_type(p.name)

        arguments = [GenericArgumentCTor[type(p)](name=p.name, value=val(p)) for p in param_group.parameters]
        return GenericArgumentGroupAst(arguments=arguments)

    @staticmethod
    def from_dict(dictionary: dict[Asts.TypeAst, Asts.ExpressionAst | Asts.TypeAst]) -> GenericArgumentGroupAst:
        args = []
        for arg_name, arg_val in dictionary.items():
            if isinstance(arg_val, Asts.TypeAst):
                args.append(Asts.GenericTypeArgumentNamedAst(name=arg_name, value=arg_val))
            else:
                args.append(Asts.GenericCompArgumentNamedAst(name=arg_name, value=arg_val))
        return GenericArgumentGroupAst(arguments=args)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        if self.arguments:
            string = [
                self.tok_l.print(printer),
                SequenceUtils.print(printer, self.arguments, sep=", "),
                self.tok_r.print(printer)]
            return "".join(string)
        return ""

    @property
    def pos_end(self) -> int:
        return self.tok_r.pos_end if self.arguments else self.tok_l.pos_end

    def get_type_args(self) -> list[Asts.GenericTypeArgumentAst]:
        return [a for a in self.arguments if isinstance(a, Asts.GenericTypeArgumentAst)]

    def get_comp_args(self) -> list[Asts.GenericCompArgumentAst]:
        return [a for a in self.arguments if isinstance(a, Asts.GenericCompArgumentAst)]

    def get_named_args(self) -> list[Asts.GenericArgumentNamedAst]:
        return [a for a in self.arguments if isinstance(a, Asts.GenericArgumentNamedAst)]

    def get_unnamed_args(self) -> list[Asts.GenericArgumentUnnamedAst]:
        return [a for a in self.arguments if isinstance(a, Asts.GenericArgumentUnnamedAst)]

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        """
        The analysis for a group of generic arguments requires checking there are no duplicate argument names, and that
        the named arguments follow the unnamed arguments. Following this, each argument's value is analysed.

        :param sm: The scope manager.
        :param kwargs: Additional keyword arguments.
        """

        # Check there are no duplicate argument names.
        generic_argument_names = [a.name for a in self.get_named_args()]
        if duplicates := SequenceUtils.duplicates(generic_argument_names):
            raise SemanticErrors.IdentifierDuplicationError().add(
                duplicates[0], duplicates[0], "named generic argument").scopes(sm.current_scope)

        # Check the generic arguments are in the correct order.
        if dif := AstOrderingUtils.order_args(self.arguments):
            raise SemanticErrors.OrderInvalidError().add(
                dif[0][0], dif[0][1], dif[1][0], dif[1][1], "generic argument").scopes(sm.current_scope)

        # Analyse the arguments.
        for a in self.arguments:
            a.analyse_semantics(sm, **kwargs)

    def check_memory(self, sm: ScopeManager, **kwargs) -> None:
        """
        Check the memory of the generic arguments. This is done by checking the memory of each argument. This is only
        needed for the comp generic args, as they use actual values, not types.

        :param sm: The scope manager.
        :param kwargs: Additional keyword arguments.
        """

        for a in self.arguments:
            a.check_memory(sm, **kwargs)


__all__ = [
    "GenericArgumentGroupAst"]
