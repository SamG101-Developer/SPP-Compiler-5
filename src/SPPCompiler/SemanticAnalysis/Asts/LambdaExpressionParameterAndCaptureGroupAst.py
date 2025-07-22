from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Scoping.Symbols import VariableSymbol
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import AstPrinter, ast_printer_method
from SPPCompiler.Utils.Sequence import SequenceUtils


@dataclass(slots=True, repr=False)
class LambdaExpressionParameterAndCaptureGroupAst(Asts.Ast):
    """
    The LambdaExpressionParameterAndCaptureGroupAst holds the captured variables and parameters for a lambda expression.
    Similar to a standard FunctionParameterGroupAst, but can contain variable identifiers that are always captured into
    the lambda.
    """

    tok_l: Asts.TokenAst = field(default=None)
    """The opening vertical bar token of the lambda expression parameter and capture group."""

    params: list[Asts.LambdaExpressionParameterAst] = field(default_factory=list)
    """The list of parameters in the lambda expression."""

    captures: list[Asts.LambdaExpressionCaptureItemAst] = field(default_factory=list)
    """The list of captured variables in the lambda expression."""

    tok_r: Asts.TokenAst = field(default=None)
    """The closing vertical bar token of the lambda expression parameter and capture group."""

    def __post_init__(self) -> None:
        self.tok_l = self.tok_l or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkVerticalBar)
        self.tok_r = self.tok_r or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkVerticalBar)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        return "".join([
            self.tok_l.print(printer),
            SequenceUtils.print(printer, self.params, sep=", "),
            " caps " if self.captures else "",
            SequenceUtils.print(printer, self.captures, sep=", "),
            self.tok_r.print(printer)])

    @property
    def pos_end(self) -> int:
        return self.tok_r.pos_end if self.tok_r else self.tok_l.pos_end

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # Analyse the parameters in a mock group AST (for uniformity).
        Asts.FunctionParameterGroupAst(params=self.params).analyse_semantics(sm, **kwargs)

        # Add the capture variables after analysis, otherwise their symbol checks refer to the new captures not original
        # asts from the argument group analysis.
        for cap in self.captures:
            # Create a "let" statement to insert the symbol into the current scope.
            var = Asts.LocalVariableSingleIdentifierAst(name=cap.value)
            var_type = cap.value.infer_type(sm, **kwargs)
            ast = Asts.LetStatementInitializedAst(assign_to=var, value=Asts.ObjectInitializerAst(class_type=var_type))
            ast.analyse_semantics(sm, **kwargs)

            # Apply the borrow to the symbol.
            sym: VariableSymbol = sm.current_scope.get_symbol(cap.value)
            sym.memory_info.ast_borrowed = cap.convention
            sym.memory_info.is_borrow_mut = type(cap.convention) is Asts.ConventionMutAst
            sym.memory_info.is_borrow_ref = type(cap.convention) is Asts.ConventionRefAst

            # Apply the borrow to the type.
            sym.type = sym.type.with_convention(cap.convention)


__all__ = [
    "LambdaExpressionParameterAndCaptureGroupAst",
]
