from __future__ import annotations

from dataclasses import dataclass, field

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable, InferredTypeInfo
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class ArrayLiteralNElementAst(Ast, TypeInferrable):
    tok_left_bracket: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.TkBrackL))
    elements: Seq[Asts.ExpressionAst] = field(default_factory=Seq)
    tok_right_bracket: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.TkBrackR))

    def __eq__(self, other: ArrayLiteralNElementAst) -> bool:
        # Check both ASTs are the same type and have the same elements.
        return isinstance(other, ArrayLiteralNElementAst) and self.elements == other.elements

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_left_bracket.print(printer),
            self.elements.print(printer, ", "),
            self.tok_right_bracket.print(printer)]
        return "".join(string)

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredTypeInfo:
        # Create the standard "std::Arr[T, n: BigNum]" type, with generic items.
        size = Asts.IntegerLiteralAst.from_python_literal(self.elements.length)
        element_type = self.elements[0].infer_type(scope_manager, **kwargs).type
        array_type = CommonTypes.Arr(element_type, size, self.pos)
        array_type.analyse_semantics(scope_manager, **kwargs)
        return InferredTypeInfo(array_type)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # Analyse the elements in the array.
        for element in self.elements:
            element.analyse_semantics(scope_manager, **kwargs)
            if isinstance(element, (Asts.TokenAst, Asts.TypeAst)):
                raise SemanticErrors.ExpressionTypeInvalidError().add(element)

        # Check all elements have the same type as the 0th element.
        element_types = self.elements.map(lambda e: e.infer_type(scope_manager, **kwargs))
        for element_type in element_types[1:]:
            if not element_types[0].symbolic_eq(element_type, scope_manager.current_scope):
                raise SemanticErrors.ArrayElementsDifferentTypesError().add(element_types[0], element_type)

        # Check all elements are "owned", and not "borrowed".
        borrowed_elements = self.elements.filter(lambda e: e.infer_type(scope_manager, **kwargs).convention is not Asts.ConventionMovAst)
        if borrowed_elements:
            if borrow_symbol := scope_manager.current_scope.get_variable_symbol_outermost_part(borrowed_elements[0]):
                if borrow_ast := borrow_symbol.memory_info.ast_borrowed:
                    raise SemanticErrors.ArrayElementBorrowedError().add(borrowed_elements[0], borrow_ast)


__all__ = ["ArrayLiteralNElementAst"]
