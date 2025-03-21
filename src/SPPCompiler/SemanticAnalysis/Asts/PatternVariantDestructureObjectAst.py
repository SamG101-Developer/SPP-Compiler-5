from __future__ import annotations

import copy
from dataclasses import dataclass, field

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypes, CommonTypesPrecompiled
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class PatternVariantDestructureObjectAst(Asts.Ast, Asts.Mixins.AbstractPatternVariantAst):
    class_type: Asts.TypeAst = field(default=None)
    tok_l: Asts.TokenAst = field(default=None)
    elems: Seq[Asts.PatternVariantNestedForDestructureObjectAst] = field(default_factory=Seq)
    tok_r: Asts.TokenAst = field(default=None)

    def __post_init__(self) -> None:
        self.tok_l = self.tok_l or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkLeftParenthesis)
        self.tok_r = self.tok_r or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkRightParenthesis)
        assert self.class_type is not None

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.class_type.print(printer),
            self.tok_l.print(printer),
            self.elems.print(printer, ", "),
            self.tok_r.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.tok_r.pos_end

    def convert_to_variable(self, **kwargs) -> Asts.LocalVariableDestructureObjectAst:
        # Convert the object destructuring into a local variable object destructuring.
        elems = self.elems.filter_to_type(*Asts.PatternVariantNestedForDestructureObjectAst.__args__)
        converted_elems = elems.map(lambda e: e.convert_to_variable(**kwargs))
        return Asts.LocalVariableDestructureObjectAst(self.pos, self.class_type, self.tok_l, converted_elems, self.tok_r)

    def analyse_semantics(self, sm: ScopeManager, cond: Asts.ExpressionAst = None, **kwargs) -> None:
        self.class_type.analyse_semantics(sm, **kwargs)

        # Flow type the condition symbol if necessary.
        condition_symbol = sm.current_scope.get_symbol(cond)
        is_condition_symbol_variant = condition_symbol and condition_symbol.type.without_generics().symbolic_eq(CommonTypesPrecompiled.EMPTY_VARIANT, sm.current_scope)
        if condition_symbol and is_condition_symbol_variant:
            if not condition_symbol.type.symbolic_eq(self.class_type, sm.current_scope, sm.current_scope):
                raise SemanticErrors.TypeMismatchError().add(cond, condition_symbol.type, self.class_type, self.class_type).scopes(sm.current_scope)

            flow_symbol = copy.deepcopy(condition_symbol)
            flow_symbol.type = self.class_type
            sm.current_scope.add_symbol(flow_symbol)

        # Create the new variables from the pattern in the patterns scope.
        variable = self.convert_to_variable(**kwargs)
        new_ast = Asts.LetStatementInitializedAst(pos=variable.pos, assign_to=variable, value=cond)
        new_ast.analyse_semantics(sm, **kwargs)


__all__ = [
    "PatternVariantDestructureObjectAst"]
