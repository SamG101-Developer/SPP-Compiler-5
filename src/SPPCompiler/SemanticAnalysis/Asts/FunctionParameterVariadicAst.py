from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter


@dataclass(slots=True, repr=False)
class FunctionParameterVariadicAst(Asts.Ast, Asts.Mixins.OrderableAst, Asts.Mixins.VariableLikeAst):
    tok_variadic: Asts.TokenAst = field(default=None)
    variable: Asts.LocalVariableAst = field(default=None)
    tok_colon: Asts.TokenAst = field(default=None)
    type: Asts.TypeAst = field(default=None)

    def __post_init__(self) -> None:
        self.tok_variadic = self.tok_variadic or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkDoubleDot)
        self.tok_colon = self.tok_colon or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkColon)
        self._variant = "Variadic"

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_variadic.print(printer),
            self.variable.print(printer),
            self.tok_colon.print(printer) + " ",
            self.type.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.type.pos_end

    @property
    def extract_names(self) -> list[Asts.IdentifierAst]:
        return self.variable.extract_names

    @property
    def extract_name(self) -> Asts.IdentifierAst:
        return self.variable.extract_name

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # Analyse the type.
        self.type.analyse_semantics(sm, **kwargs)
        self.type = sm.current_scope.get_symbol(self.type).fq_name.with_convention(self.type.convention)

        # Create the variable for the parameter.
        ast = Asts.LetStatementUninitializedAst(pos=self.variable.pos, assign_to=self.variable, type=self.type)
        ast.analyse_semantics(sm, explicit_type=self.type, **kwargs)

        # Mark the symbol as initialized.
        conv = self.type.convention
        for name in self.variable.extract_names:
            sym = sm.current_scope.get_symbol(name)
            sym.memory_info.initialized_by(self)
            sym.memory_info.ast_borrowed = conv
            sym.memory_info.is_borrow_mut = type(conv) is Asts.ConventionMutAst
            sym.memory_info.is_borrow_ref = type(conv) is Asts.ConventionRefAst

    def check_memory(self, sm: ScopeManager, **kwargs) -> None:
        for name in self.variable.extract_names:
            sym = sm.current_scope.get_symbol(name)
            sym.memory_info.initialized_by(self)


__all__ = [
    "FunctionParameterVariadicAst"]
