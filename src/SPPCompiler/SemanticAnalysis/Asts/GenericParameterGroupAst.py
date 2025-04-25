from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstOrderingUtils import AstOrderingUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors
from SPPCompiler.Utils.FastDeepcopy import fast_deepcopy
from SPPCompiler.Utils.Sequence import Seq


@dataclass(slots=True)
class GenericParameterGroupAst(Asts.Ast):
    tok_l: Asts.TokenAst = field(default=None)
    parameters: Seq[Asts.GenericParameterAst] = field(default_factory=Seq)
    tok_r: Asts.TokenAst = field(default=None)

    def __post_init__(self) -> None:
        self.tok_l = self.tok_l or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkLeftSquareBracket)
        self.tok_r = self.tok_r or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkRightSquareBracket)

    def __copy__(self) -> GenericParameterGroupAst:
        return GenericParameterGroupAst(parameters=self.parameters.copy())

    def __deepcopy__(self, memodict=None) -> GenericParameterGroupAst:
        return GenericParameterGroupAst(parameters=fast_deepcopy(self.parameters))

    def __eq__(self, other: GenericParameterGroupAst) -> bool:
        # Check both ASTs are the same type and have the same parameters.
        return isinstance(other, GenericParameterGroupAst) and self.parameters == other.parameters

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        if self.parameters:
            string = [
                self.tok_l.print(printer),
                self.parameters.print(printer, ", "),
                self.tok_r.print(printer) + " "]
        else:
            string = []
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.tok_r.pos_end

    def get_required_params(self) -> Seq[Asts.GenericParameterRequiredAst]:
        # Get all the required generic parameters.
        return self.parameters.filter_to_type(Asts.GenericCompParameterRequiredAst, Asts.GenericTypeParameterRequiredAst)

    def get_optional_params(self) -> Seq[Asts.GenericParameterOptionalAst]:
        # Get all the optional generic parameters.
        return self.parameters.filter_to_type(Asts.GenericCompParameterOptionalAst, Asts.GenericTypeParameterOptionalAst)

    def get_variadic_params(self) -> Seq[Asts.GenericParameterVariadicAst]:
        # Get all the variadic generic parameters.
        return self.parameters.filter_to_type(Asts.GenericCompParameterVariadicAst, Asts.GenericTypeParameterVariadicAst)

    def get_comp_params(self) -> Seq[Asts.GenericCompParameterAst]:
        # Get all the computation generic parameters.
        return self.parameters.filter_to_type(*Asts.GenericCompParameterAst.__args__)

    def get_type_params(self) -> Seq[Asts.GenericTypeParameterAst]:
        # Get all the type generic parameters.
        return self.parameters.filter_to_type(*Asts.GenericTypeParameterAst.__args__)

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # Check there are no duplicate generic parameter names.
        generic_parameter_names = self.parameters.map(lambda parameter: parameter.name)
        if duplicates := generic_parameter_names.non_unique():
            raise SemanticErrors.IdentifierDuplicationError().add(duplicates[0][0], duplicates[0][1], "generic parameter")

        # Check the generic parameters are in the correct order.
        if difference := AstOrderingUtils.order_params(self.parameters):
            raise SemanticErrors.OrderInvalidError().add(difference[0][0], difference[0][1], difference[1][0], difference[1][1], "generic parameter")

        # Analyse the parameters.
        for p in self.parameters:
            p.analyse_semantics(sm, **kwargs)


__all__ = [
    "GenericParameterGroupAst"]
