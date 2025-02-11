from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Any

from llvmlite import ir as llvm

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstOrdering import AstOrdering
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class FunctionParameterGroupAst(Ast):
    tok_left_paren: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.TkParenL))
    parameters: Seq[Asts.FunctionParameterAst] = field(default_factory=Seq)
    tok_right_paren: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.TkParenR))

    def __copy__(self) -> FunctionParameterGroupAst:
        return FunctionParameterGroupAst(parameters=self.parameters.copy())

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

    def get_self(self) -> Optional[Asts.FunctionParameterSelfAst]:
        # Get the "self" function parameter (if it exists).
        from SPPCompiler.SemanticAnalysis import FunctionParameterSelfAst
        return self.parameters.filter_to_type(FunctionParameterSelfAst).first(None)

    def get_req(self) -> Seq[Asts.FunctionParameterRequiredAst]:
        # Get all the required function parameters.
        from SPPCompiler.SemanticAnalysis import FunctionParameterRequiredAst
        return self.parameters.filter_to_type(FunctionParameterRequiredAst)

    def get_opt(self) -> Seq[Asts.FunctionParameterOptionalAst]:
        # Get all the optional function parameters.
        from SPPCompiler.SemanticAnalysis import FunctionParameterOptionalAst
        return self.parameters.filter_to_type(FunctionParameterOptionalAst)

    def get_var(self) -> Optional[Asts.FunctionParameterVariadicAst]:
        # Get the variadic function parameter (if it exists).
        from SPPCompiler.SemanticAnalysis import FunctionParameterVariadicAst
        return self.parameters.filter_to_type(FunctionParameterVariadicAst).first(None)

    def get_non_self(self) -> Seq[Asts.FunctionParameterAst]:
        # Get all the function parameters that are not "self".
        from SPPCompiler.SemanticAnalysis import FunctionParameterSelfAst
        return self.parameters.filter_not_type(FunctionParameterSelfAst)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # Check there are no duplicate parameter names.
        parameter_names = self.get_non_self().map_attr("extract_names").flat()
        if duplicates := parameter_names.non_unique():
            raise SemanticErrors.IdentifierDuplicationError().add(duplicates[0][0], duplicates[0][1], "parameter")

        # Check the parameters are in the correct order.
        if difference := AstOrdering.order_params(self.parameters):
            raise SemanticErrors.OrderInvalidError().add(difference[0][0], difference[0][1], difference[1][0], difference[1][1], "parameter")

        # Check there is only 1 "self" parameter.
        self_parameters = self.parameters.filter_to_type(Asts.FunctionParameterSelfAst)
        if self_parameters.length > 1:
            raise SemanticErrors.ParameterMultipleSelfError().add(self_parameters[0], self_parameters[1])

        # Check there is only 1 variadic parameter.
        variadic_parameters = self.parameters.filter_to_type(Asts.FunctionParameterVariadicAst)
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
