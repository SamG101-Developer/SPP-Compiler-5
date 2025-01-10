from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING, Any

from llvmlite import ir as llvm

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast, Default
from SPPCompiler.SemanticAnalysis.Meta.AstOrdering import AstOrdering
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages
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
class FunctionParameterGroupAst(Ast, Default, CompilerStages):
    tok_left_paren: TokenAst
    parameters: Seq[FunctionParameterAst]
    tok_right_paren: TokenAst

    def __post_init__(self) -> None:
        # Convert the parameters into a sequence.
        self.parameters = Seq(self.parameters)

    def __copy__(self) -> FunctionParameterGroupAst:
        return FunctionParameterGroupAst.default(self.parameters.copy())

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
        from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
        from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
        return FunctionParameterGroupAst(-1, TokenAst.default(SppTokenType.TkParenL), parameters or Seq(), TokenAst.default(SppTokenType.TkParenR))

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

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        from SPPCompiler.SemanticAnalysis import FunctionParameterSelfAst, FunctionParameterVariadicAst
        from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors

        # Check there are no duplicate parameter names.
        parameter_names = self.get_non_self().map_attr("extract_names").flat()
        if duplicates := parameter_names.non_unique():
            raise SemanticErrors.IdentifierDuplicationError().add(duplicates[0][0], duplicates[0][1], "parameter")

        # Check the parameters are in the correct order.
        if difference := AstOrdering.order_params(self.parameters):
            raise SemanticErrors.OrderInvalidError().add(difference[0][0], difference[0][1], difference[1][0], difference[1][1], "parameter")

        # Check there is only 1 "self" parameter.
        self_parameters = self.parameters.filter_to_type(FunctionParameterSelfAst)
        if self_parameters.length > 1:
            raise SemanticErrors.ParameterMultipleSelfError().add(self_parameters[0], self_parameters[1])

        # Check there is only 1 variadic parameter.
        variadic_parameters = self.parameters.filter_to_type(FunctionParameterVariadicAst)
        if variadic_parameters.length > 1:
            raise SemanticErrors.ParameterMultipleVariadicError().add(variadic_parameters[0], variadic_parameters[1])

        # Analyse the parameters.
        for p in self.parameters:
            p.analyse_semantics(scope_manager, **kwargs)

    def generate_llvm_definitions(self, scope_handler: ScopeManager, llvm_module: llvm.Module = None, builder: llvm.IRBuilder = None, block: llvm.Block = None, **kwargs) -> Any:
        # Get the parameter's llvm types.
        parameter_types = self.parameters.map_attr("type")
        llvm_parameter_types = parameter_types.map(lambda t: t.generate_llvm_definitions(scope_handler, llvm_module, **kwargs))
        return llvm_parameter_types


__all__ = ["FunctionParameterGroupAst"]
