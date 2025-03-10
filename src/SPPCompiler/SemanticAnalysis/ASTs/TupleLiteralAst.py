from __future__ import annotations

from dataclasses import dataclass, field

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class TupleLiteralAst(Ast, TypeInferrable):
    tok_left_paren: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.TkLeftParenthesis))
    elements: Seq[Asts.ExpressionAst] = field(default_factory=Seq)
    tok_right_paren: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.TkRightParenthesis))

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_left_paren.print(printer),
            self.elements.print(printer, ", "),
            self.tok_right_paren.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.tok_right_paren.pos_end

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> Asts.TypeAst:
        # Create the standard "std::Tup[..Items]" type, with generic items.
        inner_types = self.elements.map(lambda element: element.infer_type(scope_manager, **kwargs))
        tuple_type = CommonTypes.Tup(inner_types, self.pos)
        tuple_type.analyse_semantics(scope_manager, **kwargs)
        return tuple_type

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # Analyse the elements in the tuple.
        for element in self.elements:
            element.analyse_semantics(scope_manager, **kwargs)
            if isinstance(element, (Asts.TokenAst, Asts.TypeAst)):
                raise SemanticErrors.ExpressionTypeInvalidError().add(element).scopes(scope_manager.current_scope)

        # Check all elements are "owned", and not "borrowed".
        for element in self.elements:
            if borrow_symbol := scope_manager.current_scope.get_variable_symbol_outermost_part(element):
                if borrow_ast := borrow_symbol.memory_info.ast_borrowed:
                    raise SemanticErrors.TupleElementBorrowedError().add(element, borrow_ast).scopes(scope_manager.current_scope)


__all__ = ["TupleLiteralAst"]
