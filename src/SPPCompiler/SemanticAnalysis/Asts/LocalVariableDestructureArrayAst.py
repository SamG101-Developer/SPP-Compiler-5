from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstTypeUtils import AstTypeUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors
from SPPCompiler.Utils.Sequence import SequenceUtils


@dataclass(slots=True, repr=False)
class LocalVariableDestructureArrayAst(Asts.Ast, Asts.Mixins.VariableLikeAst):
    tok_l: Asts.TokenAst = field(default=None)
    elems: list[Asts.LocalVariableNestedForDestructureArrayAst] = field(default_factory=list)
    tok_r: Asts.TokenAst = field(default=None)

    _new_asts: list[Asts.LetStatementAst] = field(default_factory=list, init=False)

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

    @property
    def extract_names(self) -> list[Asts.IdentifierAst]:
        return SequenceUtils.flatten([e.extract_names for e in self.elems])

    @property
    def extract_name(self) -> Asts.IdentifierAst:
        return Asts.IdentifierAst(self.pos, "_Unmatchable")

    def analyse_semantics(self, sm: ScopeManager, value: Asts.ExpressionAst = None, **kwargs) -> None:

        # Only 1 "multi-skip" allowed in a destructure.
        multi_arg_skips = [e for e in self.elems if type(e) is Asts.LocalVariableDestructureSkipNArgumentsAst]
        if len(multi_arg_skips) > 1:
            raise SemanticErrors.VariableDestructureContainsMultipleMultiSkipsError().add(
                multi_arg_skips[0], multi_arg_skips[1]).scopes(sm.current_scope)

        # Ensure the rhs value is an array.
        value_type = value.infer_type(sm, **kwargs)
        if not AstTypeUtils.is_type_array(value_type, sm.current_scope):
            raise SemanticErrors.VariableArrayDestructureArrayTypeMismatchError().add(
                self, value, value_type).scopes(sm.current_scope)

        # Determine the number of elements in the lhs and rhs arrays.
        num_lhs_array_elements = len(self.elems)
        num_rhs_array_elements = int(value_type.type_parts[0].generic_argument_group.arguments[1].value.value.token_data)

        # Ensure the lhs and rhs arrays have the same number of elements unless a multi-skip is present.
        if (num_lhs_array_elements < num_rhs_array_elements and not multi_arg_skips) or num_lhs_array_elements > num_rhs_array_elements:
            raise SemanticErrors.VariableArrayDestructureArraySizeMismatchError().add(
                self, num_lhs_array_elements, value, num_rhs_array_elements).scopes(sm.current_scope)

        # For a binding ".." destructure, ie "let [a, ..b, c] = t", create an intermediary rhs array.
        if multi_arg_skips and multi_arg_skips[0].binding:
            m = self.elems.index(multi_arg_skips[0])
            indexes = [*range(m, m + num_rhs_array_elements - num_lhs_array_elements + 1)]
            new_ast = Asts.ArrayLiteralNElementAst(
                pos=value.pos,
                elems=[Asts.PostfixExpressionAst(pos=value.pos, lhs=value, op=Asts.PostfixExpressionOperatorMemberAccessAst.new_runtime(value.pos, Asts.TokenAst(0, SppTokenType.LxNumber, str(i)))) for i in indexes])
            bound_multi_skip = new_ast

        # Create new indexes like [0, 1, 2, 6, 7] if elements 3->5 are skipped (and possibly bound).
        indexes  = [*range(0, (self.elems.index(multi_arg_skips[0]) if multi_arg_skips else len(self.elems) - 1) + 1)]
        indexes += [*range(num_lhs_array_elements, num_rhs_array_elements)]

        # Create expanded "let" statements for each part of the destructure.
        for i, element in zip(indexes, self.elems):
            if type(element) is Asts.LocalVariableDestructureSkipNArgumentsAst and multi_arg_skips[0].binding:
                new_ast = Asts.LetStatementInitializedAst(pos=element.pos, assign_to=element.binding, value=bound_multi_skip)
                new_ast.analyse_semantics(sm, **kwargs)
                self._new_asts.append(new_ast)

            elif type(element) is Asts.LocalVariableDestructureSkip1ArgumentAst:
                continue

            elif type(element) is Asts.LocalVariableDestructureSkipNArgumentsAst:
                continue

            else:
                i = Asts.TokenAst(0, SppTokenType.LxNumber, str(i))
                postfix = Asts.PostfixExpressionAst(pos=value.pos, lhs=value, op=Asts.PostfixExpressionOperatorMemberAccessAst.new_runtime(value.pos, i))
                new_ast = Asts.LetStatementInitializedAst(pos=element.pos, assign_to=element, value=postfix)
                new_ast.analyse_semantics(sm, **kwargs)
                self._new_asts.append(new_ast)

    def check_memory(self, sm: ScopeManager, **kwargs) -> None:
        for new_ast in self._new_asts:
            new_ast.check_memory(sm, **kwargs)


__all__ = [
    "LocalVariableDestructureArrayAst"]
