from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstBinUtils import AstBinUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors


@dataclass(slots=True)
class IsExpressionAst(Asts.Ast, Asts.Mixins.TypeInferrable):
    lhs: Asts.ExpressionAst = field(default=None)
    op: Asts.TokenAst = field(default=None)
    rhs: Asts.PatternVariantAst = field(default=None)

    _as_func: Optional[Asts.CaseExpressionAst] = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        self.op = self.op or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.KwIs)

    def __hash__(self) -> int:
        return id(self)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.lhs.print(printer) + " ",
            self.op.print(printer) + " ",
            self.rhs.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.rhs.pos_end

    def infer_type(self, sm: ScopeManager, **kwargs) -> Asts.TypeAst:
        """!
        The inferred type is almost always the return type of the converted function equivalent. The exception is for
        "is" expressions, which evaluate to a boolean type.
        """

        # Comparisons using the "is" keyword are always boolean.
        return CommonTypes.Bool(self.pos)

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # The TypeAst cannot be used as an expression for a binary operation. todo: TokenAst check?
        if isinstance(self.lhs, Asts.TypeAst):
            raise SemanticErrors.ExpressionTypeInvalidError().add(self.lhs).scopes(sm.current_scope)
        if isinstance(self.rhs, Asts.TypeAst):
            raise SemanticErrors.ExpressionTypeInvalidError().add(self.rhs).scopes(sm.current_scope)

        # Convert to a "case" destructure and analyse it.
        n = len(sm.current_scope.children)
        self._as_func = AstBinUtils._convert_is_expression_to_function_call(self)
        self._as_func.analyse_semantics(sm, **kwargs)
        destructures_symbols = sm.current_scope.children[n].children[0].all_symbols(exclusive=True, sup_scope_search=True)
        for sym in destructures_symbols:
            sm.current_scope.add_symbol(sym)

    def check_memory(self, sm: ScopeManager, **kwargs) -> None:
        self._as_func.check_memory(sm, **kwargs)


__all__ = [
    "IsExpressionAst"]
