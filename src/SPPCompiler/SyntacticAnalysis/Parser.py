from __future__ import annotations
from typing import Callable, List, Optional, Tuple, TYPE_CHECKING
import functools

from SPPCompiler.LexicalAnalysis.Token import Token
from SPPCompiler.LexicalAnalysis.TokenType import TokenType
from SPPCompiler.SyntacticAnalysis.ParserRuleHandler import ParserRuleHandler
from SPPCompiler.SemanticAnalysis import *

if TYPE_CHECKING:
    from SPPCompiler.SyntacticAnalysis.Errors.ParserError import ParserError, ParserErrors
    from SPPCompiler.Utils.ErrorFormatter import ErrorFormatter


# Todo: add newlines after multi-expression/statement blocks (ie between multiple ret/gen/let etc)


# Decorator that wraps the function in a ParserRuleHandler
def parser_rule(func) -> Callable[..., ParserRuleHandler]:
    @functools.wraps(func)
    @functools.cache
    def wrapper(self, *args) -> ParserRuleHandler:
        return ParserRuleHandler(self, functools.partial(func, self, *args))
    return wrapper


class Parser:
    _tokens: List[Token]
    _name: str
    _index: int
    _err_fmt: ErrorFormatter
    _error: Optional[ParserErrors.SyntaxError]

    def __init__(self, tokens: List[Token], file_name: str = "", error_formatter: Optional[ErrorFormatter] = None) -> None:
        from SPPCompiler.SyntacticAnalysis.Errors.ParserError import ParserErrors
        from SPPCompiler.Utils.ErrorFormatter import ErrorFormatter

        self._tokens = tokens
        self._name = file_name
        self._index = 0
        self._err_fmt = error_formatter or ErrorFormatter(self._tokens, file_name)
        self._error = ParserErrors.SyntaxError()

    def current_pos(self) -> int:
        return self._index

    def current_tok(self) -> Token:
        return self._tokens[self._index]

    # ===== PARSING =====

    def parse(self) -> ProgramAst:
        from SPPCompiler.SyntacticAnalysis.Errors.ParserError import ParserError

        try:
            ast = self.parse_module_prototype().parse_once()
            return ast

        except ParserError as e:
            e.throw(self._err_fmt)

    # ===== PROGRAM =====

    @parser_rule
    def parse_eof(self) -> TokenAst:
        p1 = self.parse_token(TokenType.TkEOF).parse_once()
        return p1

    # ===== MODULES =====

    @parser_rule
    def parse_module_prototype(self) -> ModulePrototypeAst:
        c1 = self.current_pos()
        p1 = self.parse_module_implementation().parse_once()
        p2 = self.parse_eof().parse_once()
        return ModulePrototypeAst(c1, p1, p2)

    @parser_rule
    def parse_module_implementation(self) -> ModuleImplementationAst:
        c1 = self.current_pos()
        p1 = self.parse_module_member().parse_zero_or_more(TokenType.NO_TOK)
        return ModuleImplementationAst(c1, p1)

    @parser_rule
    def parse_module_member(self) -> ModuleMemberAst:
        p1 = self.parse_function_prototype()
        p2 = self.parse_class_prototype()
        p3 = self.parse_sup_prototype_inheritance()
        p4 = self.parse_sup_prototype_functions()
        p5 = self.parse_global_use_statement()
        p6 = self.parse_global_constant()
        p7 = (p1 | p2 | p3 | p4 | p5 | p6).parse_once()
        return p7

    # ===== CLASSES =====

    @parser_rule
    def parse_class_prototype(self) -> ClassPrototypeAst:
        c1 = self.current_pos()
        p1 = self.parse_annotation().parse_zero_or_more(TokenType.TkNewLine)
        p2 = self.parse_token(TokenType.KwCls).parse_once()
        p3 = self.parse_upper_identifier().parse_once()
        p4 = self.parse_generic_parameters().parse_optional()
        p5 = self.parse_where_block().parse_optional()
        p6 = self.parse_class_implementation().parse_once()
        return ClassPrototypeAst(c1, p1, p2, p3, p4, p5, p6)

    @parser_rule
    def parse_class_implementation(self) -> ClassImplementationAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.TkBraceL).parse_once()
        p2 = self.parse_class_member().parse_zero_or_more(TokenType.NO_TOK)
        p3 = self.parse_token(TokenType.TkBraceR).parse_once()
        return ClassImplementationAst(c1, p1, p2, p3)

    @parser_rule
    def parse_class_member(self) -> ClassMemberAst:
        p1 = self.parse_class_attribute().parse_once()
        return p1

    @parser_rule
    def parse_class_attribute(self) -> ClassAttributeAst:
        c1 = self.current_pos()
        p1 = self.parse_annotation().parse_zero_or_more(TokenType.TkNewLine)
        p2 = self.parse_identifier().parse_once()
        p3 = self.parse_token(TokenType.TkColon).parse_once()
        p4 = self.parse_type().parse_once()
        return ClassAttributeAst(c1, p1, p2, p3, p4)

    # ===== SUPERIMPOSITION =====

    @parser_rule
    def parse_sup_prototype_functions(self) -> SupPrototypeFunctionsAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.KwSup).parse_once()
        p2 = self.parse_generic_parameters().parse_optional()
        p3 = self.parse_type().parse_once()
        p4 = self.parse_where_block().parse_optional()
        p5 = self.parse_sup_implementation().parse_once()
        return SupPrototypeFunctionsAst(c1, p1, p2, p3, p4, p5)

    @parser_rule
    def parse_sup_prototype_inheritance(self) -> SupPrototypeInheritanceAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.KwSup).parse_once()
        p2 = self.parse_generic_parameters().parse_optional()
        p3 = self.parse_type().parse_once()
        p4 = self.parse_token(TokenType.KwExt).parse_once()
        p5 = self.parse_type().parse_once()
        p6 = self.parse_where_block().parse_optional()
        p7 = self.parse_sup_implementation().parse_once()
        return SupPrototypeInheritanceAst(c1, p1, p2, p3, p6, p7, p4, p5)

    @parser_rule
    def parse_sup_implementation(self) -> SupImplementationAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.TkBraceL).parse_once()
        p2 = self.parse_sup_member().parse_zero_or_more(TokenType.NO_TOK)
        p3 = self.parse_token(TokenType.TkBraceR).parse_once()
        return SupImplementationAst(c1, p1, p2, p3)

    @parser_rule
    def parse_sup_member(self) -> SupMemberAst:
        p1 = self.parse_sup_method_prototype()
        p2 = self.parse_sup_use_statement()
        p3 = (p1 | p2).parse_once()
        return p3

    @parser_rule
    def parse_sup_use_statement(self) -> SupUseStatementAst:
        p1 = self.parse_annotation().parse_zero_or_more(TokenType.TkNewLine)
        p2 = self.parse_use_statement().parse_once()
        return SupUseStatementAst(**p2.__dict__, annotations=p1)

    @parser_rule
    def parse_sup_method_prototype(self) -> FunctionPrototypeAst:
        p1 = self.parse_function_prototype().parse_once()
        return p1

    # ===== FUNCTIONS =====

    @parser_rule
    def parse_function_prototype(self) -> FunctionPrototypeAst:
        p1 = self.parse_subroutine_prototype()
        p2 = self.parse_coroutine_prototype()
        p3 = (p1 | p2).parse_once()
        return p3

    @parser_rule
    def parse_subroutine_prototype(self) -> SubroutinePrototypeAst:
        c1 = self.current_pos()
        p1 = self.parse_annotation().parse_zero_or_more(TokenType.TkNewLine)
        p2 = self.parse_token(TokenType.KwFun).parse_once()
        p3 = self.parse_identifier().parse_once()
        p4 = self.parse_generic_parameters().parse_optional()
        p5 = self.parse_function_parameters().parse_once()
        p6 = self.parse_token(TokenType.TkArrowR).parse_once()
        p7 = self.parse_type().parse_once()
        p8 = self.parse_where_block().parse_optional()
        p9 = self.parse_function_implementation().parse_once()
        return SubroutinePrototypeAst(c1, p1, p2, p3, p4, p5, p6, p7, p8, p9)

    @parser_rule
    def parse_coroutine_prototype(self) -> CoroutinePrototypeAst:
        c1 = self.current_pos()
        p1 = self.parse_annotation().parse_zero_or_more(TokenType.TkNewLine)
        p2 = self.parse_token(TokenType.KwCor).parse_once()
        p3 = self.parse_identifier().parse_once()
        p4 = self.parse_generic_parameters().parse_optional()
        p5 = self.parse_function_parameters().parse_once()
        p6 = self.parse_token(TokenType.TkArrowR).parse_once()
        p7 = self.parse_type().parse_once()
        p8 = self.parse_where_block().parse_optional()
        p9 = self.parse_function_implementation().parse_once()
        return CoroutinePrototypeAst(c1, p1, p2, p3, p4, p5, p6, p7, p8, p9)

    @parser_rule
    def parse_function_implementation(self) -> FunctionImplementationAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.TkBraceL).parse_once()
        p2 = self.parse_function_member().parse_zero_or_more(TokenType.NO_TOK)
        p3 = self.parse_token(TokenType.TkBraceR).parse_once()
        return FunctionImplementationAst(c1, p1, p2, p3)

    @parser_rule
    def parse_function_member(self) -> FunctionMemberAst:
        p1 = self.parse_statement().parse_once()
        return p1

    @parser_rule
    def parse_function_call_arguments(self) -> FunctionCallArgumentGroupAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.TkParenL).parse_once()
        p2 = self.parse_function_call_argument().parse_zero_or_more(TokenType.TkComma)
        p4 = self.parse_token(TokenType.TkParenR).parse_once()
        return FunctionCallArgumentGroupAst(c1, p1, p2, p4)

    @parser_rule
    def parse_function_call_argument(self) -> FunctionCallArgumentAst:
        p1 = self.parse_function_call_argument_named()
        p2 = self.parse_function_call_argument_unnamed()
        p3 = (p1 | p2).parse_once()
        return p3

    @parser_rule
    def parse_function_call_argument_unnamed(self) -> FunctionCallArgumentUnnamedAst:
        c1 = self.current_pos()
        p1 = self.parse_convention().parse_once()
        p2 = self.parse_token(TokenType.TkVariadic).parse_optional()
        p3 = self.parse_expression().parse_once()
        return FunctionCallArgumentUnnamedAst(c1, p1, p2, p3)

    @parser_rule
    def parse_function_call_argument_named(self) -> FunctionCallArgumentNamedAst:
        c1 = self.current_pos()
        p1 = self.parse_identifier().parse_once()
        p2 = self.parse_token(TokenType.TkAssign).parse_once()
        p3 = self.parse_convention().parse_once()
        p4 = self.parse_expression().parse_once()
        return FunctionCallArgumentNamedAst(c1, p1, p2, p3, p4)

    @parser_rule
    def parse_function_parameters(self) -> FunctionParameterGroupAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.TkParenL).parse_once()
        p2 = self.parse_function_parameter().parse_zero_or_more(TokenType.TkComma)
        p3 = self.parse_token(TokenType.TkParenR).parse_once()
        return FunctionParameterGroupAst(c1, p1, p2, p3)

    @parser_rule
    def parse_function_parameter(self) -> FunctionParameterAst:
        p1 = self.parse_function_parameter_variadic()
        p2 = self.parse_function_parameter_optional()
        p3 = self.parse_function_parameter_required()
        p4 = self.parse_function_parameter_self()
        p5 = (p1 | p2 | p3 | p4).parse_once()
        return p5

    @parser_rule
    def parse_function_parameter_self(self) -> FunctionParameterSelfAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.KwMut).parse_optional()
        p2 = self.parse_convention().parse_once()
        p3 = self.parse_self_keyword().parse_once()
        return FunctionParameterSelfAst(c1, p1, p2, p3)

    @parser_rule
    def parse_function_parameter_required(self) -> FunctionParameterRequiredAst:
        c1 = self.current_pos()
        p1 = self.parse_local_variable().parse_once()
        p2 = self.parse_token(TokenType.TkColon).parse_once()
        p3 = self.parse_convention().parse_once()
        p4 = self.parse_type().parse_once()
        return FunctionParameterRequiredAst(c1, p1, p2, p3, p4)

    @parser_rule
    def parse_function_parameter_optional(self) -> FunctionParameterOptionalAst:
        c1 = self.current_pos()
        p1 = self.parse_local_variable().parse_once()
        p2 = self.parse_token(TokenType.TkColon).parse_once()
        p3 = self.parse_convention().parse_once()
        p4 = self.parse_type().parse_once()
        p5 = self.parse_token(TokenType.TkAssign).parse_once()
        p6 = self.parse_expression().parse_once()
        return FunctionParameterOptionalAst(c1, p1, p2, p3, p4, p5, p6)

    @parser_rule
    def parse_function_parameter_variadic(self) -> FunctionParameterVariadicAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.TkVariadic).parse_once()
        p2 = self.parse_local_variable().parse_once()
        p3 = self.parse_token(TokenType.TkColon).parse_once()
        p4 = self.parse_convention().parse_once()
        p5 = self.parse_type().parse_once()
        return FunctionParameterVariadicAst(c1, p1, p2, p3, p4, p5)

    # ===== GENERICS =====

    @parser_rule
    def parse_generic_arguments(self) -> GenericArgumentGroupAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.TkBrackL).parse_once()
        p2 = self.parse_generic_argument().parse_one_or_more(TokenType.TkComma)
        p3 = self.parse_token(TokenType.TkBrackR).parse_once()
        return GenericArgumentGroupAst(c1, p1, p2, p3)

    @parser_rule
    def parse_generic_argument(self) -> GenericArgumentAst:
        p1 = self.parse_generic_type_argument_named()
        p2 = self.parse_generic_type_argument_unnamed()
        p3 = self.parse_generic_comp_argument_named()
        p4 = self.parse_generic_comp_argument_unnamed()
        p5 = (p1 | p2 | p3 | p4).parse_once()
        return p5

    @parser_rule
    def parse_generic_type_argument_named(self) -> GenericTypeArgumentNamedAst:
        c1 = self.current_pos()
        p1 = self.parse_upper_identifier().parse_once()
        p2 = self.parse_token(TokenType.TkAssign).parse_once()
        p3 = self.parse_type().parse_once()
        return GenericTypeArgumentNamedAst(c1, p1, p2, p3)

    @parser_rule
    def parse_generic_type_argument_unnamed(self) -> GenericTypeArgumentUnnamedAst:
        c1 = self.current_pos()
        p1 = self.parse_type().parse_once()
        return GenericTypeArgumentUnnamedAst(c1, p1)

    @parser_rule
    def parse_generic_comp_argument_named(self) -> GenericCompArgumentNamedAst:
        c1 = self.current_pos()
        p1 = self.parse_identifier().parse_once()
        p2 = self.parse_token(TokenType.TkAssign).parse_once()
        p3 = self.parse_global_constant_value().parse_once()
        return GenericCompArgumentNamedAst(c1, p1, p2, p3)

    @parser_rule
    def parse_generic_comp_argument_unnamed(self) -> GenericCompArgumentUnnamedAst:
        c1 = self.current_pos()
        p1 = self.parse_global_constant_value().parse_once()
        return GenericCompArgumentUnnamedAst(c1, p1)

    @parser_rule
    def parse_generic_parameters(self) -> GenericParameterGroupAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.TkBrackL).parse_once()
        p2 = self.parse_generic_parameter().parse_one_or_more(TokenType.TkComma)
        p3 = self.parse_token(TokenType.TkBrackR).parse_once()
        return GenericParameterGroupAst(c1, p1, p2, p3)

    @parser_rule
    def parse_generic_parameter(self) -> GenericParameterAst:
        p1 = self.parse_generic_comp_parameter_variadic()
        p2 = self.parse_generic_comp_parameter_optional()
        p3 = self.parse_generic_comp_parameter_required()
        p4 = self.parse_generic_type_parameter_variadic()
        p5 = self.parse_generic_type_parameter_optional()
        p6 = self.parse_generic_type_parameter_required()
        p7 = (p1 | p2 | p3 | p4 | p5 | p6).parse_once()
        return p7

    @parser_rule
    def parse_generic_type_parameter_required(self) -> GenericTypeParameterRequiredAst:
        c1 = self.current_pos()
        p1 = self.parse_upper_identifier().parse_once()
        p2 = self.parse_generic_inline_constraints().parse_optional()
        return GenericTypeParameterRequiredAst(c1, p1, p2)

    @parser_rule
    def parse_generic_type_parameter_optional(self) -> GenericTypeParameterOptionalAst:
        c1 = self.current_pos()
        p1 = self.parse_upper_identifier().parse_once()
        p2 = self.parse_generic_inline_constraints().parse_optional()
        p3 = self.parse_token(TokenType.TkAssign).parse_once()
        p4 = self.parse_type().parse_once()
        return GenericTypeParameterOptionalAst(c1, p1, p2, p3, p4)

    @parser_rule
    def parse_generic_type_parameter_variadic(self) -> GenericTypeParameterVariadicAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.TkVariadic).parse_once()
        p2 = self.parse_upper_identifier().parse_once()
        p3 = self.parse_generic_inline_constraints().parse_optional()
        return GenericTypeParameterVariadicAst(c1, p1, p2, p3)

    @parser_rule
    def parse_generic_comp_parameter_required(self) -> GenericCompParameterRequiredAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.KwCmp).parse_once()
        p2 = self.parse_identifier().parse_once()
        p3 = self.parse_token(TokenType.TkColon).parse_once()
        p4 = self.parse_type().parse_once()
        return GenericCompParameterRequiredAst(c1, p1, p2, p3, p4)

    @parser_rule
    def parse_generic_comp_parameter_optional(self) -> GenericCompParameterOptionalAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.KwCmp).parse_once()
        p2 = self.parse_identifier().parse_once()
        p3 = self.parse_token(TokenType.TkColon).parse_once()
        p4 = self.parse_type().parse_once()
        p5 = self.parse_token(TokenType.TkAssign).parse_once()
        p6 = self.parse_global_constant_value().parse_once()
        return GenericCompParameterOptionalAst(c1, p1, p2, p3, p4, p5, p6)

    @parser_rule
    def parse_generic_comp_parameter_variadic(self) -> GenericCompParameterVariadicAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.KwCmp).parse_once()
        p2 = self.parse_token(TokenType.TkVariadic).parse_once()
        p3 = self.parse_identifier().parse_once()
        p4 = self.parse_token(TokenType.TkColon).parse_once()
        p5 = self.parse_type().parse_once()
        return GenericCompParameterVariadicAst(c1, p1, p2, p3, p4, p5)

    @parser_rule
    def parse_generic_inline_constraints(self) -> GenericTypeParameterInlineConstraintsAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.TkColon).parse_once()
        p2 = self.parse_type().parse_one_or_more(TokenType.TkComma)
        return GenericTypeParameterInlineConstraintsAst(c1, p1, p2)

    # ===== WHERE =====

    @parser_rule
    def parse_where_block(self) -> WhereBlockAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.KwWhere).parse_once()
        p2 = self.parse_where_block_constraints_group().parse_once()
        return WhereBlockAst(c1, p1, p2)

    @parser_rule
    def parse_where_block_constraints_group(self) -> WhereConstraintsGroupAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.TkBrackL).parse_once()
        p2 = self.parse_where_block_constraints().parse_one_or_more(TokenType.TkComma)
        p3 = self.parse_token(TokenType.TkBrackR).parse_once()
        return WhereConstraintsGroupAst(c1, p1, p2, p3)

    @parser_rule
    def parse_where_block_constraints(self) -> WhereConstraintsAst:
        c1 = self.current_pos()
        p1 = self.parse_type().parse_one_or_more(TokenType.TkComma)
        p2 = self.parse_token(TokenType.TkColon).parse_once()
        p3 = self.parse_type().parse_once()
        return WhereConstraintsAst(c1, p1, p2, p3)

    # ===== ANNOTATIONS =====

    @parser_rule
    def parse_annotation(self) -> AnnotationAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.TkAt).parse_once()
        p2 = self.parse_identifier().parse_once()
        return AnnotationAst(c1, p1, p2)

    # ===== EXPRESSIONS =====

    @parser_rule
    def parse_expression(self) -> ExpressionAst:
        p1 = self.parse_binary_expression_precedence_level_1().parse_once()
        return p1

    @parser_rule
    def parse_binary_expression_precedence_level_n_rhs(self, op, rhs) -> Tuple[TokenAst, ExpressionAst]:
        p1 = op().parse_once()
        p2 = rhs().parse_once()
        return p1, p2

    @parser_rule
    def parse_binary_expression_precedence_level_n(self, lhs, op, rhs) -> BinaryExpressionAst:
        c1 = self.current_pos()
        p1 = lhs().parse_once()
        p2 = self.parse_binary_expression_precedence_level_n_rhs(op, rhs).parse_optional()
        return BinaryExpressionAst(c1, p1, p2[0], p2[1]) if p2 else p1

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
            self.parse_pattern_variant_object_destructure)

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
    def parse_unary_expression(self) -> ExpressionAst:
        c1 = self.current_pos()
        p1 = self.parse_unary_op().parse_zero_or_more(TokenType.NO_TOK)
        p2 = self.parse_postfix_expression().parse_once()
        return functools.reduce(lambda acc, x: UnaryExpressionAst(c1, x, acc), p1, p2)

    @parser_rule
    def parse_postfix_expression(self) -> ExpressionAst:
        c1 = self.current_pos()
        p1 = self.parse_primary_expression().parse_once()
        p2 = self.parse_postfix_op().parse_zero_or_more(TokenType.NO_TOK)
        return functools.reduce(lambda acc, x: PostfixExpressionAst(c1, acc, x), p2, p1)

    @parser_rule
    def parse_primary_expression(self) -> ExpressionAst:
        p1 = self.parse_literal()
        p2 = self.parse_object_initialization()
        # p3 = self.parse_lambda_prototype()
        p4 = self.parse_parenthesized_expression()
        p5 = self.parse_type()
        p6 = self.parse_identifier()
        p7 = self.parse_case_expression()
        p8 = self.parse_loop_expression()
        p9 = self.parse_gen_expression()
        p10 = self.parse_with_expression()
        p11 = self.parse_inner_scope(self.parse_statement)
        p12 = self.parse_self_keyword()
        p13 = self.parse_token(TokenType.TkVariadic)
        p14 = (p1 | p2 | p4 | p5 | p6 | p7 | p8 | p9 | p10 | p11 | p12 | p13).parse_once()
        return p14

    @parser_rule
    def parse_parenthesized_expression(self) -> ParenthesizedExpressionAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.TkParenL).parse_once()
        p2 = self.parse_expression().parse_once()
        p3 = self.parse_token(TokenType.TkParenR).parse_once()
        return ParenthesizedExpressionAst(c1, p1, p2, p3)

    @parser_rule
    def parse_self_keyword(self) -> IdentifierAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.KwSelf).parse_once()
        return IdentifierAst(c1, p1.token.token_metadata)

    # ===== EXPRESSION STATEMENTS =====

    @parser_rule
    def parse_case_expression(self) -> CaseExpressionAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.KwCase).parse_once()
        p2 = self.parse_expression().parse_once()
        p3 = self.parse_token(TokenType.KwThen).parse_optional()
        p4 = self.parse_case_expression_branch().parse_one_or_more(TokenType.NO_TOK)
        return CaseExpressionAst(c1, p1, p2, p3, p4)

    @parser_rule
    def parse_loop_expression(self) -> LoopExpressionAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.KwLoop).parse_once()
        p2 = self.parse_loop_expression_condition().parse_once()
        p3 = self.parse_inner_scope(self.parse_statement).parse_once()
        p4 = self.parse_loop_else_statement().parse_optional()
        return LoopExpressionAst(c1, p1, p2, p3, p4)

    @parser_rule
    def parse_loop_expression_condition(self) -> LoopConditionAst:
        p1 = self.parse_loop_expression_condition_iterable()
        p2 = self.parse_loop_expression_condition_boolean()
        p3 = (p1 | p2).parse_once()
        return p3

    @parser_rule
    def parse_loop_expression_condition_boolean(self) -> LoopConditionBooleanAst:
        c1 = self.current_pos()
        p1 = self.parse_expression().parse_once()
        return LoopConditionBooleanAst(c1, p1)

    @parser_rule
    def parse_loop_expression_condition_iterable(self) -> LoopConditionIterableAst:
        c1 = self.current_pos()
        p1 = self.parse_local_variable().parse_once()
        p2 = self.parse_token(TokenType.KwIn).parse_once()
        p3 = self.parse_expression().parse_once()
        return LoopConditionIterableAst(c1, p1, p2, p3)

    @parser_rule
    def parse_loop_else_statement(self) -> LoopElseStatementAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.KwElse).parse_once()
        p2 = self.parse_inner_scope(self.parse_statement).parse_once()
        return LoopElseStatementAst(c1, p1, p2)

    @parser_rule
    def parse_gen_expression(self) -> GenExpressionAst:
        p1 = self.parse_gen_expression_unroll()
        p2 = self.parse_gen_expression_normal()
        p3 = (p1 | p2).parse_once()
        return p3

    @parser_rule
    def parse_gen_expression_normal(self) -> GenExpressionAst:
        p1 = self.parse_gen_expression_normal_with_expression()
        p2 = self.parse_gen_expression_normal_no_expression()
        p3 = (p1 | p2).parse_once()
        return p3

    @parser_rule
    def parse_gen_expression_normal_no_expression(self) -> GenExpressionAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.KwGen).parse_once()
        return GenExpressionAst(c1, p1, None, None, None)

    @parser_rule
    def parse_gen_expression_normal_with_expression(self) -> GenExpressionAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.KwGen).parse_once()
        p2 = self.parse_convention().parse_once()
        p3 = self.parse_expression().parse_once()
        return GenExpressionAst(c1, p1, None, p2, p3)

    @parser_rule
    def parse_gen_expression_unroll(self) -> GenExpressionAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.KwGen).parse_once()
        p2 = self.parse_token(TokenType.KwWith).parse_once()
        p3 = self.parse_expression().parse_once()
        return GenExpressionAst(c1, p1, p2, None, p3)

    @parser_rule
    def parse_with_expression(self) -> WithExpressionAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.KwWith).parse_once()
        p2 = self.parse_with_expression_lhs_alias().parse_optional()
        p3 = self.parse_expression().parse_once()
        p4 = self.parse_inner_scope(self.parse_statement).parse_once()
        return WithExpressionAst(c1, p1, p2, p3, p4)

    @parser_rule
    def parse_with_expression_lhs_alias(self) -> WithExpressionAliasAst:
        c1 = self.current_pos()
        p1 = self.parse_local_variable().parse_once()
        p2 = self.parse_token(TokenType.TkAssign).parse_once()
        return WithExpressionAliasAst(c1, p1, p2)

    # ===== STATEMENTS =====

    @parser_rule
    def parse_ret_statement(self) -> RetStatementAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.KwRet).parse_once()
        p2 = self.parse_expression().parse_optional()
        return RetStatementAst(c1, p1, p2)

    @parser_rule
    def parse_exit_statement(self) -> LoopControlFlowStatementAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.KwExit).parse_one_or_more(TokenType.NO_TOK)
        p2 = self.parse_exit_statement_final_action().parse_optional()
        return LoopControlFlowStatementAst(c1, p1, p2)

    @parser_rule
    def parse_exit_statement_final_action(self) -> TokenAst | ExpressionAst:
        p1 = self.parse_token(TokenType.KwSkip)
        p2 = self.parse_expression()
        p3 = (p1 | p2).parse_once()
        return p3

    @parser_rule
    def parse_skip_statement(self) -> LoopControlFlowStatementAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.KwSkip).parse_once()
        return LoopControlFlowStatementAst(c1, [], p1)

    @parser_rule
    def parse_pin_statement(self) -> PinStatementAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.KwPin).parse_once()
        p2 = self.parse_expression().parse_one_or_more(TokenType.TkComma)
        return PinStatementAst(c1, p1, p2)

    @parser_rule
    def parse_rel_statement(self) -> RelStatementAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.KwRel).parse_once()
        p2 = self.parse_expression().parse_one_or_more(TokenType.TkComma)
        return RelStatementAst(c1, p1, p2)

    @parser_rule
    def parse_inner_scope(self, rule) -> InnerScopeAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.TkBraceL).parse_once()
        p2 = rule().parse_zero_or_more(TokenType.NO_TOK)
        p3 = self.parse_token(TokenType.TkBraceR).parse_once()
        return InnerScopeAst(c1, p1, p2, p3)

    @parser_rule
    def parse_statement(self) -> StatementAst:
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
    def parse_global_use_statement(self) -> UseStatementAst:
        c1 = self.current_pos()
        p1 = self.parse_annotation().parse_zero_or_more(TokenType.TkNewLine)
        p2 = self.parse_token(TokenType.KwUse).parse_once()
        p3 = self.parse_use_statement_type_alias()
        p4 = self.parse_use_statement_namespace_reduction()
        p5 = (p3 | p4).parse_once()
        return UseStatementAst(c1, p1, p2, p5)

    @parser_rule
    def parse_use_statement(self) -> UseStatementAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.KwUse).parse_once()
        p2 = self.parse_use_statement_type_alias().parse_once()
        # p3 = self.parse_use_statement_namespace_reduction()
        # p4 = (p2 | p3).parse_once()
        return UseStatementAst(c1, [], p1, p2)

    @parser_rule
    def parse_use_statement_namespace_reduction(self) -> UseStatementNamespaceReductionAst:
        c1 = self.current_pos()
        p1 = self.parse_use_statement_namespace_reduction_body().parse_once()
        return UseStatementNamespaceReductionAst(c1, p1)

    @parser_rule
    def parse_use_statement_namespace_reduction_types_multiple(self) -> UseStatementNamespaceReductionTypesMultipleAst:
        c1 = self.current_pos()
        p1 = self.parse_identifier().parse_one_or_more(TokenType.TkDblColon)
        p2 = self.parse_token(TokenType.TkDblColon).parse_once()
        p3 = self.parse_token(TokenType.TkBraceL).parse_once()
        p4 = self.parse_use_statement_namespace_reduction_body().parse_one_or_more(TokenType.TkComma)
        p5 = self.parse_token(TokenType.TkBraceR).parse_once()
        return UseStatementNamespaceReductionTypesMultipleAst(c1, p1, p3, p4, p5)

    @parser_rule
    def parse_use_statement_namespace_reduction_types_single(self) -> UseStatementNamespaceReductionTypesSingleAst:
        p1 = self.parse_use_statement_namespace_reduction_types_single_with_namespace()
        p2 = self.parse_use_statement_namespace_reduction_types_single_without_namespace()
        p3 = (p1 | p2).parse_once()
        return p3

    @parser_rule
    def parse_use_statement_namespace_reduction_types_single_with_namespace(self) -> UseStatementNamespaceReductionTypesSingleAst:
        c1 = self.current_pos()
        p1 = self.parse_identifier().parse_one_or_more(TokenType.TkDblColon)
        p2 = self.parse_token(TokenType.TkDblColon).parse_once()
        p3 = self.parse_generic_identifier().parse_one_or_more(TokenType.TkDblColon)  # No generics allowed here
        p4 = self.parse_use_statement_namespace_reduction_type_alias().parse_optional()
        return UseStatementNamespaceReductionTypesSingleAst(c1, p1, p3, p4)

    @parser_rule
    def parse_use_statement_namespace_reduction_types_single_without_namespace(self) -> UseStatementNamespaceReductionTypesSingleAst:
        c1 = self.current_pos()
        p1 = self.parse_generic_identifier().parse_one_or_more(TokenType.TkDblColon)  # No generics allowed here
        p2 = self.parse_use_statement_namespace_reduction_type_alias().parse_optional()
        return UseStatementNamespaceReductionTypesSingleAst(c1, [], p1, p2)

    @parser_rule
    def parse_use_statement_namespace_reduction_type_alias(self) -> UseStatementNamespaceReductionTypeAliasAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.KwAs).parse_once()
        p2 = self.parse_upper_identifier().parse_once()
        return UseStatementNamespaceReductionTypeAliasAst(c1, p1, p2)

    @parser_rule
    def parse_use_statement_namespace_reduction_body(self) -> UseStatementNamespaceReductionBodyAst:
        c1 = self.current_pos()
        p1 = self.parse_use_statement_namespace_reduction_types_multiple()
        p2 = self.parse_use_statement_namespace_reduction_types_single()
        p3 = (p1 | p2).parse_once()
        return UseStatementNamespaceReductionBodyAst(c1, p3)

    @parser_rule
    def parse_use_statement_type_alias(self) -> UseStatementTypeAliasAst:
        c1 = self.current_pos()
        p1 = self.parse_upper_identifier().parse_once()
        p2 = self.parse_generic_parameters().parse_optional()
        p3 = self.parse_token(TokenType.TkAssign).parse_once()
        p4 = self.parse_type().parse_once()
        return UseStatementTypeAliasAst(c1, p1, p2, p3, p4)

    # ===== LET-DECLARATIONS =====

    @parser_rule
    def parse_global_constant(self) -> GlobalConstantAst:
        c1 = self.current_pos()
        p1 = self.parse_annotation().parse_zero_or_more(TokenType.TkNewLine)
        p2 = self.parse_token(TokenType.KwCmp).parse_once()
        p3 = self.parse_identifier().parse_once()
        p4 = self.parse_token(TokenType.TkColon).parse_once()
        p5 = self.parse_type().parse_once()
        p6 = self.parse_token(TokenType.TkAssign).parse_once()
        p7 = self.parse_global_constant_value().parse_once()
        return GlobalConstantAst(c1, p1, p2, p3, p4, p5, p6, p7)

    @parser_rule
    def parse_let_statement(self) -> LetStatementAst:
        p1 = self.parse_let_statement_initialized()
        p2 = self.parse_let_statement_uninitialized()
        p3 = (p1 | p2).parse_once()
        return p3

    @parser_rule
    def parse_let_statement_initialized(self) -> LetStatementInitializedAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.KwLet).parse_once()
        p2 = self.parse_local_variable().parse_once()
        p3 = self.parse_token(TokenType.TkAssign).parse_once()
        p4 = self.parse_expression().parse_once()
        return LetStatementInitializedAst(c1, p1, p2, p3, p4)

    @parser_rule
    def parse_let_statement_uninitialized(self) -> LetStatementUninitializedAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.KwLet).parse_once()
        p2 = self.parse_local_variable().parse_once()
        p3 = self.parse_token(TokenType.TkColon).parse_once()
        p4 = self.parse_type().parse_once()
        return LetStatementUninitializedAst(c1, p1, p2, p3, p4)

    @parser_rule
    def parse_local_variable(self) -> LocalVariableAst:
        p1 = self.parse_local_variable_single_identifier()
        p2 = self.parse_local_variable_tuple_destructure()
        p3 = self.parse_local_variable_object_destructure()
        p4 = (p1 | p2 | p3).parse_once()
        return p4

    @parser_rule
    def parse_local_variable_skip_argument(self) -> LocalVariableDestructureSkip1ArgumentAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.TkUnderscore).parse_once()
        return LocalVariableDestructureSkip1ArgumentAst(c1, p1)

    @parser_rule
    def parse_local_variable_skip_arguments(self) -> LocalVariableDestructureSkipNArgumentsAst:
        p1 = self.parse_local_variable_skip_arguments_bound()
        p2 = self.parse_local_variable_skip_arguments_unbound()
        p3 = (p1 | p2).parse_once()
        return p3

    @parser_rule
    def parse_local_variable_skip_arguments_bound(self) -> LocalVariableDestructureSkipNArgumentsAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.KwMut).parse_optional()
        p2 = self.parse_token(TokenType.TkVariadic).parse_once()
        p3 = self.parse_identifier().parse_once()
        return LocalVariableDestructureSkipNArgumentsAst(c1, p2, LocalVariableSingleIdentifierAst(c1, p1, p3))

    @parser_rule
    def parse_local_variable_skip_arguments_unbound(self) -> LocalVariableDestructureSkipNArgumentsAst:
        c1 = self.current_pos()
        p2 = self.parse_token(TokenType.TkVariadic).parse_once()
        return LocalVariableDestructureSkipNArgumentsAst(c1, p2, None)

    @parser_rule
    def parse_local_variable_single_identifier(self) -> LocalVariableSingleIdentifierAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.KwMut).parse_optional()
        p2 = self.parse_identifier().parse_once()
        return LocalVariableSingleIdentifierAst(c1, p1, p2)

    @parser_rule
    def parse_local_variable_object_destructure(self) -> LocalVariableDestructureObjectAst:
        c1 = self.current_pos()
        p1 = self.parse_type_single().parse_once()
        p2 = self.parse_token(TokenType.TkParenL).parse_once()
        p3 = self.parse_local_variable_nested_for_object_destructure().parse_zero_or_more(TokenType.TkComma)
        p4 = self.parse_token(TokenType.TkParenR).parse_once()
        return LocalVariableDestructureObjectAst(c1, p1, p2, p3, p4)

    @parser_rule
    def parse_local_variable_tuple_destructure(self) -> LocalVariableDestructureTupleAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.TkParenL).parse_once()
        p2 = self.parse_local_variable_nested_for_tuple_destructure().parse_one_or_more(TokenType.TkComma)
        p3 = self.parse_token(TokenType.TkParenR).parse_once()
        return LocalVariableDestructureTupleAst(c1, p1, p2, p3)

    @parser_rule
    def parse_local_variable_attribute_binding(self) -> LocalVariableAttributeBindingAst:
        c1 = self.current_pos()
        p1 = self.parse_identifier().parse_once()
        p2 = self.parse_token(TokenType.TkAssign).parse_once()
        p3 = self.parse_local_variable_nested_for_attribute_binding().parse_once()
        return LocalVariableAttributeBindingAst(c1, p1, p2, p3)

    @parser_rule
    def parse_local_variable_nested_for_object_destructure(self) -> LocalVariableNestedForDestructureObjectAst:
        p1 = self.parse_local_variable_attribute_binding()
        p2 = self.parse_local_variable_single_identifier()
        p3 = self.parse_local_variable_skip_arguments()
        p4 = (p1 | p2 | p3).parse_once()
        return p4

    @parser_rule
    def parse_local_variable_nested_for_tuple_destructure(self) -> LocalVariableNestedForDestructureTupleAst:
        p1 = self.parse_local_variable_tuple_destructure()
        p2 = self.parse_local_variable_object_destructure()
        p3 = self.parse_local_variable_single_identifier()
        p4 = self.parse_local_variable_skip_arguments()
        p5 = self.parse_local_variable_skip_argument()
        p6 = (p1 | p2 | p3 | p4 | p5).parse_once()
        return p6

    @parser_rule
    def parse_local_variable_nested_for_attribute_binding(self) -> LocalVariableNestedForAttributeBindingAst:
        p1 = self.parse_local_variable_object_destructure()
        p2 = self.parse_local_variable_tuple_destructure()
        p3 = self.parse_local_variable_single_identifier()
        p4 = (p1 | p2 | p3).parse_once()
        return p4

    # ===== ASSIGNMENT =====

    @parser_rule
    def parse_assignment_statement(self) -> AssignmentStatementAst:
        c1 = self.current_pos()
        p1 = self.parse_expression().parse_one_or_more(TokenType.TkComma)
        p2 = self.parse_token(TokenType.TkAssign).parse_once()
        p3 = self.parse_expression().parse_one_or_more(TokenType.TkComma)
        return AssignmentStatementAst(c1, p1, p2, p3)

    # ===== PATTERNS =====

    @parser_rule
    def parse_case_expression_branch(self) -> CaseExpressionBranchAst:
        p1 = self.parse_pattern_statement_flavour_destructuring()
        p2 = self.parse_pattern_statement_flavour_non_destructuring()
        p3 = self.parse_pattern_statement_flavour_else_case()
        p4 = self.parse_pattern_statement_flavour_else()
        p5 = (p1 | p2 | p3 | p4).parse_once()
        return p5

    @parser_rule
    def parse_pattern_statement_flavour_destructuring(self) -> CaseExpressionBranchAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.KwIs).parse_once()
        p2 = self.parse_pattern_group_destructure().parse_one_or_more(TokenType.TkComma)
        p3 = self.parse_pattern_guard().parse_optional()
        p4 = self.parse_inner_scope(self.parse_statement).parse_once()
        return CaseExpressionBranchAst(c1, p1, p2, p3, p4)

    @parser_rule
    def parse_pattern_statement_flavour_non_destructuring(self) -> CaseExpressionBranchAst:
        c1 = self.current_pos()
        p1 = self.parse_boolean_comparison_op().parse_once()
        p2 = self.parse_pattern_variant_expression().parse_one_or_more(TokenType.TkComma)
        p3 = self.parse_inner_scope(self.parse_statement).parse_once()
        return CaseExpressionBranchAst(c1, p1, p2, None, p3)

    @parser_rule
    def parse_pattern_statement_flavour_else(self) -> CaseExpressionBranchAst:
        c1 = self.current_pos()
        p1 = self.parse_pattern_variant_else().parse_once()
        p2 = self.parse_inner_scope(self.parse_statement).parse_once()
        return CaseExpressionBranchAst(c1, None, [p1], None, p2)

    @parser_rule
    def parse_pattern_statement_flavour_else_case(self) -> CaseExpressionBranchAst:
        c1 = self.current_pos()
        p1 = self.parse_pattern_variant_else_case().parse_once()
        return CaseExpressionBranchAst(c1, None, [p1], None, None)

    @parser_rule
    def parse_pattern_group_destructure(self) -> PatternGroupDestructureAst:
        p1 = self.parse_pattern_variant_tuple_destructure()
        p2 = self.parse_pattern_variant_object_destructure()
        return (p1 | p2).parse_once()

    @parser_rule
    def parse_pattern_variant_skip_argument(self) -> PatternVariantDestructureSkip1ArgumentAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.TkUnderscore).parse_once()
        return PatternVariantDestructureSkip1ArgumentAst(c1, p1)

    @parser_rule
    def parse_pattern_variant_skip_arguments(self) -> PatternVariantDestructureSkipNArgumentsAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.TkVariadic).parse_once()
        p2 = self.parse_pattern_variant_single_identifier().parse_optional()
        return PatternVariantDestructureSkipNArgumentsAst(c1, p1, p2)

    @parser_rule
    def parse_pattern_variant_single_identifier(self) -> PatternVariantSingleIdentifierAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.KwMut).parse_optional()
        p2 = self.parse_identifier().parse_once()
        return PatternVariantSingleIdentifierAst(c1, p1, p2)

    @parser_rule
    def parse_pattern_variant_object_destructure(self) -> PatternVariantDestructureObjectAst:
        c1 = self.current_pos()
        p1 = self.parse_type_single().parse_once()
        p2 = self.parse_token(TokenType.TkParenL).parse_once()
        p3 = self.parse_pattern_variant_nested_for_object_destructure().parse_zero_or_more(TokenType.TkComma)
        p4 = self.parse_token(TokenType.TkParenR).parse_once()
        return PatternVariantDestructureObjectAst(c1, p1, p2, p3, p4)

    @parser_rule
    def parse_pattern_variant_tuple_destructure(self) -> PatternVariantDestructureTupleAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.TkParenL).parse_once()
        p2 = self.parse_pattern_variant_nested_for_tuple_destructure().parse_one_or_more(TokenType.TkComma)
        p3 = self.parse_token(TokenType.TkParenR).parse_once()
        return PatternVariantDestructureTupleAst(c1, p1, p2, p3)

    @parser_rule
    def parse_pattern_variant_attribute_binding(self) -> PatternVariantAttributeBindingAst:
        c1 = self.current_pos()
        p1 = self.parse_identifier().parse_once()
        p2 = self.parse_token(TokenType.TkAssign).parse_once()
        p3 = self.parse_pattern_variant_nested_for_attribute_binding().parse_once()
        return PatternVariantAttributeBindingAst(c1, p1, p2, p3)

    @parser_rule
    def parse_pattern_variant_literal(self) -> PatternVariantLiteralAst:
        c1 = self.current_pos()
        p1 = self.parse_literal_float()
        p2 = self.parse_literal_integer()
        p3 = self.parse_literal_string()
        p4 = self.parse_literal_boolean()
        p5 = (p1 | p2 | p3 | p4).parse_once()
        return PatternVariantLiteralAst(c1, p5)

    @parser_rule
    def parse_pattern_variant_expression(self) -> PatternVariantExpressionAst:
        c1 = self.current_pos()
        p1 = self.parse_expression().parse_once()
        return PatternVariantExpressionAst(c1, p1)

    @parser_rule
    def parse_pattern_variant_else(self) -> PatternVariantElseAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.KwElse).parse_once()
        return PatternVariantElseAst(c1, p1)

    @parser_rule
    def parse_pattern_variant_else_case(self) -> PatternVariantElseCaseAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.KwElse).parse_once()
        p2 = self.parse_case_expression().parse_once()
        return PatternVariantElseCaseAst(c1, p1, p2)

    @parser_rule
    def parse_pattern_variant_nested_for_object_destructure(self) -> PatternVariantNestedForDestructureObjectAst:
        p1 = self.parse_pattern_variant_attribute_binding()
        p2 = self.parse_pattern_variant_single_identifier()
        p3 = self.parse_pattern_variant_skip_arguments()
        p4 = (p1 | p2 | p3).parse_once()
        return p4

    @parser_rule
    def parse_pattern_variant_nested_for_tuple_destructure(self) -> PatternVariantNestedForDestructureTupleAst:
        p1 = self.parse_pattern_variant_tuple_destructure()
        p2 = self.parse_pattern_variant_object_destructure()
        p3 = self.parse_pattern_variant_single_identifier()
        p4 = self.parse_pattern_variant_literal()
        p5 = self.parse_pattern_variant_skip_arguments()
        p6 = self.parse_pattern_variant_skip_argument()
        p7 = (p1 | p2 | p3 | p4 | p5 | p6).parse_once()
        return p7

    @parser_rule
    def parse_pattern_variant_nested_for_attribute_binding(self) -> PatternVariantNestedForAttributeBindingAst:
        p1 = self.parse_pattern_variant_tuple_destructure()
        p2 = self.parse_pattern_variant_object_destructure()
        p3 = self.parse_pattern_variant_literal()
        p4 = (p1 | p2 | p3).parse_once()
        return p4

    @parser_rule
    def parse_pattern_guard(self) -> PatternGuardAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.KwAnd).parse_once()
        p2 = self.parse_expression().parse_once()
        return PatternGuardAst(c1, p1, p2)

    # ===== OPERATORS =====

    @parser_rule
    def parse_binary_op_precedence_level_1(self) -> TokenAst:
        p1 = self.parse_token(TokenType.KwOr).parse_once()
        return p1

    @parser_rule
    def parse_binary_op_precedence_level_2(self) -> TokenAst:
        p1 = self.parse_token(TokenType.KwAnd).parse_once()
        return p1

    @parser_rule
    def parse_binary_op_precedence_level_3(self) -> TokenAst:
        p1 = self.parse_token(TokenType.KwIs).parse_once()
        return p1

    @parser_rule
    def parse_binary_op_precedence_level_4(self) -> TokenAst:
        p1 = self.parse_token(TokenType.TkEq)
        p2 = self.parse_token(TokenType.TkNe)
        p3 = self.parse_token(TokenType.TkLe)
        p4 = self.parse_token(TokenType.TkGe)
        p5 = self.parse_token(TokenType.TkLt)
        p6 = self.parse_token(TokenType.TkGt)
        p7 = self.parse_token(TokenType.TkSs)
        p8 = (p1 | p2 | p3 | p4 | p5 | p6 | p7).parse_once()
        return p8

    @parser_rule
    def parse_binary_op_precedence_level_5(self) -> TokenAst:
        p1 = self.parse_token(TokenType.TkAdd)
        p2 = self.parse_token(TokenType.TkSub)
        p3 = self.parse_token(TokenType.TkAddAssign)
        p4 = self.parse_token(TokenType.TkSubAssign)
        p5 = (p1 | p2 | p3 | p4).parse_once()
        return p5

    @parser_rule
    def parse_binary_op_precedence_level_6(self) -> TokenAst:
        p1 = self.parse_token(TokenType.TkMul)
        p2 = self.parse_token(TokenType.TkDiv)
        p3 = self.parse_token(TokenType.TkRem)
        p4 = self.parse_token(TokenType.TkMod)
        p5 = self.parse_token(TokenType.TkExp)
        p6 = self.parse_token(TokenType.TkMulAssign)
        p7 = self.parse_token(TokenType.TkDivAssign)
        p8 = self.parse_token(TokenType.TkRemAssign)
        p9 = self.parse_token(TokenType.TkModAssign)
        p10 = self.parse_token(TokenType.TkExpAssign)
        p11 = (p1 | p2 | p3 | p4 | p5 | p6 | p7 | p8 | p9 | p10).parse_once()
        return p11

    @parser_rule
    def parse_boolean_comparison_op(self) -> TokenAst:
        p1 = self.parse_token(TokenType.TkEq)
        p2 = self.parse_token(TokenType.TkNe)
        p3 = self.parse_token(TokenType.TkLe)
        p4 = self.parse_token(TokenType.TkGe)
        p5 = self.parse_token(TokenType.TkLt)
        p6 = self.parse_token(TokenType.TkGt)
        p8 = (p1 | p2 | p3 | p4 | p5 | p6).parse_once()
        return p8

    @parser_rule
    def parse_unary_op(self) -> TokenAst:
        p1 = self.parse_unary_op_async_call().parse_once()
        return p1

    @parser_rule
    def parse_unary_op_async_call(self) -> UnaryExpressionOperatorAsyncAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.KwAsync).parse_once()
        return UnaryExpressionOperatorAsyncAst(c1, p1)

    @parser_rule
    def parse_postfix_op(self) -> PostfixExpressionOperatorAst:
        p1 = self.parse_postfix_op_function_call()
        p2 = self.parse_postfix_op_member_access()
        p3 = self.parse_postfix_op_early_return()
        p4 = self.parse_postfix_op_not_keyword()
        p5 = (p1 | p2 | p3 | p4).parse_once()
        return p5

    @parser_rule
    def parse_postfix_op_function_call(self) -> PostfixExpressionOperatorFunctionCallAst:
        c1 = self.current_pos()
        p1 = self.parse_generic_arguments().parse_optional()
        p2 = self.parse_function_call_arguments().parse_once()
        p3 = self.parse_token(TokenType.TkVariadic).parse_optional()
        return PostfixExpressionOperatorFunctionCallAst(c1, p1, p2, p3)

    @parser_rule
    def parse_postfix_op_member_access(self) -> PostfixExpressionOperatorMemberAccessAst:
        p1 = self.parse_postfix_op_member_access_runtime()
        p2 = self.parse_postfix_op_member_access_static()
        p3 = (p1 | p2).parse_once()
        return p3

    @parser_rule
    def parse_postfix_op_member_access_runtime(self) -> PostfixExpressionOperatorMemberAccessAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.TkDot).parse_once()
        p2 = self.parse_identifier()
        p3 = self.parse_lexeme(TokenType.LxDecInteger)
        p4 = (p2 | p3).parse_once()
        return PostfixExpressionOperatorMemberAccessAst(c1, p1, p4)

    @parser_rule
    def parse_postfix_op_member_access_static(self) -> PostfixExpressionOperatorMemberAccessAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.TkDblColon).parse_once()
        p2 = self.parse_identifier().parse_once()
        return PostfixExpressionOperatorMemberAccessAst(c1, p1, p2)

    @parser_rule
    def parse_postfix_op_early_return(self) -> PostfixExpressionOperatorEarlyReturnAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.TkQst).parse_once()
        return PostfixExpressionOperatorEarlyReturnAst(c1, p1)

    @parser_rule
    def parse_postfix_op_not_keyword(self) -> PostfixExpressionOperatorNotKeywordAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.TkDot).parse_once()
        p2 = self.parse_token(TokenType.KwNot).parse_once()
        return PostfixExpressionOperatorNotKeywordAst(c1, p1, p2)

    # ===== CONVENTIONS =====

    @parser_rule
    def parse_convention(self) -> ConventionAst:
        p1 = self.parse_convention_mut()
        p2 = self.parse_convention_ref()
        p3 = self.parse_convention_mov()
        p4 = (p1 | p2 | p3).parse_once()
        return p4

    @parser_rule
    def parse_convention_mov(self) -> ConventionMovAst:
        c1 = self.current_pos()
        return ConventionMovAst(c1)

    @parser_rule
    def parse_convention_ref(self) -> ConventionRefAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.TkBorrow).parse_once()
        return ConventionRefAst(c1, p1)

    @parser_rule
    def parse_convention_mut(self) -> ConventionMutAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.TkBorrow).parse_once()
        p2 = self.parse_token(TokenType.KwMut).parse_once()
        return ConventionMutAst(c1, p1, p2)

    # ===== OBJECT INITIALIZATION =====

    @parser_rule
    def parse_object_initialization(self) -> ObjectInitializerAst:
        c1 = self.current_pos()
        p1 = self.parse_type_single().parse_once()
        p2 = self.parse_object_initializer_arguments().parse_once()
        return ObjectInitializerAst(c1, p1, p2)

    @parser_rule
    def parse_object_initializer_arguments(self) -> ObjectInitializerArgumentGroupAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.TkParenL).parse_once()
        p2 = self.parse_object_initializer_argument().parse_zero_or_more(TokenType.TkComma)
        p3 = self.parse_token(TokenType.TkParenR).parse_once()
        return ObjectInitializerArgumentGroupAst(c1, p1, p2, p3)

    @parser_rule
    def parse_object_initializer_argument(self) -> ObjectInitializerArgumentAst:
        p1 = self.parse_object_initializer_argument_named()
        p2 = self.parse_object_initializer_argument_unnamed()
        p3 = (p1 | p2).parse_once()
        return p3

    @parser_rule
    def parse_object_initializer_argument_unnamed(self) -> ObjectInitializerArgumentUnnamedAst:
        c1 = self.current_pos()
        p1 = self.parse_identifier().parse_once()
        return ObjectInitializerArgumentUnnamedAst(c1, p1)

    @parser_rule
    def parse_object_initializer_argument_named(self) -> ObjectInitializerArgumentNamedAst:
        c1 = self.current_pos()
        p1 = self.parse_object_initializer_argument_named_key().parse_once()
        p2 = self.parse_token(TokenType.TkAssign).parse_once()
        p3 = self.parse_expression().parse_once()
        return ObjectInitializerArgumentNamedAst(c1, p1, p2, p3)

    @parser_rule
    def parse_object_initializer_argument_named_key(self) -> IdentifierAst | TokenAst:
        p1 = self.parse_identifier()
        p2 = self.parse_token(TokenType.KwElse)
        p3 = self.parse_token(TokenType.KwSup)
        p4 = (p1 | p2 | p3).parse_once()
        return p4

    # ===== LAMBDAS =====

    # @parser_rule
    # def parse_lambda_prototype(self) -> LambdaPrototypeAst:
    #     c1 = self.current_pos()
    #     p1 = self.parse_token(TokenType.KwFun).parse_once()  # todo: allow lambda coroutines
    #     p2 = self.parse_generic_parameters().parse_optional()
    #     p3 = self.parse_function_parameters().parse_once()
    #     p4 = self.parse_token(TokenType.TkArrowR).parse_once()
    #     p5 = self.parse_type().parse_once()
    #     p6 = self.parse_lambda_capture_block().parse_optional()
    #     p7 = self.parse_where_block().parse_optional()
    #     p8 = self.parse_inner_scope(self.parse_statement).parse_once()
    #     return LambdaPrototypeAst(c1, p1, p2, p3, p4, p5, p6, p7, p8)
    #
    # @parser_rule
    # def parse_lambda_capture_block(self) -> LambdaCaptureBlockAst:
    #     c1 = self.current_pos()
    #     p1 = self.parse_token(TokenType.TkBrackL).parse_once()
    #     p2 = self.parse_lambda_capture_item().parse_zero_or_more(TokenType.TkComma)
    #     p3 = self.parse_token(TokenType.TkBrackR).parse_once()
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
    #     p2 = self.parse_token(TokenType.TkAssign).parse_once()
    #     p3 = self.parse_convention().parse_once()
    #     p4 = self.parse_expression().parse_once()
    #     return LambdaCaptureItemNamedAst(c1, p1, p2, p3, p4)

    # ===== TYPES =====

    @parser_rule
    def parse_type(self) -> TypeAst:
        p1 = self.parse_type_optional()
        p2 = self.parse_type_variant()
        p3 = self.parse_type_tuple()
        p4 = self.parse_type_single()
        p5 = (p1 | p2 | p3 | p4).parse_once()
        return p5

    @parser_rule
    def parse_type_optional(self) -> TypeAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.TkQst).parse_once()
        p2 = self.parse_type().parse_once()
        return TypeOptionalAst(c1, p1, p2).to_type()

    @parser_rule
    def parse_type_single(self) -> TypeAst:
        p1 = self.parse_type_single_with_namespace()
        p2 = self.parse_type_single_without_namespace()
        p3 = (p1 | p2).parse_once()
        return p3

    @parser_rule
    def parse_type_single_with_namespace(self) -> TypeAst:
        c1 = self.current_pos()
        p1 = self.parse_identifier().parse_one_or_more(TokenType.TkDblColon)
        p2 = self.parse_token(TokenType.TkDblColon).parse_once()
        # p3 = self.parse_type_part_first().parse_once()
        # p4 = self.parse_type_part().parse_zero_or_more(TokenType.NO_TOK)
        p3 = self.parse_generic_identifier().parse_one_or_more(TokenType.TkDblColon)
        return TypeAst(c1, p1, p3)  # [p3, *p4])

    @parser_rule
    def parse_type_single_without_namespace(self) -> TypeAst:
        c1 = self.current_pos()
        # p1 = self.parse_type_part_first().parse_once()
        # p2 = self.parse_type_part().parse_zero_or_more(TokenType.NO_TOK)
        p1 = self.parse_generic_identifier().parse_one_or_more(TokenType.TkDblColon)
        return TypeAst(c1, [], p1)  # [p1, *p2])

    @parser_rule
    def parse_type_tuple(self) -> TypeAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.TkParenL).parse_once()
        p2 = self.parse_type().parse_zero_or_more(TokenType.TkComma)
        p3 = self.parse_token(TokenType.TkParenR).parse_once()
        return TypeTupleAst(c1, p1, p2, p3).to_type()

    @parser_rule
    def parse_type_non_union(self) -> TypeAst:
        p1 = self.parse_type_single()
        p2 = self.parse_type_tuple()
        p3 = self.parse_type_optional()
        p4 = (p1 | p2 | p3).parse_once()
        return p4

    @parser_rule
    def parse_type_variant(self) -> TypeAst:
        c1 = self.current_pos()
        p1 = self.parse_type_non_union().parse_two_or_more(TokenType.TkUnion)
        return TypeVariantAst(c1, p1).to_type()

    @parser_rule
    def parse_type_part(self) -> TypePartAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.TkDblColon).parse_once()
        p2 = self.parse_generic_identifier()
        p3 = self.parse_lexeme(TokenType.LxDecInteger)
        p4 = (p2 | p3).parse_once()
        return p4

    @parser_rule
    def parse_type_part_first(self) -> TypePartAst:
        c1 = self.current_pos()
        p1 = self.parse_generic_identifier().parse_once()
        # p2 = self.parse_self_type_keyword()
        # p3 = (p1 | p2).parse_once()
        return p1

    # @parser_rule
    # def parse_self_type_keyword(self) -> GenericIdentifierAst:
    #     c1 = self.current_pos()
    #     p1 = self.parse_token(TokenType.KwSelfType).parse_once()
    #     return GenericIdentifierAst(c1, p1.token.token_metadata, None)

    # ===== IDENTIFIERS =====

    @parser_rule
    def parse_identifier(self) -> IdentifierAst:
        c1 = self.current_pos()
        p1 = self.parse_lexeme(TokenType.LxIdentifier).parse_once()
        return IdentifierAst(c1, p1.token.token_metadata)

    @parser_rule
    def parse_upper_identifier(self) -> IdentifierAst:
        c1 = self.current_pos()
        p1 = self.parse_lexeme(TokenType.LxUpperIdentifier).parse_once()
        return IdentifierAst(c1, p1.token.token_metadata)

    @parser_rule
    def parse_generic_identifier(self) -> GenericIdentifierAst:
        c1 = self.current_pos()
        p1 = self.parse_upper_identifier().parse_once()
        p2 = self.parse_generic_arguments().parse_optional()
        return GenericIdentifierAst(c1, p1.value, p2)

    # ===== LITERALS =====

    @parser_rule
    def parse_literal(self) -> LiteralAst:
        p1 = self.parse_literal_float()
        p2 = self.parse_literal_integer()
        p3 = self.parse_literal_string()
        p4 = self.parse_literal_tuple(self.parse_expression)
        p5 = self.parse_literal_array(self.parse_expression)
        p6 = self.parse_literal_regex()
        p7 = self.parse_literal_boolean()
        p8 = (p1 | p2 | p3 | p4 | p5 | p6 | p7).parse_once()
        return p8

    @parser_rule
    def parse_literal_float(self) -> FloatLiteralAst:
        p1 = self.parse_literal_float_b10().parse_once()
        return p1

    @parser_rule
    def parse_literal_integer(self) -> IntegerLiteralAst:
        p1 = self.parse_literal_integer_b10()
        p2 = self.parse_literal_integer_b02()
        p3 = self.parse_literal_integer_b16()
        p4 = (p1 | p2 | p3).parse_once()
        return p4

    @parser_rule
    def parse_literal_string(self) -> StringLiteralAst:
        c1 = self.current_pos()
        p1 = self.parse_lexeme(TokenType.LxDoubleQuoteStr).parse_once()
        return StringLiteralAst(c1, p1)

    @parser_rule
    def parse_literal_tuple(self, item=None) -> TupleLiteralAst:
        p1 = self.parse_literal_tuple_0_items()
        p2 = self.parse_literal_tuple_1_items(item or self.parse_expression)
        p3 = self.parse_literal_tuple_n_items(item or self.parse_expression)
        p4 = (p1 | p2 | p3).parse_once()
        return p4

    @parser_rule
    def parse_literal_array(self, item) -> ArrayLiteralAst:
        p1 = self.parse_literal_array_0_items()
        p2 = self.parse_literal_array_n_items(item)
        p3 = (p1 | p2).parse_once()
        return p3

    @parser_rule
    def parse_literal_regex(self) -> RegexLiteralAst:
        c1 = self.current_pos()
        p1 = self.parse_lexeme(TokenType.LxRegex).parse_once()
        return RegexLiteralAst(c1, p1)

    @parser_rule
    def parse_literal_boolean(self) -> BooleanLiteralAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.KwTrue)
        p2 = self.parse_token(TokenType.KwFalse)
        p3 = (p1 | p2).parse_once()
        return BooleanLiteralAst(c1, p3)

    # ===== NUMBERS =====

    @parser_rule
    def parse_literal_float_b10(self) -> FloatLiteralAst:
        c1 = self.current_pos()
        p1 = self.parse_numeric_prefix_op().parse_optional()
        p2 = self.parse_lexeme(TokenType.LxDecInteger).parse_once()
        p3 = self.parse_token(TokenType.TkDot).parse_once()
        p4 = self.parse_lexeme(TokenType.LxDecInteger).parse_once()
        p5 = self.parse_float_postfix_type().parse_optional()
        return FloatLiteralAst(c1, p1, p2, p3, p4, p5)

    @parser_rule
    def parse_literal_integer_b10(self) -> IntegerLiteralAst:
        c1 = self.current_pos()
        p1 = self.parse_numeric_prefix_op().parse_optional()
        p2 = self.parse_lexeme(TokenType.LxDecInteger).parse_once()
        p3 = self.parse_integer_postfix_type().parse_optional()
        return IntegerLiteralAst(c1, p1, p2, p3)

    @parser_rule
    def parse_literal_integer_b02(self) -> IntegerLiteralAst:
        c1 = self.current_pos()
        p1 = self.parse_numeric_prefix_op().parse_optional()
        p2 = self.parse_lexeme(TokenType.LxBinDigits).parse_once()
        p3 = self.parse_integer_postfix_type().parse_optional()
        return IntegerLiteralAst(c1, p1, p2, p3)

    @parser_rule
    def parse_literal_integer_b16(self) -> IntegerLiteralAst:
        c1 = self.current_pos()
        p1 = self.parse_numeric_prefix_op().parse_optional()
        p2 = self.parse_lexeme(TokenType.LxHexDigits).parse_once()
        p3 = self.parse_integer_postfix_type().parse_optional()
        return IntegerLiteralAst(c1, p1, p2, p3)

    @parser_rule
    def parse_numeric_prefix_op(self) -> TokenAst:
        p1 = self.parse_token(TokenType.TkSub)
        p2 = self.parse_token(TokenType.TkAdd)
        p3 = (p1 | p2).parse_once()
        return p3

    @parser_rule
    def parse_integer_postfix_type(self) -> TokenType:
        p1  = self.parse_token(TokenType.TkUnderscore).parse_once()
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
    def parse_float_postfix_type(self) -> TokenType:
        p1 = self.parse_token(TokenType.TkUnderscore).parse_once()
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
    def parse_literal_tuple_0_items(self) -> TupleLiteralAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.TkParenL).parse_once()
        p2 = self.parse_token(TokenType.TkParenR).parse_once()
        return TupleLiteralAst(c1, p1, [], p2)

    @parser_rule
    def parse_literal_tuple_1_items(self, item) -> TupleLiteralAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.TkParenL).parse_once()
        p2 = item().parse_once()
        p3 = self.parse_token(TokenType.TkComma).parse_once()
        p4 = self.parse_token(TokenType.TkParenR).parse_once()
        return TupleLiteralAst(c1, p1, [p2], p4)

    @parser_rule
    def parse_literal_tuple_n_items(self, item) -> TupleLiteralAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.TkParenL).parse_once()
        p2 = item().parse_one_or_more(TokenType.TkComma)
        p3 = self.parse_token(TokenType.TkParenR).parse_once()
        return TupleLiteralAst(c1, p1, p2, p3)

    # ===== ARRAYS =====

    @parser_rule
    def parse_literal_array_0_items(self) -> ArrayLiteral0ElementAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.TkBrackL).parse_once()
        p2 = self.parse_type().parse_once()
        p3 = self.parse_token(TokenType.TkComma).parse_once()
        p4 = self.parse_lexeme(TokenType.LxDecInteger).parse_once()
        p5 = self.parse_token(TokenType.TkBrackR).parse_once()
        return ArrayLiteral0ElementAst(c1, p1, p2, p3, p4, p5)

    @parser_rule
    def parse_literal_array_n_items(self, item) -> ArrayLiteralNElementAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.TkBrackL).parse_once()
        p2 = item().parse_one_or_more(TokenType.TkComma)
        p3 = self.parse_token(TokenType.TkBrackR).parse_once()
        return ArrayLiteralNElementAst(c1, p1, p2, p3)

    # ===== GLOBAL CONSTANTS =====
    @parser_rule
    def parse_global_constant_value(self) -> ExpressionAst:
        p1 = self.parse_literal_float()
        p2 = self.parse_literal_integer()
        p3 = self.parse_literal_string()
        p4 = self.parse_literal_tuple(self.parse_global_constant_value)
        p5 = self.parse_literal_array(self.parse_global_constant_value)
        p6 = self.parse_literal_regex()
        p7 = self.parse_literal_boolean()
        p8 = self.parse_global_object_initialization()
        p9 = self.parse_identifier()
        p10 = (p1 | p2 | p3 | p4 | p5 | p6 | p7 | p8 | p9).parse_once()
        return p10

    @parser_rule
    def parse_global_object_initialization(self) -> ObjectInitializerAst:
        c1 = self.current_pos()
        p1 = self.parse_type_single().parse_once()
        p2 = self.parse_global_object_initializer_arguments().parse_once()
        return ObjectInitializerAst(c1, p1, p2)

    @parser_rule
    def parse_global_object_initializer_arguments(self) -> ObjectInitializerArgumentGroupAst:
        c1 = self.current_pos()
        p1 = self.parse_token(TokenType.TkParenL).parse_once()
        p2 = self.parse_global_object_initializer_argument_named().parse_zero_or_more(TokenType.TkComma)  # todo: normal too for copyables?
        p3 = self.parse_token(TokenType.TkParenR).parse_once()
        return ObjectInitializerArgumentGroupAst(c1, p1, p2, p3)

    @parser_rule
    def parse_global_object_initializer_argument_named(self) -> ObjectInitializerArgumentNamedAst:
        c1 = self.current_pos()
        p1 = self.parse_identifier().parse_once()
        p2 = self.parse_token(TokenType.TkAssign).parse_once()
        p3 = self.parse_global_constant_value().parse_once()
        return ObjectInitializerArgumentNamedAst(c1, p1, p2, p3)

    # ===== TOKENS, KEYWORDS, & LEXEMES =====

    @parser_rule
    def parse_lexeme(self, lexeme: TokenType) -> TokenAst:
        compiled_lexeme = TokenType[f"Cm{lexeme.name}"]
        p1 = self.parse_token(compiled_lexeme).parse_once()
        return p1

    @parser_rule
    def parse_characters(self, characters: str) -> TokenAst:
        # TODO : these rules don't come up u the error for failed alternate parsing (see number postfix types)

        p1 = self.parse_identifier().parse_once()
        if p1.value == characters:
            return p1
        else:
            new_error = f"Expected '{characters}', got '{p1.value}'"
            self.store_error(self.current_pos(), new_error)
            raise self._error

    @parser_rule
    def parse_token(self, token_type: TokenType) -> TokenAst:
        # For the "no token", instantly return a new token.
        if token_type == TokenType.NO_TOK:
            return TokenAst(self.current_pos(), Token("", TokenType.NO_TOK))

        # Check if the end of the file has been reached.
        if self._index > len(self._tokens) - 1:
            new_error = f"Expected '{token_type}', got <EOF>"
            self.store_error(self.current_pos(), new_error)
            raise new_error

        # Skip newlines and whitespace for non-newline parsing, and whitespace only for new-line parsing.
        if token_type != TokenType.TkNewLine:
            while self._tokens[self._index].token_type == TokenType.TkNewLine or self._tokens[self._index].token_type == TokenType.TkWhitespace:
                self._index += 1
        if token_type == TokenType.TkNewLine:
            while self._tokens[self._index].token_type == TokenType.TkWhitespace:
                self._index += 1

        # Handle an incorrectly placed token.
        if self._tokens[self._index].token_type != token_type:
            if self._error.pos == self._index:
                self._error.expected_tokens.append(token_type)
                raise self._error

            new_error = f"Expected $, got '{self._tokens[self._index].token_type.name}'"
            if self.store_error(self._index, new_error):
                self._error.expected_tokens.append(token_type)
            raise self._error

        # Otherwise, the parse was successful, so return a TokenAst as the correct position.
        r = TokenAst(self._index, self._tokens[self._index])
        self._index += 1
        return r

    def store_error(self, pos: int, error: str) -> bool:
        if pos > self._error.pos:
            self._error.expected_tokens.clear()
            self._error.pos = pos
            self._error.args = (error,)
            return True
        return False


__all__ = ["Parser", "parser_rule"]
