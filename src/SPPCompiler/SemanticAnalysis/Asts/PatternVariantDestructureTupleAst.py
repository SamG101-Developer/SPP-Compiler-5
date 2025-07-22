from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.Utils.Sequence import SequenceUtils


@dataclass(slots=True, repr=False)
class PatternVariantDestructureTupleAst(Asts.Ast, Asts.Mixins.AbstractPatternVariantAst):
    tok_l: Asts.TokenAst = field(default=None)
    elems: list[Asts.PatternVariantNestedForDestructureTupleAst] = field(default_factory=list)
    tok_r: Asts.TokenAst = field(default=None)

    _new_ast: Asts.LetStatementInitializedAst = field(default=None, init=False)

    def __post_init__(self) -> None:
        self.tok_l = self.tok_l or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkLeftParenthesis)
        self.tok_r = self.tok_r or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkRightParenthesis)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_l.print(printer),
            SequenceUtils.print(printer, self.elems, sep=", "),
            self.tok_r.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.tok_r.pos_end

    def convert_to_variable(self, **kwargs) -> Asts.LocalVariableDestructureTupleAst:
        # Convert the tuple destructuring into a local variable tuple destructuring.
        elems = [e.convert_to_variable(**kwargs) for e in self.elems if isinstance(e, Asts.PatternVariantNestedForDestructureTupleAst)]
        variable = Asts.LocalVariableDestructureTupleAst(self.pos, self.tok_l, elems, self.tok_r)
        variable._from_pattern = True
        return variable

    def analyse_semantics(self, sm: ScopeManager, cond: Asts.ExpressionAst = None, **kwargs) -> None:
        # Create the new variables from the pattern in the patterns scope.
        variable = self.convert_to_variable(**kwargs)
        self._new_ast = Asts.LetStatementInitializedAst(pos=variable.pos, assign_to=variable, value=cond)
        self._new_ast.analyse_semantics(sm, **kwargs)

    def check_memory(self, sm: ScopeManager, **kwargs) -> None:
        self._new_ast.check_memory(sm, **kwargs)


__all__ = [
    "PatternVariantDestructureTupleAst"]
