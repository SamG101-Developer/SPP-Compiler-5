from __future__ import annotations
from typing import Callable, List, Optional, Tuple, TYPE_CHECKING
import functools

from SParLex.Lexer.Tokens import SpecialToken
from SParLex.Parser.Parser import Parser
from SParLex.Parser.ParserRuleHandler import ParserRuleHandler

from SPPCompiler.LexicalAnalysis.Token import Token
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.Utils.Sequence import Seq
import SPPCompiler.SemanticAnalysis as Asts

if TYPE_CHECKING:
    from SParLex.Parser.ParserError import ParserErrors
    from SParLex.Utils.ErrorFormatter import ErrorFormatter


# Todo: add newlines after multi-expression/statement blocks (ie between multiple ret/gen/let etc)
# Todo: revert multi-skip back to simpler 1 function implementation (matches variadic parameter)
# Todo: change else= inside object initializer to ".."


# Decorator that wraps the function in a ParserRuleHandler
def parser_rule[T](func: Callable[..., T]) -> Callable[..., ParserRuleHandler]:
    @functools.wraps(func)
    def wrapper(self, *args) -> ParserRuleHandler[T]:
        return ParserRuleHandler(self, functools.partial(func, self, *args))
    return wrapper


class SppParser(Parser):
    _tokens: List[Token]
    _name: str
    _index: int
    _err_fmt: ErrorFormatter
    _error: Optional[ParserErrors.SyntaxError]

    def __init__(self, tokens: List[Token], file_name: str = "", error_formatter: Optional[ErrorFormatter] = None) -> None:
        super().__init__(SppTokenType, tokens, file_name, error_formatter)

        from SParLex.Parser.ParserError import ParserErrors
        from SParLex.Utils.ErrorFormatter import ErrorFormatter

        self._tokens = tokens
        self._name = file_name
        self._index = 0
        self._err_fmt = error_formatter or ErrorFormatter(SppTokenType, self._tokens, file_name)
        self._error = ParserErrors.SyntaxError()

    def current_pos(self) -> int:
        return self._index

    def current_tok(self) -> Token:
        return self._tokens[self._index]

    # ===== PROGRAM =====

    @parser_rule
    def parse_root(self) -> Asts.ModulePrototypeAst:
        p1 = self.parse_module_prototype().parse_once()
        return p1

    # ===== MODULES =====

    @parser_rule
    def parse_module_prototype(self) -> Asts.ModulePrototypeAst:
        c1 = self.current_pos()
        p1 = self.parse_module_implementation().parse_once()
        return Asts.ModulePrototypeAst(c1, p1)

    @parser_rule
    def parse_module_implementation(self) -> Asts.ModuleImplementationAst:
        c1 = self.current_pos()
        p1 = self.parse_module_member().parse_zero_or_more(SpecialToken.NO_TOK)
        return Asts.ModuleImplementationAst(c1, Seq(p1))

    @parser_rule
    def parse_module_member(self) -> Asts.ModuleMemberAst:
        p1 = self.parse_function_prototype()
        p2 = self.parse_class_prototype()
        p3 = self.parse_sup_prototype_extension()
        p4 = self.parse_sup_prototype_functions()
        p5 = self.parse_global_use_statement()
        p6 = self.parse_global_constant()
        p7 = (p1 | p2 | p3 | p4 | p5 | p6).parse_once()
        return p7

    # ===== CLASSES =====

    @parser_rule
    def parse_class_prototype(self) -> Asts.ClassPrototypeAst:
        c1 = self.current_pos()
        p1 = self.parse_annotation().parse_zero_or_more(SppTokenType.TkNewLine)
        p2 = self.parse_token(SppTokenType.KwCls).parse_once()
        p3 = self.parse_upper_identifier().parse_once()
        p4 = self.parse_generic_parameters().parse_optional() or Asts.GenericParameterGroupAst(pos=c1)
        p5 = self.parse_where_block().parse_optional() or Asts.WhereBlockAst(pos=c1)
        p6 = self.parse_class_implementation().parse_once()
        return Asts.ClassPrototypeAst(c1, Seq(p1), p2, Asts.TypeAst.from_identifier(p3), p4, p5, p6)

    @parser_rule
    def parse_class_implementation(self) -> Asts.ClassImplementationAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.TkBraceL).parse_once()
        p2 = self.parse_class_member().parse_zero_or_more(SpecialToken.NO_TOK)
        p3 = self.parse_token(SppTokenType.TkBraceR).parse_once()
        return Asts.ClassImplementationAst(c1, p1, Seq(p2), p3)

    @parser_rule
    def parse_class_member(self) -> Asts.ClassMemberAst:
        p1 = self.parse_class_attribute().parse_once()
        return p1

    @parser_rule
    def parse_class_attribute(self) -> Asts.ClassAttributeAst:
        c1 = self.current_pos()
        p1 = self.parse_annotation().parse_zero_or_more(SppTokenType.TkNewLine)
        p2 = self.parse_identifier().parse_once()
        p3 = self.parse_token(SppTokenType.TkColon).parse_once()
        p4 = self.parse_type().parse_once()
        return Asts.ClassAttributeAst(c1, Seq(p1), p2, p3, p4)

    # ===== SUPERIMPOSITION =====

    @parser_rule
    def parse_sup_prototype_functions(self) -> Asts.SupPrototypeFunctionsAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.KwSup).parse_once()
        p2 = self.parse_generic_parameters().parse_optional() or Asts.GenericParameterGroupAst(pos=c1)
        p3 = self.parse_type().parse_once()
        p4 = self.parse_where_block().parse_optional() or Asts.WhereBlockAst(pos=c1)
        p5 = self.parse_sup_implementation().parse_once()
        return Asts.SupPrototypeFunctionsAst(c1, p1, p2, p3, p4, p5)

    @parser_rule
    def parse_sup_prototype_extension(self) -> Asts.SupPrototypeExtensionAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.KwSup).parse_once()
        p2 = self.parse_generic_parameters().parse_optional() or Asts.GenericParameterGroupAst(pos=c1)
        p3 = self.parse_type().parse_once()
        p4 = self.parse_token(SppTokenType.KwExt).parse_once()
        p5 = self.parse_type().parse_once()
        p6 = self.parse_where_block().parse_optional() or Asts.WhereBlockAst(pos=c1)
        p7 = self.parse_sup_implementation().parse_once()
        return Asts.SupPrototypeExtensionAst(c1, p1, p2, p3, p6, p7, p4, p5)

    @parser_rule
    def parse_sup_implementation(self) -> Asts.SupImplementationAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.TkBraceL).parse_once()
        p2 = self.parse_sup_member().parse_zero_or_more(SpecialToken.NO_TOK)
        p3 = self.parse_token(SppTokenType.TkBraceR).parse_once()
        return Asts.SupImplementationAst(c1, p1, Seq(p2), p3)

    @parser_rule
    def parse_sup_member(self) -> Asts.SupMemberAst:
        p1 = self.parse_sup_method_prototype()
        p2 = self.parse_sup_use_statement()
        p3 = (p1 | p2).parse_once()
        return p3

    @parser_rule
    def parse_sup_method_prototype(self) -> Asts.FunctionPrototypeAst:
        p1 = self.parse_function_prototype().parse_once()
        return p1

    @parser_rule
    def parse_sup_use_statement(self) -> Asts.SupUseStatementAst:
        p1 = self.parse_annotation().parse_zero_or_more(SppTokenType.TkNewLine)
        p2 = self.parse_use_statement().parse_once()
        return Asts.UseStatementAst(**p2.__dict__, annotations=Seq(p1))

    # ===== FUNCTIONS =====

    @parser_rule
    def parse_function_prototype(self) -> Asts.FunctionPrototypeAst:
        p1 = self.parse_subroutine_prototype()
        p2 = self.parse_coroutine_prototype()
        p3 = (p1 | p2).parse_once()
        return p3

    @parser_rule
    def parse_subroutine_prototype(self) -> Asts.SubroutinePrototypeAst:
        c1 = self.current_pos()
        p1 = self.parse_annotation().parse_zero_or_more(SppTokenType.TkNewLine)
        p2 = self.parse_token(SppTokenType.KwFun).parse_once()
        p3 = self.parse_identifier().parse_once()
        p4 = self.parse_generic_parameters().parse_optional() or Asts.GenericParameterGroupAst(pos=c1)
        p5 = self.parse_function_parameters().parse_once()
        p6 = self.parse_token(SppTokenType.TkArrowR).parse_once()
        p7 = self.parse_type().parse_once()
        p8 = self.parse_where_block().parse_optional() or Asts.WhereBlockAst(pos=c1)
        p9 = self.parse_function_implementation().parse_once()
        return Asts.SubroutinePrototypeAst(c1, Seq(p1), p2, p3, p4, p5, p6, p7, p8, p9)

    @parser_rule
    def parse_coroutine_prototype(self) -> Asts.CoroutinePrototypeAst:
        c1 = self.current_pos()
        p1 = self.parse_annotation().parse_zero_or_more(SppTokenType.TkNewLine)
        p2 = self.parse_token(SppTokenType.KwCor).parse_once()
        p3 = self.parse_identifier().parse_once()
        p4 = self.parse_generic_parameters().parse_optional() or Asts.GenericParameterGroupAst(pos=c1)
        p5 = self.parse_function_parameters().parse_once()
        p6 = self.parse_token(SppTokenType.TkArrowR).parse_once()
        p7 = self.parse_type().parse_once()
        p8 = self.parse_where_block().parse_optional() or Asts.WhereBlockAst(pos=c1)
        p9 = self.parse_function_implementation().parse_once()
        return Asts.CoroutinePrototypeAst(c1, Seq(p1), p2, p3, p4, p5, p6, p7, p8, p9)

    @parser_rule
    def parse_function_implementation(self) -> Asts.FunctionImplementationAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.TkBraceL).parse_once()
        p2 = self.parse_function_member().parse_zero_or_more(SpecialToken.NO_TOK)
        p3 = self.parse_token(SppTokenType.TkBraceR).parse_once()
        return Asts.FunctionImplementationAst(c1, p1, Seq(p2), p3)

    @parser_rule
    def parse_function_member(self) -> Asts.FunctionMemberAst:
        p1 = self.parse_statement().parse_once()
        return p1

    @parser_rule
    def parse_function_call_arguments(self) -> Asts.FunctionCallArgumentGroupAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.TkParenL).parse_once()
        p2 = self.parse_function_call_argument().parse_zero_or_more(SppTokenType.TkComma)
        p4 = self.parse_token(SppTokenType.TkParenR).parse_once()
        return Asts.FunctionCallArgumentGroupAst(c1, p1, Seq(p2), p4)

    @parser_rule
    def parse_function_call_argument(self) -> Asts.FunctionCallArgumentAst:
        p1 = self.parse_function_call_argument_named()
        p2 = self.parse_function_call_argument_unnamed()
        p3 = (p1 | p2).parse_once()
        return p3

    @parser_rule
    def parse_function_call_argument_unnamed(self) -> Asts.FunctionCallArgumentUnnamedAst:
        c1 = self.current_pos()
        p1 = self.parse_convention().parse_once()
        p2 = self.parse_token(SppTokenType.TkDblDot).parse_optional()
        p3 = self.parse_expression().parse_once()
        return Asts.FunctionCallArgumentUnnamedAst(c1, p1, p2, p3)

    @parser_rule
    def parse_function_call_argument_named(self) -> Asts.FunctionCallArgumentNamedAst:
        c1 = self.current_pos()
        p1 = self.parse_identifier().parse_once()
        p2 = self.parse_token(SppTokenType.TkAssign).parse_once()
        p3 = self.parse_convention().parse_once()
        p4 = self.parse_expression().parse_once()
        return Asts.FunctionCallArgumentNamedAst(c1, p1, p2, p3, p4)

    @parser_rule
    def parse_function_parameters(self) -> Asts.FunctionParameterGroupAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.TkParenL).parse_once()
        p2 = self.parse_function_parameter().parse_zero_or_more(SppTokenType.TkComma)
        p3 = self.parse_token(SppTokenType.TkParenR).parse_once()
        return Asts.FunctionParameterGroupAst(c1, p1, Seq(p2), p3)

    @parser_rule
    def parse_function_parameter(self) -> Asts.FunctionParameterAst:
        p1 = self.parse_function_parameter_variadic()
        p2 = self.parse_function_parameter_optional()
        p3 = self.parse_function_parameter_required()
        p4 = self.parse_function_parameter_self()
        p5 = (p1 | p2 | p3 | p4).parse_once()
        return p5

    @parser_rule
    def parse_function_parameter_self(self) -> Asts.FunctionParameterSelfAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.KwMut).parse_optional()
        p2 = self.parse_convention().parse_once()
        p3 = self.parse_self_keyword().parse_once()
        return Asts.FunctionParameterSelfAst(c1, p1, p2, p3)

    @parser_rule
    def parse_function_parameter_required(self) -> Asts.FunctionParameterRequiredAst:
        c1 = self.current_pos()
        p1 = self.parse_local_variable().parse_once()
        p2 = self.parse_token(SppTokenType.TkColon).parse_once()
        p3 = self.parse_convention().parse_once()
        p4 = self.parse_type().parse_once()
        return Asts.FunctionParameterRequiredAst(c1, p1, p2, p3, p4)

    @parser_rule
    def parse_function_parameter_optional(self) -> Asts.FunctionParameterOptionalAst:
        c1 = self.current_pos()
        p1 = self.parse_local_variable().parse_once()
        p2 = self.parse_token(SppTokenType.TkColon).parse_once()
        p3 = self.parse_convention().parse_once()
        p4 = self.parse_type().parse_once()
        p5 = self.parse_token(SppTokenType.TkAssign).parse_once()
        p6 = self.parse_expression().parse_once()
        return Asts.FunctionParameterOptionalAst(c1, p1, p2, p3, p4, p5, p6)

    @parser_rule
    def parse_function_parameter_variadic(self) -> Asts.FunctionParameterVariadicAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.TkDblDot).parse_once()
        p2 = self.parse_local_variable().parse_once()
        p3 = self.parse_token(SppTokenType.TkColon).parse_once()
        p4 = self.parse_convention().parse_once()
        p5 = self.parse_type().parse_once()
        return Asts.FunctionParameterVariadicAst(c1, p1, p2, p3, p4, p5)

    # ===== GENERICS =====

    @parser_rule
    def parse_generic_arguments(self) -> Asts.GenericArgumentGroupAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.TkBrackL).parse_once()
        p2 = self.parse_generic_argument().parse_one_or_more(SppTokenType.TkComma)
        p3 = self.parse_token(SppTokenType.TkBrackR).parse_once()
        return Asts.GenericArgumentGroupAst(c1, p1, Seq(p2), p3)

    @parser_rule
    def parse_generic_argument(self) -> Asts.GenericArgumentAst:
        p1 = self.parse_generic_type_argument_named()
        p2 = self.parse_generic_type_argument_unnamed()
        p3 = self.parse_generic_comp_argument_named()
        p4 = self.parse_generic_comp_argument_unnamed()
        p5 = (p1 | p2 | p3 | p4).parse_once()
        return p5

    @parser_rule
    def parse_generic_type_argument_named(self) -> Asts.GenericTypeArgumentNamedAst:
        c1 = self.current_pos()
        p1 = self.parse_upper_identifier().parse_once()
        p2 = self.parse_token(SppTokenType.TkAssign).parse_once()
        p3 = self.parse_type().parse_once()
        return Asts.GenericTypeArgumentNamedAst(c1, Asts.TypeAst.from_identifier(p1), p2, p3)

    @parser_rule
    def parse_generic_type_argument_unnamed(self) -> Asts.GenericTypeArgumentUnnamedAst:
        c1 = self.current_pos()
        p1 = self.parse_type().parse_once()
        return Asts.GenericTypeArgumentUnnamedAst(c1, p1)

    @parser_rule
    def parse_generic_comp_argument_named(self) -> Asts.GenericCompArgumentNamedAst:
        c1 = self.current_pos()
        p1 = self.parse_identifier().parse_once()
        p2 = self.parse_token(SppTokenType.TkAssign).parse_once()
        p3 = self.parse_global_constant_value().parse_once()
        return Asts.GenericCompArgumentNamedAst(c1, Asts.TypeAst.from_identifier(p1), p2, p3)

    @parser_rule
    def parse_generic_comp_argument_unnamed(self) -> Asts.GenericCompArgumentUnnamedAst:
        c1 = self.current_pos()
        p1 = self.parse_global_constant_value().parse_once()
        return Asts.GenericCompArgumentUnnamedAst(c1, p1)

    @parser_rule
    def parse_generic_parameters(self) -> Asts.GenericParameterGroupAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.TkBrackL).parse_once()
        p2 = self.parse_generic_parameter().parse_one_or_more(SppTokenType.TkComma)
        p3 = self.parse_token(SppTokenType.TkBrackR).parse_once()
        return Asts.GenericParameterGroupAst(c1, p1, Seq(p2), p3)

    @parser_rule
    def parse_generic_parameter(self) -> Asts.GenericParameterAst:
        p1 = self.parse_generic_comp_parameter_variadic()
        p2 = self.parse_generic_comp_parameter_optional()
        p3 = self.parse_generic_comp_parameter_required()
        p4 = self.parse_generic_type_parameter_variadic()
        p5 = self.parse_generic_type_parameter_optional()
        p6 = self.parse_generic_type_parameter_required()
        p7 = (p1 | p2 | p3 | p4 | p5 | p6).parse_once()
        return p7

    @parser_rule
    def parse_generic_type_parameter_required(self) -> Asts.GenericTypeParameterRequiredAst:
        c1 = self.current_pos()
        p1 = self.parse_upper_identifier().parse_once()
        p2 = self.parse_generic_inline_constraints().parse_optional() or Asts.GenericTypeParameterInlineConstraintsAst(pos=c1)
        return Asts.GenericTypeParameterRequiredAst(c1, Asts.TypeAst.from_identifier(p1), p2)

    @parser_rule
    def parse_generic_type_parameter_optional(self) -> Asts.GenericTypeParameterOptionalAst:
        c1 = self.current_pos()
        p1 = self.parse_upper_identifier().parse_once()
        p2 = self.parse_generic_inline_constraints().parse_optional() or Asts.GenericTypeParameterInlineConstraintsAst(pos=c1)
        p3 = self.parse_token(SppTokenType.TkAssign).parse_once()
        p4 = self.parse_type().parse_once()
        return Asts.GenericTypeParameterOptionalAst(c1, Asts.TypeAst.from_identifier(p1), p2, p3, p4)

    @parser_rule
    def parse_generic_type_parameter_variadic(self) -> Asts.GenericTypeParameterVariadicAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.TkDblDot).parse_once()
        p2 = self.parse_upper_identifier().parse_once()
        p3 = self.parse_generic_inline_constraints().parse_optional() or Asts.GenericTypeParameterInlineConstraintsAst(pos=c1)
        return Asts.GenericTypeParameterVariadicAst(c1, p1, Asts.TypeAst.from_identifier(p2), p3)

    @parser_rule
    def parse_generic_comp_parameter_required(self) -> Asts.GenericCompParameterRequiredAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.KwCmp).parse_once()
        p2 = self.parse_identifier().parse_once()
        p3 = self.parse_token(SppTokenType.TkColon).parse_once()
        p4 = self.parse_type().parse_once()
        return Asts.GenericCompParameterRequiredAst(c1, p1, Asts.TypeAst.from_identifier(p2), p3, p4)

    @parser_rule
    def parse_generic_comp_parameter_optional(self) -> Asts.GenericCompParameterOptionalAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.KwCmp).parse_once()
        p2 = self.parse_identifier().parse_once()
        p3 = self.parse_token(SppTokenType.TkColon).parse_once()
        p4 = self.parse_type().parse_once()
        p5 = self.parse_token(SppTokenType.TkAssign).parse_once()
        p6 = self.parse_global_constant_value().parse_once()
        return Asts.GenericCompParameterOptionalAst(c1, p1, Asts.TypeAst.from_identifier(p2), p3, p4, p5, p6)

    @parser_rule
    def parse_generic_comp_parameter_variadic(self) -> Asts.GenericCompParameterVariadicAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.KwCmp).parse_once()
        p2 = self.parse_token(SppTokenType.TkDblDot).parse_once()
        p3 = self.parse_identifier().parse_once()
        p4 = self.parse_token(SppTokenType.TkColon).parse_once()
        p5 = self.parse_type().parse_once()
        return Asts.GenericCompParameterVariadicAst(c1, p1, p2, Asts.TypeAst.from_identifier(p3), p4, p5)

    @parser_rule
    def parse_generic_inline_constraints(self) -> Asts.GenericTypeParameterInlineConstraintsAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.TkColon).parse_once()
        p2 = self.parse_type().parse_one_or_more(SppTokenType.TkComma)
        return Asts.GenericTypeParameterInlineConstraintsAst(c1, p1, Seq(p2))

    # ===== WHERE =====

    @parser_rule
    def parse_where_block(self) -> Asts.WhereBlockAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.KwWhere).parse_once()
        p2 = self.parse_where_block_constraints_group().parse_once()
        return Asts.WhereBlockAst(c1, p1, p2)

    @parser_rule
    def parse_where_block_constraints_group(self) -> Asts.WhereConstraintsGroupAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.TkBrackL).parse_once()
        p2 = self.parse_where_block_constraints().parse_one_or_more(SppTokenType.TkComma)
        p3 = self.parse_token(SppTokenType.TkBrackR).parse_once()
        return Asts.WhereConstraintsGroupAst(c1, p1, Seq(p2), p3)

    @parser_rule
    def parse_where_block_constraints(self) -> Asts.WhereConstraintsAst:
        c1 = self.current_pos()
        p1 = self.parse_type().parse_one_or_more(SppTokenType.TkComma)
        p2 = self.parse_token(SppTokenType.TkColon).parse_once()
        p3 = self.parse_type().parse_once()
        return Asts.WhereConstraintsAst(c1, Seq(p1), p2, p3)

    # ===== ANNOTATIONS =====

    @parser_rule
    def parse_annotation(self) -> Asts.AnnotationAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.TkAt).parse_once()
        p2 = self.parse_identifier().parse_once()
        return Asts.AnnotationAst(c1, p1, p2)

    # ===== EXPRESSIONS =====

    @parser_rule
    def parse_expression(self) -> Asts.ExpressionAst:
        p1 = self.parse_binary_expression_precedence_level_1().parse_once()
        return p1

    @parser_rule
    def parse_binary_expression_precedence_level_n_rhs(self, op, rhs) -> Tuple[Asts.TokenAst, Asts.ExpressionAst]:
        p1 = op().parse_once()
        p2 = rhs().parse_once()
        return p1, p2

    @parser_rule
    def parse_binary_expression_precedence_level_n(self, lhs, op, rhs) -> Asts.BinaryExpressionAst:
        c1 = self.current_pos()
        p1 = lhs().parse_once()
        p2 = self.parse_binary_expression_precedence_level_n_rhs(op, rhs).parse_optional()
        return Asts.BinaryExpressionAst(c1, p1, p2[0], p2[1]) if p2 else p1

    def parse_binary_expression_precedence_level_1(self) -> ParserRuleHandler:
        return self.parse_binary_expression_precedence_level_n(
            self.parse_binary_expression_precedence_level_2,
            self.parse_binary_op_precedence_level_1,
            self.parse_binary_expression_precedence_level_1)

    def parse_binary_expression_precedence_level_2(self) -> ParserRuleHandler:
        return self.parse_binary_expression_precedence_level_n(
            self.parse_binary_expression_precedence_level_3,
            self.parse_binary_op_precedence_level_2,
            self.parse_binary_expression_precedence_level_2)

    def parse_binary_expression_precedence_level_3(self) -> ParserRuleHandler:
        return self.parse_binary_expression_precedence_level_n(
            self.parse_binary_expression_precedence_level_4,
            self.parse_binary_op_precedence_level_3,
            self.parse_pattern_group_destructure)

    def parse_binary_expression_precedence_level_4(self) -> ParserRuleHandler:
        return self.parse_binary_expression_precedence_level_n(
            self.parse_binary_expression_precedence_level_5,
            self.parse_binary_op_precedence_level_4,
            self.parse_binary_expression_precedence_level_4)

    def parse_binary_expression_precedence_level_5(self) -> ParserRuleHandler:
        return self.parse_binary_expression_precedence_level_n(
            self.parse_binary_expression_precedence_level_6,
            self.parse_binary_op_precedence_level_5,
            self.parse_binary_expression_precedence_level_5)

    def parse_binary_expression_precedence_level_6(self) -> ParserRuleHandler:
        return self.parse_binary_expression_precedence_level_n(
            self.parse_unary_expression,
            self.parse_binary_op_precedence_level_6,
            self.parse_binary_expression_precedence_level_6)

    @parser_rule
    def parse_unary_expression(self) -> Asts.ExpressionAst:
        c1 = self.current_pos()
        p1 = self.parse_unary_op().parse_zero_or_more(SpecialToken.NO_TOK)
        p2 = self.parse_postfix_expression().parse_once()
        return functools.reduce(lambda acc, x: Asts.UnaryExpressionAst(c1, x, acc), p1, p2)

    @parser_rule
    def parse_postfix_expression(self) -> Asts.ExpressionAst:
        c1 = self.current_pos()
        p1 = self.parse_primary_expression().parse_once()
        p2 = self.parse_postfix_op().parse_zero_or_more(SpecialToken.NO_TOK)
        return functools.reduce(lambda acc, x: Asts.PostfixExpressionAst(c1, acc, x), p2, p1)

    @parser_rule
    def parse_primary_expression(self) -> Asts.ExpressionAst:
        p1 = self.parse_literal()
        p2 = self.parse_object_initializer()
        # p3 = self.parse_lambda_prototype()
        p4 = self.parse_parenthesized_expression()
        p5 = self.parse_type()
        p6 = self.parse_identifier()
        p7 = self.parse_case_expression()
        p8 = self.parse_loop_expression()
        p9 = self.parse_gen_expression()
        p10 = self.parse_with_expression()
        p11 = self.parse_inner_scope()
        p12 = self.parse_self_keyword()
        p13 = self.parse_token(SppTokenType.TkDblDot)
        p14 = (p1 | p2 | p4 | p5 | p6 | p7 | p8 | p9 | p10 | p11 | p12 | p13).parse_once()
        return p14

    @parser_rule
    def parse_parenthesized_expression(self) -> Asts.ParenthesizedExpressionAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.TkParenL).parse_once()
        p2 = self.parse_expression().parse_once()
        p3 = self.parse_token(SppTokenType.TkParenR).parse_once()
        return Asts.ParenthesizedExpressionAst(c1, p1, p2, p3)

    @parser_rule
    def parse_self_keyword(self) -> Asts.IdentifierAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.KwSelf).parse_once()
        return Asts.IdentifierAst(c1, p1.token.token_metadata)

    # ===== EXPRESSION STATEMENTS =====

    @parser_rule
    def parse_case_expression(self) -> Asts.CaseExpressionAst:
        p1 = self.parse_case_expression_patterns()
        p2 = self.parse_case_expression_simple()
        p3 = (p1 | p2).parse_once()
        return p3

    @parser_rule
    def parse_case_expression_patterns(self) -> Asts.CaseExpressionAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.KwCase).parse_once()
        p2 = self.parse_expression().parse_once()
        p3 = self.parse_token(SppTokenType.KwOf).parse_once()
        p4 = self.parse_case_expression_branch().parse_one_or_more(SpecialToken.NO_TOK)
        return Asts.CaseExpressionAst(c1, p1, p2, p3, Seq(p4))

    @parser_rule
    def parse_case_expression_simple(self) -> Asts.CaseExpressionAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.KwCase).parse_once()
        p2 = self.parse_expression().parse_once()
        p3 = self.parse_inner_scope().parse_once()
        p4 = self.parse_case_expression_branch_simple().parse_zero_or_more(SpecialToken.NO_TOK)
        return Asts.CaseExpressionAst.from_simple(c1, p1, p2, p3, Seq(p4))

    @parser_rule
    def parse_loop_expression(self) -> Asts.LoopExpressionAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.KwLoop).parse_once()
        p2 = self.parse_loop_expression_condition().parse_once()
        p3 = self.parse_inner_scope().parse_once()
        p4 = self.parse_loop_else_statement().parse_optional()
        return Asts.LoopExpressionAst(c1, p1, p2, p3, p4)

    @parser_rule
    def parse_loop_expression_condition(self) -> Asts.LoopConditionAst:
        p1 = self.parse_loop_expression_condition_iterable()
        p2 = self.parse_loop_expression_condition_boolean()
        p3 = (p1 | p2).parse_once()
        return p3

    @parser_rule
    def parse_loop_expression_condition_boolean(self) -> Asts.LoopConditionBooleanAst:
        c1 = self.current_pos()
        p1 = self.parse_expression().parse_once()
        return Asts.LoopConditionBooleanAst(c1, p1)

    @parser_rule
    def parse_loop_expression_condition_iterable(self) -> Asts.LoopConditionIterableAst:
        c1 = self.current_pos()
        p1 = self.parse_local_variable().parse_once()
        p2 = self.parse_token(SppTokenType.KwIn).parse_once()
        p3 = self.parse_expression().parse_once()
        return Asts.LoopConditionIterableAst(c1, p1, p2, p3)

    @parser_rule
    def parse_loop_else_statement(self) -> Asts.LoopElseStatementAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.KwElse).parse_once()
        p2 = self.parse_inner_scope().parse_once()
        return Asts.LoopElseStatementAst(c1, p1, p2)

    @parser_rule
    def parse_gen_expression(self) -> Asts.GenExpressionAst:
        p1 = self.parse_gen_expression_unroll()
        p2 = self.parse_gen_expression_normal()
        p3 = (p1 | p2).parse_once()
        return p3

    @parser_rule
    def parse_gen_expression_normal(self) -> Asts.GenExpressionAst:
        p1 = self.parse_gen_expression_normal_with_expression()
        p2 = self.parse_gen_expression_normal_no_expression()
        p3 = (p1 | p2).parse_once()
        return p3

    @parser_rule
    def parse_gen_expression_normal_no_expression(self) -> Asts.GenExpressionAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.KwGen).parse_once()
        return Asts.GenExpressionAst(c1, p1, None, Asts.ConventionMovAst(p1.pos), None)

    @parser_rule
    def parse_gen_expression_normal_with_expression(self) -> Asts.GenExpressionAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.KwGen).parse_once()
        p2 = self.parse_convention().parse_once()
        p3 = self.parse_expression().parse_once()
        return Asts.GenExpressionAst(c1, p1, None, p2, p3)

    @parser_rule
    def parse_gen_expression_unroll(self) -> Asts.GenExpressionAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.KwGen).parse_once()
        p2 = self.parse_token(SppTokenType.KwWith).parse_once()
        p3 = self.parse_expression().parse_once()
        return Asts.GenExpressionAst(c1, p1, p2, Asts.ConventionMovAst(p3.pos), p3)

    @parser_rule
    def parse_with_expression(self) -> Asts.WithExpressionAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.KwWith).parse_once()
        p2 = self.parse_with_expression_lhs_alias().parse_optional()
        p3 = self.parse_expression().parse_once()
        p4 = self.parse_inner_scope().parse_once()
        return Asts.WithExpressionAst(c1, p1, p2, p3, p4)

    @parser_rule
    def parse_with_expression_lhs_alias(self) -> Asts.WithExpressionAliasAst:
        c1 = self.current_pos()
        p1 = self.parse_local_variable().parse_once()
        p2 = self.parse_token(SppTokenType.TkAssign).parse_once()
        return Asts.WithExpressionAliasAst(c1, p1, p2)

    # ===== STATEMENTS =====

    @parser_rule
    def parse_ret_statement(self) -> Asts.RetStatementAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.KwRet).parse_once()
        p2 = self.parse_expression().parse_optional()
        return Asts.RetStatementAst(c1, p1, p2)

    @parser_rule
    def parse_exit_statement(self) -> Asts.LoopControlFlowStatementAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.KwExit).parse_one_or_more(SpecialToken.NO_TOK)
        p2 = self.parse_exit_statement_final_action().parse_optional()
        return Asts.LoopControlFlowStatementAst(c1, Seq(p1), p2)

    @parser_rule
    def parse_exit_statement_final_action(self) -> Asts.TokenAst | Asts.ExpressionAst:
        p1 = self.parse_token(SppTokenType.KwSkip)
        p2 = self.parse_expression()
        p3 = (p1 | p2).parse_once()
        return p3

    @parser_rule
    def parse_skip_statement(self) -> Asts.LoopControlFlowStatementAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.KwSkip).parse_once()
        return Asts.LoopControlFlowStatementAst(c1, Seq(), p1)

    @parser_rule
    def parse_pin_statement(self) -> Asts.PinStatementAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.KwPin).parse_once()
        p2 = self.parse_expression().parse_one_or_more(SppTokenType.TkComma)
        return Asts.PinStatementAst(c1, p1, Seq(p2))

    @parser_rule
    def parse_rel_statement(self) -> Asts.RelStatementAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.KwRel).parse_once()
        p2 = self.parse_expression().parse_one_or_more(SppTokenType.TkComma)
        return Asts.RelStatementAst(c1, p1, Seq(p2))

    @parser_rule
    def parse_inner_scope(self) -> Asts.InnerScopeAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.TkBraceL).parse_once()
        p2 = self.parse_statement().parse_zero_or_more(SpecialToken.NO_TOK)
        p3 = self.parse_token(SppTokenType.TkBraceR).parse_once()
        return Asts.InnerScopeAst(c1, p1, Seq(p2), p3)

    @parser_rule
    def parse_statement(self) -> Asts.StatementAst:
        p1 = self.parse_use_statement()
        p2 = self.parse_let_statement()
        p3 = self.parse_ret_statement()
        p4 = self.parse_exit_statement()
        p5 = self.parse_skip_statement()
        p6 = self.parse_pin_statement()
        p7 = self.parse_rel_statement()
        p8 = self.parse_assignment_statement()
        p9 = self.parse_expression()
        p10 = (p1 | p2 | p3 | p4 | p5 | p6 | p7 | p8 | p9).parse_once()
        return p10

    # ===== TYPEDEFS =====

    @parser_rule
    def parse_global_use_statement(self) -> Asts.UseStatementAst:
        p1 = self.parse_annotation().parse_zero_or_more(SppTokenType.TkNewLine)
        p2 = self.parse_use_statement().parse_once()
        p2.annotations = Seq(p1)
        return p2

    @parser_rule
    def parse_use_statement(self) -> Asts.UseStatementAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.KwUse).parse_once()
        p2 = self.parse_upper_identifier().parse_once()
        p3 = self.parse_generic_parameters().parse_optional() or Asts.GenericParameterGroupAst(pos=c1)
        p4 = self.parse_token(SppTokenType.TkAssign).parse_once()
        p5 = self.parse_type().parse_once()
        return Asts.UseStatementAst(c1, Seq(), p1, Asts.TypeAst.from_identifier(p2), p3, p4, p5)

    # ===== LET-DECLARATIONS =====

    @parser_rule
    def parse_global_constant(self) -> Asts.GlobalConstantAst:
        c1 = self.current_pos()
        p1 = self.parse_annotation().parse_zero_or_more(SppTokenType.TkNewLine)
        p2 = self.parse_token(SppTokenType.KwCmp).parse_once()
        p3 = self.parse_identifier().parse_once()
        p4 = self.parse_token(SppTokenType.TkColon).parse_once()
        p5 = self.parse_type().parse_once()
        p6 = self.parse_token(SppTokenType.TkAssign).parse_once()
        p7 = self.parse_global_constant_value().parse_once()
        return Asts.GlobalConstantAst(c1, Seq(p1), p2, p3, p4, p5, p6, p7)

    @parser_rule
    def parse_let_statement(self) -> Asts.LetStatementAst:
        p1 = self.parse_let_statement_initialized()
        p2 = self.parse_let_statement_uninitialized()
        p3 = (p1 | p2).parse_once()
        return p3

    @parser_rule
    def parse_let_statement_initialized(self) -> Asts.LetStatementInitializedAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.KwLet).parse_once()
        p2 = self.parse_local_variable().parse_once()
        p3 = self.parse_token(SppTokenType.TkAssign).parse_once()
        p4 = self.parse_expression().parse_once()
        return Asts.LetStatementInitializedAst(c1, p1, p2, p3, p4)

    @parser_rule
    def parse_let_statement_uninitialized(self) -> Asts.LetStatementUninitializedAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.KwLet).parse_once()
        p2 = self.parse_local_variable().parse_once()
        p3 = self.parse_token(SppTokenType.TkColon).parse_once()
        p4 = self.parse_type().parse_once()
        return Asts.LetStatementUninitializedAst(c1, p1, p2, p3, p4)

    @parser_rule
    def parse_local_variable(self) -> Asts.LocalVariableAst:
        p1 = self.parse_local_variable_destructure_array()
        p2 = self.parse_local_variable_destructure_tuple()
        p3 = self.parse_local_variable_destructure_object()
        p4 = self.parse_local_variable_single_identifier()
        p5 = (p1 | p2 | p3 | p4).parse_once()
        return p5

    @parser_rule
    def parse_local_variable_destructure_skip_argument(self) -> Asts.LocalVariableDestructureSkip1ArgumentAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.TkUnderscore).parse_once()
        return Asts.LocalVariableDestructureSkip1ArgumentAst(c1, p1)

    @parser_rule
    def parse_local_variable_destructure_skip_arguments(self) -> Asts.LocalVariableDestructureSkipNArgumentsAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.TkDblDot).parse_once()
        p2 = self.parse_local_variable_single_identifier().parse_optional()
        return Asts.LocalVariableDestructureSkipNArgumentsAst(c1, p1, p2)

    @parser_rule
    def parse_local_variable_single_identifier(self) -> Asts.LocalVariableSingleIdentifierAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.KwMut).parse_optional()
        p2 = self.parse_identifier().parse_once()
        p3 = self.parse_local_variable_single_identifier_alias().parse_optional()
        return Asts.LocalVariableSingleIdentifierAst(c1, p1, p2, p3)

    @parser_rule
    def parse_local_variable_single_identifier_alias(self) -> Asts.LocalVariableSingleIdentifierAliasAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.KwAs).parse_once()
        p2 = self.parse_identifier().parse_once()
        return Asts.LocalVariableSingleIdentifierAliasAst(c1, p1, p2)

    @parser_rule
    def parse_local_variable_destructure_array(self) -> Asts.LocalVariableDestructureArrayAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.TkBrackL).parse_once()
        p2 = self.parse_local_variable_nested_for_destructure_array().parse_one_or_more(SppTokenType.TkComma)
        p3 = self.parse_token(SppTokenType.TkBrackR).parse_once()
        return Asts.LocalVariableDestructureArrayAst(c1, p1, Seq(p2), p3)

    @parser_rule
    def parse_local_variable_destructure_tuple(self) -> Asts.LocalVariableDestructureTupleAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.TkParenL).parse_once()
        p2 = self.parse_local_variable_nested_for_destructure_tuple().parse_one_or_more(SppTokenType.TkComma)
        p3 = self.parse_token(SppTokenType.TkParenR).parse_once()
        return Asts.LocalVariableDestructureTupleAst(c1, p1, Seq(p2), p3)

    @parser_rule
    def parse_local_variable_destructure_object(self) -> Asts.LocalVariableDestructureObjectAst:
        c1 = self.current_pos()
        p1 = self.parse_type_single().parse_once()
        p2 = self.parse_token(SppTokenType.TkParenL).parse_once()
        p3 = self.parse_local_variable_nested_for_destructure_object().parse_zero_or_more(SppTokenType.TkComma)  # one or more?
        p4 = self.parse_token(SppTokenType.TkParenR).parse_once()
        return Asts.LocalVariableDestructureObjectAst(c1, p1, p2, Seq(p3), p4)

    @parser_rule
    def parse_local_variable_attribute_binding(self) -> Asts.LocalVariableAttributeBindingAst:
        c1 = self.current_pos()
        p1 = self.parse_identifier().parse_once()
        p2 = self.parse_token(SppTokenType.TkAssign).parse_once()
        p3 = self.parse_local_variable_nested_for_attribute_binding().parse_once()
        return Asts.LocalVariableAttributeBindingAst(c1, p1, p2, p3)

    @parser_rule
    def parse_local_variable_nested_for_destructure_array(self) -> Asts.LocalVariableNestedForDestructureArrayAst:
        p1 = self.parse_local_variable_destructure_array()
        p2 = self.parse_local_variable_destructure_tuple()
        p3 = self.parse_local_variable_destructure_object()
        p4 = self.parse_local_variable_single_identifier()
        p5 = self.parse_local_variable_destructure_skip_arguments()
        p6 = self.parse_local_variable_destructure_skip_argument()
        p7 = (p1 | p2 | p3 | p4 | p5 | p6).parse_once()
        return p7

    @parser_rule
    def parse_local_variable_nested_for_destructure_tuple(self) -> Asts.LocalVariableNestedForDestructureTupleAst:
        p1 = self.parse_local_variable_destructure_array()
        p2 = self.parse_local_variable_destructure_tuple()
        p3 = self.parse_local_variable_destructure_object()
        p4 = self.parse_local_variable_single_identifier()
        p5 = self.parse_local_variable_destructure_skip_arguments()
        p6 = self.parse_local_variable_destructure_skip_argument()
        p7 = (p1 | p2 | p3 | p4 | p5 | p6).parse_once()
        return p7

    @parser_rule
    def parse_local_variable_nested_for_destructure_object(self) -> Asts.LocalVariableNestedForDestructureObjectAst:
        p1 = self.parse_local_variable_attribute_binding()
        p2 = self.parse_local_variable_single_identifier()
        p3 = self.parse_local_variable_destructure_skip_arguments()
        p4 = (p1 | p2 | p3).parse_once()
        return p4

    @parser_rule
    def parse_local_variable_nested_for_attribute_binding(self) -> Asts.LocalVariableNestedForAttributeBindingAst:
        p1 = self.parse_local_variable_destructure_array()
        p2 = self.parse_local_variable_destructure_tuple()
        p3 = self.parse_local_variable_destructure_object()
        p4 = self.parse_local_variable_single_identifier()
        p5 = (p1 | p2 | p3 | p4).parse_once()
        return p5

    # ===== ASSIGNMENT =====

    @parser_rule
    def parse_assignment_statement(self) -> Asts.AssignmentStatementAst:
        c1 = self.current_pos()
        p1 = self.parse_expression().parse_one_or_more(SppTokenType.TkComma)
        p2 = self.parse_token(SppTokenType.TkAssign).parse_once()
        p3 = self.parse_expression().parse_one_or_more(SppTokenType.TkComma)
        return Asts.AssignmentStatementAst(c1, Seq(p1), p2, Seq(p3))

    # ===== PATTERNS =====

    @parser_rule
    def parse_case_expression_branch_simple(self) -> Asts.CaseExpressionBranchAst:
        p1 = self.parse_pattern_statement_flavour_else_case()
        p2 = self.parse_pattern_statement_flavour_else()
        p3 = (p1 | p2).parse_once()
        return p3

    @parser_rule
    def parse_case_expression_branch(self) -> Asts.CaseExpressionBranchAst:
        p1 = self.parse_pattern_statement_flavour_destructuring()
        p2 = self.parse_pattern_statement_flavour_non_destructuring()
        p3 = self.parse_pattern_statement_flavour_else_case()
        p4 = self.parse_pattern_statement_flavour_else()
        p5 = (p1 | p2 | p3 | p4).parse_once()
        return p5

    @parser_rule
    def parse_pattern_statement_flavour_destructuring(self) -> Asts.CaseExpressionBranchAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.KwIs).parse_once()
        p2 = self.parse_pattern_group_destructure().parse_one_or_more(SppTokenType.TkComma)
        p3 = self.parse_pattern_guard().parse_optional()
        p4 = self.parse_inner_scope().parse_once()
        return Asts.CaseExpressionBranchAst(c1, p1, Seq(p2), p3, p4)

    @parser_rule
    def parse_pattern_statement_flavour_non_destructuring(self) -> Asts.CaseExpressionBranchAst:
        c1 = self.current_pos()
        p1 = self.parse_boolean_comparison_op().parse_once()
        p2 = self.parse_pattern_variant_expression().parse_one_or_more(SppTokenType.TkComma)
        p3 = self.parse_inner_scope().parse_once()
        return Asts.CaseExpressionBranchAst(c1, p1, Seq(p2), None, p3)

    @parser_rule
    def parse_pattern_statement_flavour_else_case(self) -> Asts.CaseExpressionBranchAst:
        c1 = self.current_pos()
        p1 = self.parse_pattern_variant_else_case().parse_once()
        return Asts.CaseExpressionBranchAst.from_else_to_else_case(c1, p1)

    @parser_rule
    def parse_pattern_statement_flavour_else(self) -> Asts.CaseExpressionBranchAst:
        c1 = self.current_pos()
        p1 = self.parse_pattern_variant_else().parse_once()
        p2 = self.parse_inner_scope().parse_once()
        return Asts.CaseExpressionBranchAst(c1, None, Seq([p1]), None, p2)

    @parser_rule
    def parse_pattern_group_destructure(self) -> Asts.PatternGroupDestructureAst:
        p1 = self.parse_pattern_variant_destructure_array()
        p2 = self.parse_pattern_variant_destructure_tuple()
        p3 = self.parse_pattern_variant_destructure_object()
        return (p1 | p2 | p3).parse_once()

    @parser_rule
    def parse_pattern_variant_skip_argument(self) -> Asts.PatternVariantDestructureSkip1ArgumentAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.TkUnderscore).parse_once()
        return Asts.PatternVariantDestructureSkip1ArgumentAst(c1, p1)

    @parser_rule
    def parse_pattern_variant_skip_arguments(self) -> Asts.PatternVariantDestructureSkipNArgumentsAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.TkDblDot).parse_once()
        p2 = self.parse_pattern_variant_single_identifier().parse_optional()
        return Asts.PatternVariantDestructureSkipNArgumentsAst(c1, p1, p2)

    @parser_rule
    def parse_pattern_variant_single_identifier(self) -> Asts.PatternVariantSingleIdentifierAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.KwMut).parse_optional()
        p2 = self.parse_identifier().parse_once()
        p3 = self.parse_local_variable_single_identifier_alias().parse_optional()
        return Asts.PatternVariantSingleIdentifierAst(c1, p1, p2, p3)

    @parser_rule
    def parse_pattern_variant_destructure_tuple(self) -> Asts.PatternVariantDestructureTupleAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.TkParenL).parse_once()
        p2 = self.parse_pattern_variant_nested_for_destructure_tuple().parse_one_or_more(SppTokenType.TkComma)
        p3 = self.parse_token(SppTokenType.TkParenR).parse_once()
        return Asts.PatternVariantDestructureTupleAst(c1, p1, Seq(p2), p3)

    @parser_rule
    def parse_pattern_variant_destructure_array(self) -> Asts.PatternVariantDestructureArrayAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.TkBrackL).parse_once()
        p2 = self.parse_pattern_variant_nested_for_destructure_array().parse_one_or_more(SppTokenType.TkComma)
        p3 = self.parse_token(SppTokenType.TkBrackR).parse_once()
        return Asts.PatternVariantDestructureArrayAst(c1, p1, Seq(p2), p3)

    @parser_rule
    def parse_pattern_variant_destructure_object(self) -> Asts.PatternVariantDestructureObjectAst:
        c1 = self.current_pos()
        p1 = self.parse_type_single().parse_once()
        p2 = self.parse_token(SppTokenType.TkParenL).parse_once()
        p3 = self.parse_pattern_variant_nested_for_destructure_object().parse_zero_or_more(SppTokenType.TkComma)  # one or more?
        p4 = self.parse_token(SppTokenType.TkParenR).parse_once()
        return Asts.PatternVariantDestructureObjectAst(c1, p1, p2, Seq(p3), p4)

    @parser_rule
    def parse_pattern_variant_attribute_binding(self) -> Asts.PatternVariantAttributeBindingAst:
        c1 = self.current_pos()
        p1 = self.parse_identifier().parse_once()
        p2 = self.parse_token(SppTokenType.TkAssign).parse_once()
        p3 = self.parse_pattern_variant_nested_for_attribute_binding().parse_once()
        return Asts.PatternVariantAttributeBindingAst(c1, p1, p2, p3)

    @parser_rule
    def parse_pattern_variant_literal(self) -> Asts.PatternVariantLiteralAst:
        c1 = self.current_pos()
        p1 = self.parse_literal_float()
        p2 = self.parse_literal_integer()
        p3 = self.parse_literal_string()
        p4 = self.parse_literal_boolean()
        p5 = (p1 | p2 | p3 | p4).parse_once()
        return Asts.PatternVariantLiteralAst(c1, p5)

    @parser_rule
    def parse_pattern_variant_expression(self) -> Asts.PatternVariantExpressionAst:
        c1 = self.current_pos()
        p1 = self.parse_expression().parse_once()
        return Asts.PatternVariantExpressionAst(c1, p1)

    @parser_rule
    def parse_pattern_variant_else(self) -> Asts.PatternVariantElseAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.KwElse).parse_once()
        return Asts.PatternVariantElseAst(c1, p1)

    @parser_rule
    def parse_pattern_variant_else_case(self) -> Asts.PatternVariantElseCaseAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.KwElse).parse_once()
        p2 = self.parse_case_expression().parse_once()
        return Asts.PatternVariantElseCaseAst(c1, p1, p2)

    @parser_rule
    def parse_pattern_variant_nested_for_destructure_tuple(self) -> Asts.PatternVariantNestedForDestructureTupleAst:
        p1 = self.parse_pattern_variant_destructure_array()
        p2 = self.parse_pattern_variant_destructure_tuple()
        p3 = self.parse_pattern_variant_destructure_object()
        p4 = self.parse_pattern_variant_single_identifier()
        p5 = self.parse_pattern_variant_literal()
        p6 = self.parse_pattern_variant_skip_arguments()
        p7 = self.parse_pattern_variant_skip_argument()
        p8 = (p1 | p2 | p3 | p4 | p5 | p6 | p7).parse_once()
        return p8

    @parser_rule
    def parse_pattern_variant_nested_for_destructure_array(self) -> Asts.PatternVariantNestedForDestructureArrayAst:
        p1 = self.parse_pattern_variant_destructure_array()
        p2 = self.parse_pattern_variant_destructure_tuple()
        p3 = self.parse_pattern_variant_destructure_object()
        p4 = self.parse_pattern_variant_single_identifier()
        p5 = self.parse_pattern_variant_literal()
        p6 = self.parse_pattern_variant_skip_arguments()
        p7 = self.parse_pattern_variant_skip_argument()
        p8 = (p1 | p2 | p3 | p4 | p5 | p6 | p7).parse_once()
        return p8

    @parser_rule
    def parse_pattern_variant_nested_for_destructure_object(self) -> Asts.PatternVariantNestedForDestructureObjectAst:
        p1 = self.parse_pattern_variant_attribute_binding()
        p2 = self.parse_pattern_variant_single_identifier()
        p3 = self.parse_pattern_variant_skip_arguments()
        p4 = (p1 | p2 | p3).parse_once()
        return p4

    @parser_rule
    def parse_pattern_variant_nested_for_attribute_binding(self) -> Asts.PatternVariantNestedForAttributeBindingAst:
        p1 = self.parse_pattern_variant_destructure_array()
        p2 = self.parse_pattern_variant_destructure_tuple()
        p3 = self.parse_pattern_variant_destructure_object()
        p4 = self.parse_pattern_variant_literal()
        p5 = (p1 | p2 | p3 | p4).parse_once()
        return p5

    @parser_rule
    def parse_pattern_guard(self) -> Asts.PatternGuardAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.KwAnd).parse_once()
        p2 = self.parse_expression().parse_once()
        return Asts.PatternGuardAst(c1, p1, p2)

    # ===== OPERATORS =====

    @parser_rule
    def parse_binary_op_precedence_level_1(self) -> Asts.TokenAst:
        p1 = self.parse_token(SppTokenType.KwOr).parse_once()
        return p1

    @parser_rule
    def parse_binary_op_precedence_level_2(self) -> Asts.TokenAst:
        p1 = self.parse_token(SppTokenType.KwAnd).parse_once()
        return p1

    @parser_rule
    def parse_binary_op_precedence_level_3(self) -> Asts.TokenAst:
        p1 = self.parse_token(SppTokenType.KwIs).parse_once()
        return p1

    @parser_rule
    def parse_binary_op_precedence_level_4(self) -> Asts.TokenAst:
        p1 = self.parse_token(SppTokenType.TkEq)
        p2 = self.parse_token(SppTokenType.TkNe)
        p3 = self.parse_token(SppTokenType.TkLe)
        p4 = self.parse_token(SppTokenType.TkGe)
        p5 = self.parse_token(SppTokenType.TkLt)
        p6 = self.parse_token(SppTokenType.TkGt)
        p7 = self.parse_token(SppTokenType.TkSs)
        p8 = (p1 | p2 | p3 | p4 | p5 | p6 | p7).parse_once()
        return p8

    @parser_rule
    def parse_binary_op_precedence_level_5(self) -> Asts.TokenAst:
        p1 = self.parse_token(SppTokenType.TkAdd)
        p2 = self.parse_token(SppTokenType.TkSub)
        p3 = self.parse_token(SppTokenType.TkAddAssign)
        p4 = self.parse_token(SppTokenType.TkSubAssign)
        p5 = (p1 | p2 | p3 | p4).parse_once()
        return p5

    @parser_rule
    def parse_binary_op_precedence_level_6(self) -> Asts.TokenAst:
        p1 = self.parse_token(SppTokenType.TkMul)
        p2 = self.parse_token(SppTokenType.TkDiv)
        p3 = self.parse_token(SppTokenType.TkRem)
        p4 = self.parse_token(SppTokenType.TkMod)
        p5 = self.parse_token(SppTokenType.TkExp)
        p6 = self.parse_token(SppTokenType.TkMulAssign)
        p7 = self.parse_token(SppTokenType.TkDivAssign)
        p8 = self.parse_token(SppTokenType.TkRemAssign)
        p9 = self.parse_token(SppTokenType.TkModAssign)
        p10 = self.parse_token(SppTokenType.TkExpAssign)
        p11 = (p1 | p2 | p3 | p4 | p5 | p6 | p7 | p8 | p9 | p10).parse_once()
        return p11

    @parser_rule
    def parse_boolean_comparison_op(self) -> Asts.TokenAst:
        p1 = self.parse_token(SppTokenType.TkEq)
        p2 = self.parse_token(SppTokenType.TkNe)
        p3 = self.parse_token(SppTokenType.TkLe)
        p4 = self.parse_token(SppTokenType.TkGe)
        p5 = self.parse_token(SppTokenType.TkLt)
        p6 = self.parse_token(SppTokenType.TkGt)
        p8 = (p1 | p2 | p3 | p4 | p5 | p6).parse_once()
        return p8

    @parser_rule
    def parse_unary_op(self) -> Asts.TokenAst:
        p1 = self.parse_unary_op_async_call().parse_once()
        return p1

    @parser_rule
    def parse_unary_op_async_call(self) -> Asts.UnaryExpressionOperatorAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.KwAsync).parse_once()
        return Asts.UnaryExpressionOperatorAsyncAst(c1, p1)

    @parser_rule
    def parse_postfix_op(self) -> Asts.PostfixExpressionOperatorAst:
        p1 = self.parse_postfix_op_function_call()
        p2 = self.parse_postfix_op_member_access()
        p3 = self.parse_postfix_op_early_return()
        p4 = self.parse_postfix_op_not_keyword()
        p5 = self.parse_postfix_op_step_keyword()
        p6 = (p1 | p2 | p3 | p4 | p5).parse_once()
        return p6

    @parser_rule
    def parse_postfix_op_function_call(self) -> Asts.PostfixExpressionOperatorFunctionCallAst:
        c1 = self.current_pos()
        p1 = self.parse_generic_arguments().parse_optional() or Asts.GenericArgumentGroupAst(pos=c1)
        p2 = self.parse_function_call_arguments().parse_once()
        p3 = self.parse_token(SppTokenType.TkDblDot).parse_optional()
        return Asts.PostfixExpressionOperatorFunctionCallAst(c1, p1, p2, p3)

    @parser_rule
    def parse_postfix_op_member_access(self) -> Asts.PostfixExpressionOperatorMemberAccessAst:
        p1 = self.parse_postfix_op_member_access_runtime()
        p2 = self.parse_postfix_op_member_access_static()
        p3 = (p1 | p2).parse_once()
        return p3

    @parser_rule
    def parse_postfix_op_member_access_runtime(self) -> Asts.PostfixExpressionOperatorMemberAccessAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.TkDot).parse_once()
        p2 = self.parse_identifier()
        p3 = self.parse_lexeme(SppTokenType.LxDecInteger)
        p4 = (p2 | p3).parse_once()
        return Asts.PostfixExpressionOperatorMemberAccessAst(c1, p1, p4)

    @parser_rule
    def parse_postfix_op_member_access_static(self) -> Asts.PostfixExpressionOperatorMemberAccessAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.TkDblColon).parse_once()
        p2 = self.parse_identifier().parse_once()
        return Asts.PostfixExpressionOperatorMemberAccessAst(c1, p1, p2)

    @parser_rule
    def parse_postfix_op_early_return(self) -> Asts.PostfixExpressionOperatorEarlyReturnAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.TkQst).parse_once()
        return Asts.PostfixExpressionOperatorEarlyReturnAst(c1, p1)

    @parser_rule
    def parse_postfix_op_not_keyword(self) -> Asts.PostfixExpressionOperatorNotKeywordAst:
        # Todo: Allow "::" ?
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.TkDot).parse_once()
        p2 = self.parse_token(SppTokenType.KwNot).parse_once()
        return Asts.PostfixExpressionOperatorNotKeywordAst(c1, p1, p2)

    @parser_rule
    def parse_postfix_op_step_keyword(self) -> Asts.PostfixExpressionOperatorStepKeywordAst:
        # Todo: Allow "::" ?
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.TkDot).parse_once()
        p2 = self.parse_token(SppTokenType.KwStep).parse_once()
        return Asts.PostfixExpressionOperatorStepKeywordAst(c1, p1, p2)

    # ===== CONVENTIONS =====

    @parser_rule
    def parse_convention(self) -> Asts.ConventionAst:
        p1 = self.parse_convention_mut()
        p2 = self.parse_convention_ref()
        p3 = self.parse_convention_mov()
        p4 = (p1 | p2 | p3).parse_once()
        return p4

    @parser_rule
    def parse_convention_mov(self) -> Asts.ConventionMovAst:
        c1 = self.current_pos()
        return Asts.ConventionMovAst(c1)

    @parser_rule
    def parse_convention_ref(self) -> Asts.ConventionRefAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.TkBorrow).parse_once()
        return Asts.ConventionRefAst(c1, p1)

    @parser_rule
    def parse_convention_mut(self) -> Asts.ConventionMutAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.TkBorrow).parse_once()
        p2 = self.parse_token(SppTokenType.KwMut).parse_once()
        return Asts.ConventionMutAst(c1, p1, p2)

    # ===== OBJECT INITIALIZATION =====

    @parser_rule
    def parse_object_initializer(self) -> Asts.ObjectInitializerAst:
        c1 = self.current_pos()
        p1 = self.parse_type_single().parse_once()
        p2 = self.parse_object_initializer_arguments().parse_once()
        return Asts.ObjectInitializerAst(c1, p1, p2)

    @parser_rule
    def parse_object_initializer_arguments(self) -> Asts.ObjectInitializerArgumentGroupAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.TkParenL).parse_once()
        p2 = self.parse_object_initializer_argument().parse_zero_or_more(SppTokenType.TkComma)
        p3 = self.parse_token(SppTokenType.TkParenR).parse_once()
        return Asts.ObjectInitializerArgumentGroupAst(c1, p1, Seq(p2), p3)

    @parser_rule
    def parse_object_initializer_argument(self) -> Asts.ObjectInitializerArgumentAst:
        p1 = self.parse_object_initializer_argument_named()
        p2 = self.parse_object_initializer_argument_unnamed()
        p3 = (p1 | p2).parse_once()
        return p3

    @parser_rule
    def parse_object_initializer_argument_unnamed(self) -> Asts.ObjectInitializerArgumentUnnamedAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.TkDblDot).parse_optional()
        p2 = self.parse_identifier().parse_once()
        return Asts.ObjectInitializerArgumentUnnamedAst(c1, p1, p2)

    @parser_rule
    def parse_object_initializer_argument_named(self) -> Asts.ObjectInitializerArgumentNamedAst:
        c1 = self.current_pos()
        p1 = self.parse_identifier().parse_once()
        p2 = self.parse_token(SppTokenType.TkAssign).parse_once()
        p3 = self.parse_expression().parse_once()
        return Asts.ObjectInitializerArgumentNamedAst(c1, p1, p2, p3)

    # ===== LAMBDAS =====

    # @parser_rule
    # def parse_lambda_prototype(self) -> LambdaPrototypeAst:
    #     c1 = self.current_pos()
    #     p1 = self.parse_token(SppTokenType.KwFun).parse_once()  # todo: allow lambda coroutines
    #     p2 = self.parse_generic_parameters().parse_optional()
    #     p3 = self.parse_function_parameters().parse_once()
    #     p4 = self.parse_token(SppTokenType.TkArrowR).parse_once()
    #     p5 = self.parse_type().parse_once()
    #     p6 = self.parse_lambda_capture_block().parse_optional()
    #     p7 = self.parse_where_block().parse_optional()
    #     p8 = self.parse_inner_scope().parse_once()
    #     return LambdaPrototypeAst(c1, p1, p2, p3, p4, p5, p6, p7, p8)
    #
    # @parser_rule
    # def parse_lambda_capture_block(self) -> LambdaCaptureBlockAst:
    #     c1 = self.current_pos()
    #     p1 = self.parse_token(SppTokenType.TkBrackL).parse_once()
    #     p2 = self.parse_lambda_capture_item().parse_zero_or_more(SppTokenType.TkComma)
    #     p3 = self.parse_token(SppTokenType.TkBrackR).parse_once()
    #     return LambdaCaptureBlockAst(c1, p1, p2, p3)
    #
    # @parser_rule
    # def parse_lambda_capture_item(self) -> LambdaCaptureItemAst:
    #     p1 = self.parse_lambda_capture_item_named()
    #     p2 = self.parse_lambda_capture_item_normal()
    #     p3 = (p1 | p2).parse_once()
    #     return p3
    #
    # @parser_rule
    # def parse_lambda_capture_item_normal(self) -> LambdaCaptureItemNormalAst:
    #     c1 = self.current_pos()
    #     p1 = self.parse_convention().parse_once()
    #     p2 = self.parse_expression().parse_once()
    #     return LambdaCaptureItemNormalAst(c1, p1, p2)
    #
    # @parser_rule
    # def parse_lambda_capture_item_named(self) -> LambdaCaptureItemNamedAst:
    #     c1 = self.current_pos()
    #     p1 = self.parse_identifier().parse_once()
    #     p2 = self.parse_token(SppTokenType.TkAssign).parse_once()
    #     p3 = self.parse_convention().parse_once()
    #     p4 = self.parse_expression().parse_once()
    #     return LambdaCaptureItemNamedAst(c1, p1, p2, p3, p4)

    # ===== TYPES =====

    @parser_rule
    def parse_type(self) -> Asts.TypeAst:
        p1 = self.parse_type_optional()
        p2 = self.parse_type_variant()
        p3 = self.parse_type_tuple()
        p4 = self.parse_type_single()
        p5 = (p1 | p2 | p3 | p4).parse_once()
        return p5

    @parser_rule
    def parse_type_optional(self) -> Asts.TypeAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.TkQst).parse_once()
        p2 = self.parse_type().parse_once()
        return Asts.TypeOptionalAst(c1, p1, p2).to_type()

    @parser_rule
    def parse_type_single(self) -> Asts.TypeAst:
        p1 = self.parse_type_single_with_namespace()
        p2 = self.parse_type_single_with_self()
        p3 = self.parse_type_single_without_namespace_or_self()
        p4 = (p1 | p2 | p3).parse_once()
        return p4

    @parser_rule
    def parse_type_single_with_namespace(self) -> Asts.TypeAst:
        c1 = self.current_pos()
        p1 = self.parse_identifier().parse_one_or_more(SppTokenType.TkDblColon)
        p2 = self.parse_token(SppTokenType.TkDblColon).parse_once()
        p3 = self.parse_generic_identifier().parse_one_or_more(SppTokenType.TkDblColon)
        return Asts.TypeAst(c1, Seq(p1), Seq(p3))

    @parser_rule
    def parse_type_single_with_self(self) -> Asts.TypeAst:
        c1 = self.current_pos()
        p1 = self.parse_self_type_keyword().parse_once()
        p2 = self.parse_types_after_self().parse_optional() or Seq()
        return Asts.TypeAst(c1, Seq(), Seq([p1]) + p2)

    @parser_rule
    def parse_types_after_self(self) -> Seq[Asts.GenericIdentifierAst]:
        p1 = self.parse_token(SppTokenType.TkDblColon)
        p2 = self.parse_generic_identifier().parse_zero_or_more(SppTokenType.TkDblColon)
        return Seq(p2)

    @parser_rule
    def parse_type_single_without_namespace_or_self(self) -> Asts.TypeAst:
        c1 = self.current_pos()
        p1 = self.parse_generic_identifier().parse_one_or_more(SppTokenType.TkDblColon)
        return Asts.TypeAst(c1, Seq(), Seq(p1))

    @parser_rule
    def parse_self_type_keyword(self) -> Asts.GenericIdentifierAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.KwSelfType).parse_once()
        return Asts.GenericIdentifierAst(c1, p1.token.token_metadata)

    @parser_rule
    def parse_type_tuple(self) -> Asts.TypeAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.TkParenL).parse_once()
        p2 = self.parse_type().parse_zero_or_more(SppTokenType.TkComma)
        p3 = self.parse_token(SppTokenType.TkParenR).parse_once()
        return Asts.TypeTupleAst(c1, p1, Seq(p2), p3).to_type()

    @parser_rule
    def parse_type_non_union(self) -> Asts.TypeAst:
        p1 = self.parse_type_single()
        p2 = self.parse_type_tuple()
        p3 = self.parse_type_optional()
        p4 = (p1 | p2 | p3).parse_once()
        return p4

    @parser_rule
    def parse_type_variant(self) -> Asts.TypeAst:
        c1 = self.current_pos()
        p1 = self.parse_type_non_union().parse_two_or_more(SppTokenType.TkUnion)
        return Asts.TypeVariantAst(c1, Seq(p1)).to_type()

    # ===== IDENTIFIERS =====

    @parser_rule
    def parse_identifier(self) -> Asts.IdentifierAst:
        c1 = self.current_pos()
        p1 = self.parse_lexeme(SppTokenType.LxIdentifier).parse_once()
        return Asts.IdentifierAst(c1, p1.token.token_metadata)

    @parser_rule
    def parse_upper_identifier(self) -> Asts.IdentifierAst:
        c1 = self.current_pos()
        p1 = self.parse_lexeme(SppTokenType.LxUpperIdentifier).parse_once()
        return Asts.IdentifierAst(c1, p1.token.token_metadata)

    @parser_rule
    def parse_generic_identifier(self) -> Asts.GenericIdentifierAst:
        c1 = self.current_pos()
        p1 = self.parse_upper_identifier().parse_once()
        p2 = self.parse_generic_arguments().parse_optional() or Asts.GenericArgumentGroupAst(pos=c1)
        return Asts.GenericIdentifierAst(c1, p1.value, p2)

    # ===== LITERALS =====

    @parser_rule
    def parse_literal(self) -> Asts.LiteralAst:
        p1 = self.parse_literal_float()
        p2 = self.parse_literal_integer()
        p3 = self.parse_literal_string()
        p4 = self.parse_literal_tuple(self.parse_expression)
        p5 = self.parse_literal_array(self.parse_expression)
        p6 = self.parse_literal_boolean()
        p7 = (p1 | p2 | p3 | p4 | p5 | p6).parse_once()
        return p7

    @parser_rule
    def parse_literal_float(self) -> Asts.FloatLiteralAst:
        p1 = self.parse_literal_float_b10().parse_once()
        return p1

    @parser_rule
    def parse_literal_integer(self) -> Asts.IntegerLiteralAst:
        p1 = self.parse_literal_integer_b10()
        p2 = self.parse_literal_integer_b02()
        p3 = self.parse_literal_integer_b16()
        p4 = (p1 | p2 | p3).parse_once()
        return p4

    @parser_rule
    def parse_literal_string(self) -> Asts.StringLiteralAst:
        c1 = self.current_pos()
        p1 = self.parse_lexeme(SppTokenType.LxDoubleQuoteStr).parse_once()
        return Asts.StringLiteralAst(c1, p1)

    @parser_rule
    def parse_literal_tuple(self, item=None) -> Asts.TupleLiteralAst:
        p1 = self.parse_literal_tuple_0_items()
        p2 = self.parse_literal_tuple_1_items(item or self.parse_expression)
        p3 = self.parse_literal_tuple_n_items(item or self.parse_expression)
        p4 = (p1 | p2 | p3).parse_once()
        return p4

    @parser_rule
    def parse_literal_array(self, item) -> Asts.ArrayLiteralAst:
        p1 = self.parse_literal_array_0_items()
        p2 = self.parse_literal_array_n_items(item)
        p3 = (p1 | p2).parse_once()
        return p3

    @parser_rule
    def parse_literal_boolean(self) -> Asts.BooleanLiteralAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.KwTrue)
        p2 = self.parse_token(SppTokenType.KwFalse)
        p3 = (p1 | p2).parse_once()
        return Asts.BooleanLiteralAst(c1, p3)

    # ===== NUMBERS =====

    @parser_rule
    def parse_literal_float_b10(self) -> Asts.FloatLiteralAst:
        c1 = self.current_pos()
        p1 = self.parse_numeric_prefix_op().parse_optional()
        p2 = self.parse_lexeme(SppTokenType.LxDecInteger).parse_once()
        p3 = self.parse_token(SppTokenType.TkDot).parse_once()
        p4 = self.parse_lexeme(SppTokenType.LxDecInteger).parse_once()
        p5 = self.parse_float_postfix_type().parse_optional()
        return Asts.FloatLiteralAst(c1, p1, p2, p3, p4, p5)

    @parser_rule
    def parse_literal_integer_b10(self) -> Asts.IntegerLiteralAst:
        c1 = self.current_pos()
        p1 = self.parse_numeric_prefix_op().parse_optional()
        p2 = self.parse_lexeme(SppTokenType.LxDecInteger).parse_once()
        p3 = self.parse_integer_postfix_type().parse_optional()
        return Asts.IntegerLiteralAst(c1, p1, p2, Asts.TypeAst.from_identifier(p3) if p3 else p3)

    @parser_rule
    def parse_literal_integer_b02(self) -> Asts.IntegerLiteralAst:
        c1 = self.current_pos()
        p1 = self.parse_numeric_prefix_op().parse_optional()
        p2 = self.parse_lexeme(SppTokenType.LxBinDigits).parse_once()
        p3 = self.parse_integer_postfix_type().parse_optional()
        return Asts.IntegerLiteralAst(c1, p1, p2, p3)

    @parser_rule
    def parse_literal_integer_b16(self) -> Asts.IntegerLiteralAst:
        c1 = self.current_pos()
        p1 = self.parse_numeric_prefix_op().parse_optional()
        p2 = self.parse_lexeme(SppTokenType.LxHexDigits).parse_once()
        p3 = self.parse_integer_postfix_type().parse_optional()
        return Asts.IntegerLiteralAst(c1, p1, p2, p3)

    @parser_rule
    def parse_numeric_prefix_op(self) -> Asts.TokenAst:
        p1 = self.parse_token(SppTokenType.TkSub)
        p2 = self.parse_token(SppTokenType.TkAdd)
        p3 = (p1 | p2).parse_once()
        return p3

    @parser_rule
    def parse_integer_postfix_type(self) -> SppTokenType:
        p1  = self.parse_token(SppTokenType.TkUnderscore).parse_once()
        p2  = self.parse_characters("i8")
        p3  = self.parse_characters("i16")
        p4  = self.parse_characters("i32")
        p5  = self.parse_characters("i64")
        p6  = self.parse_characters("i128")
        p7  = self.parse_characters("i256")
        p8  = self.parse_characters("u8")
        p9  = self.parse_characters("u16")
        p10 = self.parse_characters("u32")
        p11 = self.parse_characters("u64")
        p12 = self.parse_characters("u128")
        p13 = self.parse_characters("u256")
        p14 = (p2 | p3 | p4 | p5 | p6 | p7 | p8 | p9 | p10 | p11 | p12 | p13).parse_once()
        return p14

    @parser_rule
    def parse_float_postfix_type(self) -> SppTokenType:
        p1 = self.parse_token(SppTokenType.TkUnderscore).parse_once()
        p2 = self.parse_characters("f8")
        p3 = self.parse_characters("f16")
        p4 = self.parse_characters("f32")
        p5 = self.parse_characters("f64")
        p6 = self.parse_characters("f128")
        p7 = self.parse_characters("f256")
        p8 = (p2 | p3 | p4 | p5 | p6 | p7).parse_once()
        return p8

    # ===== TUPLES =====

    @parser_rule
    def parse_literal_tuple_0_items(self) -> Asts.TupleLiteralAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.TkParenL).parse_once()
        p2 = self.parse_token(SppTokenType.TkParenR).parse_once()
        return Asts.TupleLiteralAst(c1, p1, Seq(), p2)

    @parser_rule
    def parse_literal_tuple_1_items(self, item) -> Asts.TupleLiteralAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.TkParenL).parse_once()
        p2 = item().parse_once()
        p3 = self.parse_token(SppTokenType.TkComma).parse_once()
        p4 = self.parse_token(SppTokenType.TkParenR).parse_once()
        return Asts.TupleLiteralAst(c1, p1, Seq([p2]), p4)

    @parser_rule
    def parse_literal_tuple_n_items(self, item) -> Asts.TupleLiteralAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.TkParenL).parse_once()
        p2 = item().parse_two_or_more(SppTokenType.TkComma)
        p3 = self.parse_token(SppTokenType.TkParenR).parse_once()
        return Asts.TupleLiteralAst(c1, p1, Seq(p2), p3)

    # ===== ARRAYS =====

    @parser_rule
    def parse_literal_array_0_items(self) -> Asts.ArrayLiteral0ElementAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.TkBrackL).parse_once()
        p2 = self.parse_type().parse_once()
        p3 = self.parse_token(SppTokenType.TkComma).parse_once()
        p4 = self.parse_lexeme(SppTokenType.LxDecInteger).parse_once()
        p5 = self.parse_token(SppTokenType.TkBrackR).parse_once()
        return Asts.ArrayLiteral0ElementAst(c1, p1, p2, p3, p4, p5)

    @parser_rule
    def parse_literal_array_n_items(self, item) -> Asts.ArrayLiteralNElementAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.TkBrackL).parse_once()
        p2 = item().parse_one_or_more(SppTokenType.TkComma)
        p3 = self.parse_token(SppTokenType.TkBrackR).parse_once()
        return Asts.ArrayLiteralNElementAst(c1, p1, Seq(p2), p3)

    # ===== GLOBAL CONSTANTS =====

    @parser_rule
    def parse_global_constant_value(self) -> Asts.ExpressionAst:
        p1 = self.parse_literal_float()
        p2 = self.parse_literal_integer()
        p3 = self.parse_literal_string()
        p4 = self.parse_literal_tuple(self.parse_global_constant_value)
        p5 = self.parse_literal_array(self.parse_global_constant_value)
        p6 = self.parse_literal_boolean()
        p7 = self.parse_global_object_initializer()
        p8 = self.parse_identifier()
        p9 = (p1 | p2 | p3 | p4 | p5 | p6 | p7 | p8).parse_once()
        return p9

    @parser_rule
    def parse_global_object_initializer(self) -> Asts.ObjectInitializerAst:
        c1 = self.current_pos()
        p1 = self.parse_type_single().parse_once()
        p2 = self.parse_global_object_initializer_arguments().parse_once()
        return Asts.ObjectInitializerAst(c1, p1, p2)

    @parser_rule
    def parse_global_object_initializer_arguments(self) -> Asts.ObjectInitializerArgumentGroupAst:
        c1 = self.current_pos()
        p1 = self.parse_token(SppTokenType.TkParenL).parse_once()
        p2 = self.parse_global_object_initializer_argument_named().parse_zero_or_more(SppTokenType.TkComma)  # todo: normal too for copyables?
        p3 = self.parse_token(SppTokenType.TkParenR).parse_once()
        return Asts.ObjectInitializerArgumentGroupAst(c1, p1, Seq(p2), p3)

    @parser_rule
    def parse_global_object_initializer_argument_named(self) -> Asts.ObjectInitializerArgumentNamedAst:
        c1 = self.current_pos()
        p1 = self.parse_identifier().parse_once()
        p2 = self.parse_token(SppTokenType.TkAssign).parse_once()
        p3 = self.parse_global_constant_value().parse_once()
        return Asts.ObjectInitializerArgumentNamedAst(c1, p1, p2, p3)

    # ===== TOKENS, KEYWORDS, & LEXEMES =====

    @parser_rule
    def parse_lexeme(self, lexeme: SppTokenType) -> Asts.TokenAst:
        p1 = self.parse_token(lexeme).parse_once()
        return p1

    @parser_rule
    def parse_characters(self, characters: str) -> Asts.TokenAst:
        # TODO : these rules don't come up u the error for failed alternate parsing (see number postfix types)

        p1 = self.parse_identifier().parse_once()
        if p1.value == characters:
            return p1
        else:
            new_error = f"Expected '{characters}', got '{p1.value}'"
            self.store_error(self.current_pos(), new_error)
            raise self._error

    @parser_rule
    def parse_token(self, token_type: SppTokenType) -> Asts.TokenAst:
        token = super().parse_token(token_type).parse_once()
        return Asts.TokenAst(token.pos, token.token)


__all__ = ["Parser", "parser_rule"]
