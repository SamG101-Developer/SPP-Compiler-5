from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.PatternMapping import PatternMapping
from SPPCompiler.SemanticAnalysis.MultiStage.Stage4_SemanticAnalyser import Stage4_SemanticAnalyser
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.ASTs.PatternVariantAst import PatternVariantNestedForDestructureObjectAst
    from SPPCompiler.SemanticAnalysis.ASTs.LocalVariableDestructureObjectAst import LocalVariableDestructureObjectAst
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class PatternVariantDestructureObjectAst(Ast, PatternMapping,Stage4_SemanticAnalyser):
    type: TypeAst
    tok_left_paren: TokenAst
    elements: Seq[PatternVariantNestedForDestructureObjectAst]
    tok_right_paren: TokenAst

    def __post_init__(self) -> None:
        # Convert the elements into a sequence.
        self.elements = Seq(self.elements)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.type.print(printer),
            self.tok_left_paren.print(printer),
            self.elements.print(printer, ", "),
            self.tok_right_paren.print(printer)]
        return "".join(string)

    def convert_to_variable(self, **kwargs) -> LocalVariableDestructureObjectAst:
        # Convert the object destructuring into a local variable object destructuring.
        from SPPCompiler.SemanticAnalysis import LocalVariableDestructureObjectAst
        elements = self.elements.filter_to_type(*PatternVariantNestedForDestructureObjectAst.__value__.__args__)
        converted_elements = elements.map(lambda e: e.convert_to_variable(**kwargs))
        return LocalVariableDestructureObjectAst(self.pos, self.type, self.tok_left_paren, converted_elements, self.tok_right_paren)

    def analyse_semantics(self, scope_manager: ScopeManager, condition: ExpressionAst = None, **kwargs) -> None:
        # Todo: flow typing with the symbol
        from SPPCompiler.SemanticAnalysis import LetStatementInitializedAst

        # Create the new variables from the pattern in the patterns scope.
        variable = self.convert_to_variable(**kwargs)
        new_ast = LetStatementInitializedAst.from_variable_and_value(variable, condition)
        new_ast.analyse_semantics(scope_manager, **kwargs)


__all__ = ["PatternVariantDestructureObjectAst"]
