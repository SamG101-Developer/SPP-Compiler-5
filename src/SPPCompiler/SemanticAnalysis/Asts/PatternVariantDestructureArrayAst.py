from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class PatternVariantDestructureArrayAst(Asts.Ast, Asts.Mixins.AbstractPatternVariantAst):
    tok_l: Asts.TokenAst = field(default=None)
    elems: Seq[Asts.PatternVariantNestedForDestructureArrayAst] = field(default_factory=Seq)
    tok_r: Asts.TokenAst = field(default=None)

    def __post_init__(self) -> None:
        self.tok_l = self.tok_l or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkLeftParenthesis)
        self.tok_r = self.tok_r or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkRightParenthesis)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_l.print(printer),
            self.elems.print(printer, ", "),
            self.tok_r.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.tok_r.pos_end

    def convert_to_variable(self, **kwargs) -> Asts.LocalVariableDestructureArrayAst:
        # Convert the array destructuring into a local variable array destructuring.
        elems = self.elems.filter_to_type(*Asts.PatternVariantNestedForDestructureArrayAst.__args__)
        converted_elems = elems.map(lambda e: e.convert_to_variable(**kwargs))
        variable = Asts.LocalVariableDestructureArrayAst(self.pos, self.tok_l, converted_elems, self.tok_r)
        variable._from_pattern = True
        return variable

    def analyse_semantics(self, sm: ScopeManager, cond: Asts.ExpressionAst = None, **kwargs) -> None:
        # Create the new variables from the pattern in the patterns scope.
        variable = self.convert_to_variable(**kwargs)
        new_ast = Asts.LetStatementInitializedAst(pos=variable.pos, assign_to=variable, value=cond)
        new_ast.analyse_semantics(sm, **kwargs)


__all__ = [
    "PatternVariantDestructureArrayAst"]
