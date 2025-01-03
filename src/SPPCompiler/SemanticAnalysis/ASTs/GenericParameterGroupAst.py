from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast, Default
from SPPCompiler.SemanticAnalysis.Meta.AstOrdering import AstOrdering
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.GenericParameterAst import GenericParameterAst
    from SPPCompiler.SemanticAnalysis.ASTs.GenericParameterAst import GenericParameterRequiredAst, GenericParameterOptionalAst, GenericParameterVariadicAst
    from SPPCompiler.SemanticAnalysis.ASTs.GenericParameterAst import GenericCompParameterAst, GenericTypeParameterAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class GenericParameterGroupAst(Ast, Default, CompilerStages):
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

    def __copy__(self) -> GenericParameterGroupAst:
        return GenericParameterGroupAst.default(self.parameters.copy())

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

    def get_type_params(self) -> Seq[GenericTypeParameterAst]:
        # Get all the type generic parameters.
        from SPPCompiler.SemanticAnalysis.ASTs.GenericParameterAst import GenericTypeParameterAst
        return self.parameters.filter_to_type(*GenericTypeParameterAst.__value__.__args__)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors

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
