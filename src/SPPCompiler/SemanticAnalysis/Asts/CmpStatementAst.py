from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Scoping.Symbols import VariableSymbol
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.CompilerStages import PreProcessingContext
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors
from SPPCompiler.Utils.Sequence import Seq, SequenceUtils


@dataclass(slots=True)
class CmpStatementAst(Asts.Ast, Asts.Mixins.VisibilityEnabledAst):
    """
    Unlike the UseStatementAst, this AST can not be used in local scopes; only at the module or superimposition level.
    """

    annotations: Seq[Asts.AnnotationAst] = field(default_factory=Seq)
    kw_cmp: Asts.TokenAst = field(default=None)
    name: Asts.IdentifierAst = field(default=None)
    tok_colon: Asts.TokenAst = field(default=None)
    type: Asts.TypeAst = field(default=None)
    tok_assign: Asts.TokenAst = field(default=None)
    value: Asts.ExpressionAst = field(default=None)

    def __post_init__(self) -> None:
        self.kw_cmp = self.kw_cmp or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.KwCmp)
        self.tok_colon = self.tok_colon or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkColon)
        self.tok_assign = self.tok_assign or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkAssign)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            SequenceUtils.print(printer, self.annotations, sep="\n"),
            self.kw_cmp.print(printer) + " ",
            self.name.print(printer),
            self.tok_colon.print(printer) + " ",
            self.type.print(printer) + " ",
            self.tok_assign.print(printer) + " ",
            self.value.print(printer) + "\n"]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.value.pos_end

    def pre_process(self, context: PreProcessingContext) -> None:
        # Pre-process the annotations.
        for a in self.annotations:
            a.pre_process(self)

    def generate_top_level_scopes(self, sm: ScopeManager) -> None:
        # Run top level scope logic for the annotations.
        for a in self.annotations:
            a.generate_top_level_scopes(sm)

        # Ensure the old type does not have a convention.
        if c := self.type.get_convention():
            raise SemanticErrors.InvalidConventionLocationError().add(
                c, self.type, "global constant type").scopes(sm.current_scope)

        # Create a type symbol for this type in the current scope (class / function).
        symbol = VariableSymbol(name=self.name, type=self.type, visibility=self._visibility[0])
        symbol.memory_info.ast_pinned.append(self.name)
        symbol.memory_info.ast_comptime_const = self
        symbol.memory_info.initialized_by(self)
        sm.current_scope.add_symbol(symbol)

    def load_super_scopes(self, sm: ScopeManager, **kwargs) -> None:
        self.type.analyse_semantics(sm, **kwargs)

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # Analyse the annotations.
        for a in self.annotations:
            a.analyse_semantics(sm, **kwargs)

        # The ".." TokenAst, or TypeAst, cannot be used as an expression for the value.
        if isinstance(self.value, (Asts.TokenAst, Asts.TypeAst)):
            raise SemanticErrors.ExpressionTypeInvalidError().add(self.value).scopes(sm.current_scope)

        # Analyse the type and value.
        self.type.analyse_semantics(sm, **kwargs)
        self.value.analyse_semantics(sm, **kwargs)

        # Check the value's type is the same as the type.
        expected_type = self.type
        given_type = self.value.infer_type(sm, **kwargs)

        if not expected_type.symbolic_eq(given_type, sm.current_scope, sm.current_scope):
            raise SemanticErrors.TypeMismatchError().add(self.type, expected_type, self.value, given_type).scopes(sm.current_scope)

        # Todo: for an identifier, check the identifier itself is a constant value (and copyable)


__all__ = ["CmpStatementAst"]
