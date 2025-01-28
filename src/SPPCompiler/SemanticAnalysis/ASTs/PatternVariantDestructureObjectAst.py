from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
import copy, std

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.PatternMapping import PatternMapping
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import InferredType
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages
from SPPCompiler.Utils.Sequence import Seq
import SPPCompiler.SemanticAnalysis as Asts

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.ASTs.LocalVariableDestructureObjectAst import LocalVariableDestructureObjectAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class PatternVariantDestructureObjectAst[T](Ast, PatternMapping, CompilerStages):
    type: Asts.TypeAst = field(default=None)
    tok_left_paren: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.TkParenL))
    elements: Seq[Asts.PatternVariantNestedForDestructureObjectAst] = field(default_factory=Seq)
    tok_right_paren: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.TkParenR))

    def __post_init__(self) -> None:
        assert self.type

    @ast_printer_method
    @std.override_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.type.print(printer),
            self.tok_left_paren.print(printer),
            self.elements.print(printer, ", "),
            self.tok_right_paren.print(printer)]
        return "".join(string)

    @std.override_method
    def convert_to_variable(self, **kwargs) -> LocalVariableDestructureObjectAst:
        # Convert the object destructuring into a local variable object destructuring.
        elements = self.elements.filter_to_type(*Asts.PatternVariantNestedForDestructureObjectAst.__value__.__args__)
        converted_elements = elements.map(lambda e: e.convert_to_variable(**kwargs))
        return LocalVariableDestructureObjectAst(self.pos, self.type, self.tok_left_paren, converted_elements, self.tok_right_paren)

    @std.override_method
    def analyse_semantics(self, scope_manager: ScopeManager, condition: ExpressionAst = None, **kwargs) -> None:
        self.type.analyse_semantics(scope_manager, **kwargs)

        # Flow type the condition symbol if necessary.
        condition_symbol = scope_manager.current_scope.get_symbol(condition)
        is_condition_symbol_variant = condition_symbol and condition_symbol.type.without_generics().symbolic_eq(CommonTypes.Var().without_generics(), scope_manager.current_scope)
        if condition_symbol and is_condition_symbol_variant:
            if not condition_symbol.type.symbolic_eq(self.type, scope_manager.current_scope):
                raise SemanticErrors.TypeMismatchError().add(condition, InferredType.from_type(condition_symbol.type), self.type, InferredType.from_type(self.type))

            flow_symbol = copy.deepcopy(condition_symbol)
            flow_symbol.type = self.type
            scope_manager.current_scope.add_symbol(flow_symbol)

        # Create the new variables from the pattern in the patterns scope.
        variable = self.convert_to_variable(**kwargs)
        new_ast = Asts.LetStatementInitializedAst.from_variable_and_value(variable, condition)
        new_ast.analyse_semantics(scope_manager, **kwargs)


__all__ = ["PatternVariantDestructureObjectAst"]
