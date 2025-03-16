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
class ArrayLiteralNElementAst(Ast, TypeInferrable):
    """!
    The ArrayLiteralNElementAst class is an AST node that represents an array literal with n elements. The type of the
    element is never given, because every expression in S++ is type-inferrable on declaration. This means that the type
    of the array is inferred from the first element in the array.

    Example:
        let x = [1, 2, 3, 4]

    This will create a std::array::Arr[std::number::U8, 4] type. Arrays in S++ are low-level constructs, and map
    directly to memory. For example, this array will be stored in memory as 4 consecutive bytes. It is analogous to a C
    array[], but as a first-class, safe type.
    """

    tok_left_bracket: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.TkLeftSquareBracket))
    elements: Seq[Asts.ExpressionAst] = field(default_factory=Seq)
    tok_right_bracket: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.TkRightSquareBracket))

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

    @property
    def pos_end(self) -> int:
        return self.tok_right_bracket.pos_end

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> Asts.TypeAst:
        # Create the standard "std::array::Arr[T, n: BigNum]" type, with generic items.
        size = Asts.IntegerLiteralAst.from_python_literal(self.elements.length)
        element_type = self.elements[0].infer_type(scope_manager, **kwargs)
        array_type = CommonTypes.Arr(element_type, size, self.pos)
        array_type.analyse_semantics(scope_manager, **kwargs)
        return array_type

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # Analyse the elements in the array.
        for element in self.elements:
            element.analyse_semantics(scope_manager, **kwargs)
            if isinstance(element, (Asts.TokenAst, Asts.TypeAst)):
                raise SemanticErrors.ExpressionTypeInvalidError().add(element).scopes(scope_manager.current_scope)

        # Check all elements have the same type as the 0th element.
        element_types_and_ast = self.elements.map(lambda e: e.infer_type(scope_manager, **kwargs)).zip(self.elements)
        for element_type, element_ast in element_types_and_ast[1:]:
            if not element_types_and_ast[0][0].symbolic_eq(element_type, scope_manager.current_scope):
                raise SemanticErrors.ArrayElementsDifferentTypesError().add(element_types_and_ast[0][1], element_types_and_ast[0][0], element_ast, element_type).scopes(scope_manager.current_scope)

        # Check all elements are "owned", and not "borrowed".
        for element in self.elements:
            if borrow_symbol := scope_manager.current_scope.get_variable_symbol_outermost_part(element):
                if borrow_ast := borrow_symbol.memory_info.ast_borrowed:
                    raise SemanticErrors.ArrayElementBorrowedError().add(element, borrow_ast).scopes(scope_manager.current_scope)


__all__ = ["ArrayLiteralNElementAst"]
