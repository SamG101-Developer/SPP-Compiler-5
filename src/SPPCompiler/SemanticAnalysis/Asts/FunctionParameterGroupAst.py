from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstOrderingUtils import AstOrderingUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors
from SPPCompiler.Utils.Sequence import Seq, SequenceUtils


# from llvmlite import ir as llvm


@dataclass(slots=True)
class FunctionParameterGroupAst(Asts.Ast):
    tok_l: Asts.TokenAst = field(default=None)
    params: Seq[Asts.FunctionParameterAst] = field(default_factory=Seq)
    tok_r: Asts.TokenAst = field(default=None)

    def __post_init__(self) -> None:
        self.tok_l = self.tok_l or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkLeftParenthesis)
        self.tok_r = self.tok_r or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkRightParenthesis)

    def __copy__(self) -> FunctionParameterGroupAst:
        return FunctionParameterGroupAst(params=self.params.copy())

    def __eq__(self, other: FunctionParameterGroupAst) -> bool:
        # Check both ASTs are the same type and have the same parameters.
        return isinstance(other, FunctionParameterGroupAst) and self.params == other.params

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_l.print(printer),
            SequenceUtils.print(printer, self.params, sep=", "),
            self.tok_r.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.tok_r.pos_end

    def get_self_param(self) -> Optional[Asts.FunctionParameterSelfAst]:
        # Get the "self" function parameter (if it exists).
        ps = [p for p in self.params if isinstance(p, Asts.FunctionParameterSelfAst)]
        return ps[0] if ps else None

    def get_required_params(self) -> Seq[Asts.FunctionParameterRequiredAst]:
        # Get all the required function parameters.
        ps = [p for p in self.params if isinstance(p, Asts.FunctionParameterRequiredAst)]
        return ps

    def get_optional_params(self) -> Seq[Asts.FunctionParameterOptionalAst]:
        # Get all the optional function parameters.
        ps = [p for p in self.params if isinstance(p, Asts.FunctionParameterOptionalAst)]
        return ps

    def get_variadic_param(self) -> Optional[Asts.FunctionParameterVariadicAst]:
        # Get the variadic function parameter (if it exists).
        ps = [p for p in self.params if isinstance(p, Asts.FunctionParameterVariadicAst)]
        return ps[0] if ps else None

    def get_non_self_params(self) -> Seq[Asts.FunctionParameterAst]:
        # Get all the function parameters that are not "self".
        ps = [p for p in self.params if not isinstance(p, Asts.FunctionParameterSelfAst)]
        return ps

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # Check there is only 1 "self" parameter.
        self_params = [p for p in self.params if isinstance(p, Asts.FunctionParameterSelfAst)]
        if len(self_params) > 1:
            raise SemanticErrors.ParameterMultipleSelfError().add(
                self_params[0], self_params[1]).scopes(sm.current_scope)

        # Check there are no duplicate parameter names.
        param_names = SequenceUtils.flatten([p.extract_names for p in self.params])
        if duplicates := SequenceUtils.duplicates(param_names):
            raise SemanticErrors.IdentifierDuplicationError().add(
                duplicates[0], duplicates[1], "parameter").scopes(sm.current_scope)

        # Check the parameters are in the correct order.
        if dif := AstOrderingUtils.order_params(self.params):
            raise SemanticErrors.OrderInvalidError().add(
                dif[0][0], dif[0][1], dif[1][0], dif[1][1], "parameter").scopes(sm.current_scope)

        # Check there is only 1 variadic parameter.
        variadic_params = [p for p in self.params if isinstance(p, Asts.FunctionParameterVariadicAst)]
        if len(variadic_params) > 1:
            raise SemanticErrors.ParameterMultipleVariadicError().add(
                variadic_params[0], variadic_params[1]).scopes(sm.current_scope)

        # Analyse the parameters.
        for p in self.params:
            p.analyse_semantics(sm, **kwargs)

    # def generate_llvm_definitions(self, sm: ScopeManager, llvm_module: llvm.Module = None, builder: llvm.IRBuilder = None, block: llvm.Block = None, **kwargs) -> Any:
    #     # Get the parameter's llvm types.
    #     parameter_types = self.params.map_attr("type")
    #     llvm_parameter_types = parameter_types.map(lambda t: t.generate_llvm_definitions(sm, llvm_module, **kwargs))
    #     return llvm_parameter_types


__all__ = [
    "FunctionParameterGroupAst"]
