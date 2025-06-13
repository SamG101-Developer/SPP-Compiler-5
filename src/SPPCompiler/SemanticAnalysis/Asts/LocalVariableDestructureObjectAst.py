from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstTypeUtils import AstTypeUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors
from SPPCompiler.Utils.Sequence import Seq, SequenceUtils


@dataclass(slots=True)
class LocalVariableDestructureObjectAst(Asts.Ast, Asts.Mixins.VariableLikeAst):
    class_type: Asts.TypeAst = field(default=None)
    tok_l: Asts.TokenAst = field(default=None)
    elems: Seq[Asts.LocalVariableNestedForDestructureObjectAst] = field(default_factory=Seq)
    tok_r: Asts.TokenAst = field(default=None)

    _new_asts: list[Asts.LetStatementAst] = field(default_factory=list, init=False)

    def __post_init__(self) -> None:
        self.tok_l = self.tok_l or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkLeftParenthesis)
        self.tok_r = self.tok_r or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkRightParenthesis)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.class_type.print(printer),
            self.tok_l.print(printer),
            SequenceUtils.print(printer, self.elems, sep=", "),
            self.tok_r.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.tok_r.pos_end

    @property
    def extract_names(self) -> Seq[Asts.IdentifierAst]:
        return SequenceUtils.flatten([e.extract_name for e in self.elems])

    @property
    def extract_name(self) -> Asts.IdentifierAst:
        return Asts.IdentifierAst(self.pos, Asts.Mixins.VariableLikeAst.UNMATCHABLE_VARIABLE)

    def analyse_semantics(self, sm: ScopeManager, value: Asts.ExpressionAst = None, **kwargs) -> None:

        # Analyse the class and determine the attributes of the class.
        self.class_type.analyse_semantics(sm, skip_generic_check=True, **kwargs)
        value_type = value.infer_type(sm, **kwargs)
        if not AstTypeUtils.symbolic_eq(value_type, self.class_type, sm.current_scope, sm.current_scope, check_variant=self._from_pattern):
            raise SemanticErrors.TypeMismatchError().add(value, value_type, self.class_type, self.class_type).scopes(sm.current_scope)
        attributes = sm.current_scope.get_symbol(self.class_type).type.body.members

        # Only 1 "multi-skip" allowed in a destructure.
        multi_arg_skips = [e for e in self.elems if isinstance(e, Asts.LocalVariableDestructureSkipNArgumentsAst)]
        if len(multi_arg_skips) > 1:
            raise SemanticErrors.VariableDestructureContainsMultipleMultiSkipsError().add(
                multi_arg_skips[0], multi_arg_skips[1]).scopes(sm.current_scope)

        # Multi-skip cannot contain a binding for object destructuring.
        if multi_arg_skips and multi_arg_skips[0].binding:
            raise SemanticErrors.VariableObjectDestructureWithBoundMultiSkipError().add(
                self, multi_arg_skips[0]).scopes(sm.current_scope)

        # Create expanded "let" statements for each part of the destructure.
        for element in self.elems:
            if isinstance(element, Asts.LocalVariableDestructureSkipNArgumentsAst):
                continue

            elif isinstance(element, Asts.LocalVariableSingleIdentifierAst):
                postfix = Asts.PostfixExpressionAst(pos=value.pos, lhs=value, op=Asts.PostfixExpressionOperatorMemberAccessAst.new_runtime(element.name.pos, element.name))
                new_ast = Asts.LetStatementInitializedAst(pos=element.pos, assign_to=element, value=postfix)
                new_ast.analyse_semantics(sm, **kwargs)
                self._new_asts.append(new_ast)

            elif isinstance(element, Asts.LocalVariableAttributeBindingAst) and isinstance(element.value, Asts.LocalVariableSingleIdentifierAst):
                continue

            elif isinstance(element, Asts.LocalVariableAttributeBindingAst):
                postfix = Asts.PostfixExpressionAst(pos=value.pos, lhs=value, op=Asts.PostfixExpressionOperatorMemberAccessAst.new_runtime(element.name.pos, element.name))
                new_ast = Asts.LetStatementInitializedAst(pos=element.pos, assign_to=element.value, value=postfix)
                new_ast.analyse_semantics(sm, **kwargs)
                self._new_asts.append(new_ast)

        # Check for any missing attributes in the destructure, unless a multi-skip is present.
        # Todo: connect correct scope for the class type. sm.current_scope.get_symbol(self.class_type).scope.parent_module?
        if not multi_arg_skips:
            assigned_attributes = [e.name for e in self.elems if not isinstance(e, Asts.LocalVariableDestructureSkipNArgumentsAst)]
            missing_attributes = [a for a in attributes if a.name not in assigned_attributes]
            if missing_attributes:
                raise SemanticErrors.ArgumentRequiredNameMissingError().add(
                    self, missing_attributes[0], "attribute", "destructure argument").scopes(sm.current_scope.get_symbol(self.class_type).scope, sm.current_scope)

    def check_memory(self, sm: ScopeManager, **kwargs) -> None:
        for new_ast in self._new_asts:
            new_ast.check_memory(sm, **kwargs)


__all__ = [
    "LocalVariableDestructureObjectAst"]
