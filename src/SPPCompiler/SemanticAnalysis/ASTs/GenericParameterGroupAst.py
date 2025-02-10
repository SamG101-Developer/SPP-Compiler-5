from __future__ import annotations

from dataclasses import dataclass, field

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstOrdering import AstOrdering
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class GenericParameterGroupAst(Ast):
    tok_left_bracket: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.TkBraceL))
    parameters: Seq[Asts.GenericParameterAst] = field(default_factory=Seq)
    tok_right_bracket: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.TkBraceR))

    def __copy__(self) -> GenericParameterGroupAst:
        return GenericParameterGroupAst(parameters=self.parameters.copy())

    def __eq__(self, other: GenericParameterGroupAst) -> bool:
        # Check both ASTs are the same type and have the same parameters.
        return isinstance(other, GenericParameterGroupAst) and self.parameters == other.parameters

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        if self.parameters:
            string = [
                self.tok_left_bracket.print(printer),
                self.parameters.print(printer, ", "),
                self.tok_right_bracket.print(printer) + " "]
        else:
            string = []
        return "".join(string)

    def get_req(self) -> Seq[Asts.GenericParameterRequiredAst]:
        # Get all the required generic parameters.
        return self.parameters.filter_to_type(Asts.GenericCompParameterRequiredAst, Asts.GenericTypeParameterRequiredAst)

    def get_opt(self) -> Seq[Asts.GenericParameterOptionalAst]:
        # Get all the optional generic parameters.
        return self.parameters.filter_to_type(Asts.GenericCompParameterOptionalAst, Asts.GenericTypeParameterOptionalAst)

    def get_var(self) -> Seq[Asts.GenericParameterVariadicAst]:
        # Get all the variadic generic parameters.
        return self.parameters.filter_to_type(Asts.GenericCompParameterVariadicAst, Asts.GenericTypeParameterVariadicAst)

    def get_comp_params(self) -> Seq[Asts.GenericCompParameterAst]:
        # Get all the computation generic parameters.
        return self.parameters.filter_to_type(*Asts.GenericCompParameterAst.__value__.__args__)

    def get_type_params(self) -> Seq[Asts.GenericTypeParameterAst]:
        # Get all the type generic parameters.
        return self.parameters.filter_to_type(*Asts.GenericTypeParameterAst.__value__.__args__)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # Check there are no duplicate generic parameter names.
        generic_parameter_names = self.parameters.map(lambda parameter: parameter.name)
        if duplicates := generic_parameter_names.non_unique():
            raise SemanticErrors.IdentifierDuplicationError().add(duplicates[0][0], duplicates[0][1], "generic parameter")

        # Check the generic parameters are in the correct order.
        if difference := AstOrdering.order_params(self.parameters):
            raise SemanticErrors.OrderInvalidError().add(difference[0][0], difference[0][1], difference[1][0], difference[1][1], "generic parameter")

        # Analyse the parameters.
        for p in self.parameters:
            p.analyse_semantics(scope_manager, **kwargs)


__all__ = ["GenericParameterGroupAst"]
