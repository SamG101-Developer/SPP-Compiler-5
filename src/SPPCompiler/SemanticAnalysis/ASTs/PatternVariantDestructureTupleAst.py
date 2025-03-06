from __future__ import annotations

from dataclasses import dataclass, field

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.PatternMapping import PatternMapping
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class PatternVariantDestructureTupleAst(Ast, PatternMapping):
    tok_left_paren: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.TkLeftParenthesis))
    elements: Seq[Asts.PatternVariantNestedForDestructureTupleAst] = field(default_factory=Seq)
    tok_right_paren: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.TkRightParenthesis))

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_left_paren.print(printer),
            self.elements.print(printer, ", "),
            self.tok_right_paren.print(printer)]
        return "".join(string)

    def convert_to_variable(self, **kwargs) -> Asts.LocalVariableDestructureTupleAst:
        # Convert the tuple destructuring into a local variable tuple destructuring.
        elements = self.elements.filter_to_type(*Asts.PatternVariantNestedForDestructureTupleAst.__args__)
        converted_elements = elements.map(lambda e: e.convert_to_variable(**kwargs))
        return Asts.LocalVariableDestructureTupleAst(self.pos, self.tok_left_paren, converted_elements, self.tok_right_paren)

    def analyse_semantics(self, scope_manager: ScopeManager, condition: Asts.ExpressionAst = None, **kwargs) -> None:
        # Create the new variables from the pattern in the patterns scope.
        variable = self.convert_to_variable(**kwargs)
        new_ast = Asts.LetStatementInitializedAst(pos=variable.pos, assign_to=variable, value=condition)
        new_ast.analyse_semantics(scope_manager, **kwargs)


__all__ = ["PatternVariantDestructureTupleAst"]
