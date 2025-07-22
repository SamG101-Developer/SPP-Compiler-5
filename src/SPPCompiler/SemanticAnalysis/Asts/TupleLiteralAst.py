from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors
from SPPCompiler.Utils.Sequence import SequenceUtils


@dataclass(slots=True, repr=False)
class TupleLiteralAst(Asts.Ast, Asts.Mixins.TypeInferrable):
    tok_l: Asts.TokenAst = field(default=None)
    elems: list[Asts.ExpressionAst] = field(default_factory=list)
    tok_r: Asts.TokenAst = field(default=None)

    def __post_init__(self) -> None:
        self.tok_l = self.tok_l or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkLeftParenthesis)
        self.tok_r = self.tok_r or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkRightParenthesis)

    def __eq__(self, other: TupleLiteralAst) -> bool:
        return self.elems == other.elems

    def __hash__(self) -> int:
        return id(self)

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

    def infer_type(self, sm: ScopeManager, **kwargs) -> Asts.TypeAst:
        # Create the standard "std::tuple::Tup[..Items]" type, with generic items.
        inner_types = [e.infer_type(sm, **kwargs) for e in self.elems]
        tuple_type = CommonTypes.Tup(self.pos, inner_types)
        tuple_type.analyse_semantics(sm, **kwargs)
        return tuple_type

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # Analyse the elements in the tuple.
        for element in self.elems:
            element.analyse_semantics(sm, **kwargs)
            if isinstance(element, (Asts.TokenAst, Asts.TypeAst)):
                raise SemanticErrors.ExpressionTypeInvalidError().add(
                    element).scopes(sm.current_scope)

        # Check all elements are "owned", and not "borrowed".
        for element in self.elems:
            if borrow_symbol := sm.current_scope.get_variable_symbol_outermost_part(element):
                if borrow_ast := borrow_symbol.memory_info.ast_borrowed:
                    raise SemanticErrors.TupleElementBorrowedError().add(
                        element, borrow_ast).scopes(sm.current_scope)

        # Analyse the inferred tuple type to generate the generic implementation.
        self.infer_type(sm, **kwargs).analyse_semantics(sm, **kwargs)


__all__ = [
    "TupleLiteralAst"]
