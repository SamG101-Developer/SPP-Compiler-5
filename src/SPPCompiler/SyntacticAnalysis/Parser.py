from __future__ import annotations

from typing import Callable, List, Optional, Tuple, Union

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType, RawToken, RawTokenType, RawKeywordType
from SPPCompiler.SyntacticAnalysis.ErrorFormatter import ErrorFormatter
from SPPCompiler.SyntacticAnalysis.ParserErrors import ParserErrors
from SPPCompiler.Utils.Functools import reduce
from SPPCompiler.Utils.Sequence import Seq


# Todo: add newlines after multi-expression/statement blocks (ie between multiple ret/gen/let etc)


class SppParser:
    _pos: int
    _tokens: List[RawToken]
    _tokens_len: int
    _error: ParserErrors.SyntaxError
    _error_formatter: ErrorFormatter

    _identifier_characters: List[SppTokenType]
    _upper_identifier_characters: List[SppTokenType]
    _skip_all_characters: List[SppTokenType]
    _skip_newline_character: SppTokenType
    _skip_whitespace_character: SppTokenType

    def __init__(self, tokens: List[RawToken], file_name: str = "", error_formatter: Optional[ErrorFormatter] = None) -> None:
        self._pos = 0
        self._tokens = tokens
        self._tokens_len = len(tokens)
        self._error = ParserErrors.SyntaxError()
        self._error_formatter = error_formatter or ErrorFormatter(tokens, file_name)

        self._identifier_characters = [RawTokenType.TkCharacter, RawTokenType.TkDigit, RawTokenType.TkUnderscore]
        self._upper_identifier_characters = [RawTokenType.TkCharacter, RawTokenType.TkDigit]
        self._skip_all_characters = [RawTokenType.TkWhitespace, RawTokenType.TkNewLine]
        self._skip_newline_character = RawTokenType.TkNewLine
        self._skip_whitespace_character = RawTokenType.TkWhitespace

    def current_tok(self) -> RawToken:
        return self._tokens[self._pos]

    # ===== TECHNIQUES =====

    def parse_once[T](self, method: Callable[..., T]) -> T:
        return method()

    def parse_optional[T](self, method: Callable[..., T]) -> Optional[T]:
        pos = self._pos
        try:
            result = method()
            return result
        except ParserErrors.SyntaxError as e:
            self._pos = pos
            return None

    def parse_zero_or_more[T, S](self, method: Callable[..., T], separator: Callable[..., S]) -> Seq[T]:
        done_1_parse = False
        result = Seq()
        temp_pos = self._pos

        while True:
            if done_1_parse:
                if (sep := self.parse_optional(separator)) is None:
                    return result

            if ast := self.parse_optional(method):
                result.append(ast)
                done_1_parse = True
                temp_pos = self._pos
            else:
                self._pos = temp_pos
                return result

    def parse_one_or_more[T, S](self, method: Callable[..., T], separator: Callable[..., S]) -> Seq[T]:
        result = self.parse_zero_or_more(method, separator)
        if result.length < 1:
            self.store_error(self._pos, "Expected at least one element")
            raise self._error
        return result

    def parse_two_or_more[T, S](self, method: Callable[..., T], separator: Callable[..., S]) -> Seq[T]:
        result = self.parse_zero_or_more(method, separator)
        if result.length < 2:
            self.store_error(self._pos, "Expected at least two elements")
            raise self._error
        return result

    def parse_alternate[Ts](self, *methods: Callable[..., *Ts]) -> Union[*Ts]:
        for method in methods:
            if ast := self.parse_optional(method):
                return ast
        self.store_error(self._pos, "Expected one of the alternatives")
        raise self._error

    # ===== PROGRAM =====

    def parse(self):
        try:
            return self.parse_root()
        except ParserErrors.SyntaxError:
            self._error.throw(self._error_formatter)

    def parse_root(self) -> Asts.ModulePrototypeAst:
        p1 = self.parse_once(self.parse_module_prototype)
        p2 = self.parse_eof()
        return p1

    def parse_eof(self) -> Asts.TokenAst:
        return self.parse_token_raw(RawTokenType.EndOfFile, SppTokenType.NoToken)

    # ===== MODULES =====

    def parse_module_prototype(self) -> Asts.ModulePrototypeAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_module_implementation)
        return Asts.ModulePrototypeAst(c1, p1)

    def parse_module_implementation(self) -> Asts.ModuleImplementationAst:
        c1 = self._pos
        p1 = self.parse_zero_or_more(self.parse_module_member, self.parse_newline)
        return Asts.ModuleImplementationAst(c1, p1)

    def parse_module_member(self) -> Asts.ModuleMemberAst:
        p1 = self.parse_alternate(
            self.parse_function_prototype,
            self.parse_class_prototype,
            self.parse_sup_prototype_extension,
            self.parse_sup_prototype_functions,
            self.parse_global_use_statement,
            self.parse_global_constant)
        return p1

    # ===== CLASSES =====

    def parse_class_prototype(self) -> Asts.ClassPrototypeAst:
        c1 = self._pos
        p1 = self.parse_zero_or_more(self.parse_annotation, self.parse_newline)
        p2 = self.parse_once(self.parse_keyword_cls)
        p3 = self.parse_once(self.parse_upper_identifier)
        p4 = self.parse_optional(self.parse_generic_parameters) or Asts.GenericParameterGroupAst(pos=c1)
        p5 = self.parse_optional(self.parse_where_block) or Asts.WhereBlockAst(pos=c1)
        p6 = self.parse_once(self.parse_class_implementation)
        return Asts.ClassPrototypeAst(c1, p1, p2, Asts.TypeSingleAst.from_identifier(p3), p4, p5, p6)

    def parse_class_implementation(self) -> Asts.ClassImplementationAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_token_left_curly_brace)
        p2 = self.parse_zero_or_more(self.parse_class_member, self.parse_newline)
        p3 = self.parse_once(self.parse_token_right_curly_brace)
        return Asts.ClassImplementationAst(c1, p1, p2, p3)

    def parse_class_member(self) -> Asts.ClassMemberAst:
        p1 = self.parse_once(self.parse_class_attribute)
        return p1

    def parse_class_attribute(self) -> Asts.ClassAttributeAst:
        c1 = self._pos
        p1 = self.parse_zero_or_more(self.parse_annotation, self.parse_newline)
        p2 = self.parse_once(self.parse_identifier)
        p3 = self.parse_once(self.parse_token_colon)
        p4 = self.parse_once(self.parse_type)
        return Asts.ClassAttributeAst(c1, p1, p2, p3, p4)

    # ===== SUPERIMPOSITION =====

    def parse_sup_prototype_functions(self) -> Asts.SupPrototypeFunctionsAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_keyword_sup)
        p2 = self.parse_optional(self.parse_generic_parameters) or Asts.GenericParameterGroupAst(pos=c1)
        p3 = self.parse_once(self.parse_type)
        p4 = self.parse_optional(self.parse_where_block) or Asts.WhereBlockAst(pos=c1)
        p5 = self.parse_once(self.parse_sup_implementation)
        return Asts.SupPrototypeFunctionsAst(c1, p1, p2, p3, p4, p5)

    def parse_sup_prototype_extension(self) -> Asts.SupPrototypeExtensionAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_keyword_sup)
        p2 = self.parse_optional(self.parse_generic_parameters) or Asts.GenericParameterGroupAst(pos=c1)
        p3 = self.parse_once(self.parse_type)
        p4 = self.parse_once(self.parse_keyword_ext)
        p5 = self.parse_once(self.parse_type)
        p6 = self.parse_optional(self.parse_where_block) or Asts.WhereBlockAst(pos=c1)
        p7 = self.parse_once(self.parse_sup_implementation)
        return Asts.SupPrototypeExtensionAst(c1, p1, p2, p3, p4, p5, p6, p7)

    def parse_sup_implementation(self) -> Asts.SupImplementationAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_token_left_curly_brace)
        p2 = self.parse_zero_or_more(self.parse_sup_member, self.parse_newline)
        p3 = self.parse_once(self.parse_token_right_curly_brace)
        return Asts.SupImplementationAst(c1, p1, p2, p3)

    def parse_sup_member(self) -> Asts.SupMemberAst:
        p1 = self.parse_alternate(
            self.parse_sup_method_prototype,
            self.parse_sup_use_statement)
        return p1

    def parse_sup_method_prototype(self) -> Asts.FunctionPrototypeAst:
        p1 = self.parse_once(self.parse_function_prototype)
        return p1

    def parse_sup_use_statement(self) -> Asts.SupUseStatementAst:
        p1 = self.parse_zero_or_more(self.parse_annotation, self.parse_newline)
        p2 = self.parse_once(self.parse_use_statement)
        p2.annotations = p1
        return p2

    # ===== FUNCTIONS =====

    def parse_function_prototype(self) -> Asts.FunctionPrototypeAst:
        p1 = self.parse_alternate(
            self.parse_subroutine_prototype,
            self.parse_coroutine_prototype)
        return p1

    def parse_subroutine_prototype(self) -> Asts.SubroutinePrototypeAst:
        c1 = self._pos
        p1 = self.parse_zero_or_more(self.parse_annotation, self.parse_newline)
        p2 = self.parse_once(self.parse_keyword_fun)
        p3 = self.parse_once(self.parse_identifier)
        p4 = self.parse_optional(self.parse_generic_parameters) or Asts.GenericParameterGroupAst(pos=c1)
        p5 = self.parse_once(self.parse_function_parameters)
        p6 = self.parse_once(self.parse_token_arrow_right)
        p7 = self.parse_once(self.parse_type)
        p8 = self.parse_optional(self.parse_where_block) or Asts.WhereBlockAst(pos=c1)
        p9 = self.parse_once(self.parse_function_implementation)
        return Asts.SubroutinePrototypeAst(c1, p1, p2, p3, p4, p5, p6, p7, p8, p9)

    def parse_coroutine_prototype(self) -> Asts.CoroutinePrototypeAst:
        c1 = self._pos
        p1 = self.parse_zero_or_more(self.parse_annotation, self.parse_newline)
        p2 = self.parse_once(self.parse_keyword_cor)
        p3 = self.parse_once(self.parse_identifier)
        p4 = self.parse_optional(self.parse_generic_parameters) or Asts.GenericParameterGroupAst(pos=c1)
        p5 = self.parse_once(self.parse_function_parameters)
        p6 = self.parse_once(self.parse_token_arrow_right)
        p7 = self.parse_once(self.parse_type)
        p8 = self.parse_optional(self.parse_where_block) or Asts.WhereBlockAst(pos=c1)
        p9 = self.parse_once(self.parse_function_implementation)
        return Asts.CoroutinePrototypeAst(c1, p1, p2, p3, p4, p5, p6, p7, p8, p9)

    def parse_function_implementation(self) -> Asts.FunctionImplementationAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_token_left_curly_brace)
        p2 = self.parse_zero_or_more(self.parse_function_member, self.parse_newline)
        p3 = self.parse_once(self.parse_token_right_curly_brace)
        return Asts.FunctionImplementationAst(c1, p1, p2, p3)

    def parse_function_member(self) -> Asts.FunctionMemberAst:
        p1 = self.parse_once(self.parse_statement)
        return p1

    def parse_function_call_arguments(self) -> Asts.FunctionCallArgumentGroupAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_token_left_parenthesis)
        p2 = self.parse_zero_or_more(self.parse_function_call_argument, self.parse_token_comma)
        p3 = self.parse_once(self.parse_token_right_parenthesis)
        return Asts.FunctionCallArgumentGroupAst(c1, p1, Seq(p2), p3)

    def parse_function_call_argument(self) -> Asts.FunctionCallArgumentAst:
        p1 = self.parse_alternate(
            self.parse_function_call_argument_named,
            self.parse_function_call_argument_unnamed)
        return p1

    def parse_function_call_argument_unnamed(self) -> Asts.FunctionCallArgumentUnnamedAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_convention)
        p2 = self.parse_optional(self.parse_token_double_dot)
        p3 = self.parse_once(self.parse_expression)
        return Asts.FunctionCallArgumentUnnamedAst(c1, p1, p2, p3)

    def parse_function_call_argument_named(self) -> Asts.FunctionCallArgumentNamedAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_identifier)
        p2 = self.parse_once(self.parse_token_assign)
        p3 = self.parse_once(self.parse_convention)
        p4 = self.parse_once(self.parse_expression)
        return Asts.FunctionCallArgumentNamedAst(c1, p1, p2, p3, p4)

    def parse_function_parameters(self) -> Asts.FunctionParameterGroupAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_token_left_parenthesis)
        p2 = self.parse_zero_or_more(self.parse_function_parameter, self.parse_token_comma)
        p3 = self.parse_once(self.parse_token_right_parenthesis)
        return Asts.FunctionParameterGroupAst(c1, p1, p2, p3)

    def parse_function_parameter(self) -> Asts.FunctionParameterAst:
        p1 = self.parse_alternate(
            self.parse_function_parameter_variadic,
            self.parse_function_parameter_optional,
            self.parse_function_parameter_required,
            self.parse_function_parameter_self)
        return p1

    def parse_function_parameter_self(self) -> Asts.FunctionParameterSelfAst:
        c1 = self._pos
        p1 = self.parse_optional(self.parse_keyword_mut)
        p2 = self.parse_once(self.parse_convention)
        p3 = self.parse_once(self.parse_self_keyword)
        return Asts.FunctionParameterSelfAst(c1, p1, p2, p3)

    def parse_function_parameter_required(self) -> Asts.FunctionParameterRequiredAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_local_variable)
        p2 = self.parse_once(self.parse_token_colon)
        p3 = self.parse_once(self.parse_convention)
        p4 = self.parse_once(self.parse_type)
        return Asts.FunctionParameterRequiredAst(c1, p1, p2, p3, p4)

    def parse_function_parameter_optional(self) -> Asts.FunctionParameterOptionalAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_local_variable)
        p2 = self.parse_once(self.parse_token_colon)
        p3 = self.parse_once(self.parse_convention)
        p4 = self.parse_once(self.parse_type)
        p5 = self.parse_once(self.parse_token_assign)
        p6 = self.parse_once(self.parse_expression)
        return Asts.FunctionParameterOptionalAst(c1, p1, p2, p3, p4, p5, p6)

    def parse_function_parameter_variadic(self) -> Asts.FunctionParameterVariadicAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_token_double_dot)
        p2 = self.parse_once(self.parse_local_variable)
        p3 = self.parse_once(self.parse_token_colon)
        p4 = self.parse_once(self.parse_convention)
        p5 = self.parse_once(self.parse_type)
        return Asts.FunctionParameterVariadicAst(c1, p1, p2, p3, p4, p5)

    # ===== GENERICS =====

    def parse_generic_arguments(self) -> Asts.GenericArgumentGroupAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_token_left_square_bracket)
        p2 = self.parse_zero_or_more(self.parse_generic_argument, self.parse_token_comma)
        p3 = self.parse_once(self.parse_token_right_square_bracket)
        return Asts.GenericArgumentGroupAst(c1, p1, p2, p3)

    def parse_generic_argument(self) -> Asts.GenericArgumentAst:
        p1 = self.parse_alternate(
            self.parse_generic_type_argument_named,
            self.parse_generic_type_argument_unnamed,
            self.parse_generic_comp_argument_named,
            self.parse_generic_comp_argument_unnamed)
        return p1

    def parse_generic_type_argument_named(self) -> Asts.GenericTypeArgumentNamedAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_upper_identifier)
        p2 = self.parse_once(self.parse_token_assign)
        p3 = self.parse_once(self.parse_type)
        return Asts.GenericTypeArgumentNamedAst(c1, Asts.TypeSingleAst.from_identifier(p1), p2, p3)

    def parse_generic_type_argument_unnamed(self) -> Asts.GenericTypeArgumentUnnamedAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_type)
        return Asts.GenericTypeArgumentUnnamedAst(c1, p1)

    def parse_generic_comp_argument_named(self) -> Asts.GenericCompArgumentNamedAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_identifier)
        p2 = self.parse_once(self.parse_token_assign)
        p3 = self.parse_once(self.parse_global_constant_value)
        return Asts.GenericCompArgumentNamedAst(c1, Asts.TypeSingleAst.from_identifier(p1), p2, p3)

    def parse_generic_comp_argument_unnamed(self) -> Asts.GenericCompArgumentUnnamedAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_global_constant_value)
        return Asts.GenericCompArgumentUnnamedAst(c1, p1)

    def parse_generic_parameters(self) -> Asts.GenericParameterGroupAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_token_left_square_bracket)
        p2 = self.parse_one_or_more(self.parse_generic_parameter, self.parse_token_comma)
        p3 = self.parse_once(self.parse_token_right_square_bracket)
        return Asts.GenericParameterGroupAst(c1, p1, p2, p3)

    def parse_generic_parameter(self) -> Asts.GenericParameterAst:
        p1 = self.parse_alternate(
            self.parse_generic_type_parameter_variadic,
            self.parse_generic_type_parameter_optional,
            self.parse_generic_type_parameter_required,
            self.parse_generic_comp_parameter_variadic,
            self.parse_generic_comp_parameter_optional,
            self.parse_generic_comp_parameter_required)
        return p1

    def parse_generic_type_parameter_required(self) -> Asts.GenericTypeParameterRequiredAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_upper_identifier)
        p2 = self.parse_optional(self.parse_generic_inline_constraints) or Asts.GenericTypeParameterInlineConstraintsAst(pos=c1)
        return Asts.GenericTypeParameterRequiredAst(c1, Asts.TypeSingleAst.from_identifier(p1), p2)

    def parse_generic_type_parameter_optional(self) -> Asts.GenericTypeParameterOptionalAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_upper_identifier)
        p2 = self.parse_optional(self.parse_generic_inline_constraints) or Asts.GenericTypeParameterInlineConstraintsAst(pos=c1)
        p3 = self.parse_once(self.parse_token_assign)
        p4 = self.parse_once(self.parse_type)
        return Asts.GenericTypeParameterOptionalAst(c1, Asts.TypeSingleAst.from_identifier(p1), p2, p3, p4)

    def parse_generic_type_parameter_variadic(self) -> Asts.GenericTypeParameterVariadicAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_token_double_dot)
        p2 = self.parse_once(self.parse_upper_identifier)
        p3 = self.parse_optional(self.parse_generic_inline_constraints) or Asts.GenericTypeParameterInlineConstraintsAst(pos=c1)
        return Asts.GenericTypeParameterVariadicAst(c1, p1, Asts.TypeSingleAst.from_identifier(p2), p3)

    def parse_generic_comp_parameter_required(self) -> Asts.GenericCompParameterRequiredAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_keyword_cmp)
        p2 = self.parse_once(self.parse_identifier)
        p3 = self.parse_once(self.parse_token_colon)
        p4 = self.parse_once(self.parse_type)
        return Asts.GenericCompParameterRequiredAst(c1, p1, Asts.TypeSingleAst.from_identifier(p2), p3, p4)

    def parse_generic_comp_parameter_optional(self) -> Asts.GenericCompParameterOptionalAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_keyword_cmp)
        p2 = self.parse_once(self.parse_identifier)
        p3 = self.parse_once(self.parse_token_colon)
        p4 = self.parse_once(self.parse_type)
        p5 = self.parse_once(self.parse_token_assign)
        p6 = self.parse_once(self.parse_global_constant_value)
        return Asts.GenericCompParameterOptionalAst(c1, p1, Asts.TypeSingleAst.from_identifier(p2), p3, p4, p5, p6)

    def parse_generic_comp_parameter_variadic(self) -> Asts.GenericCompParameterVariadicAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_keyword_cmp)
        p2 = self.parse_once(self.parse_token_double_dot)
        p3 = self.parse_once(self.parse_identifier)
        p4 = self.parse_once(self.parse_token_colon)
        p5 = self.parse_once(self.parse_type)
        return Asts.GenericCompParameterVariadicAst(c1, p1, p2, Asts.TypeSingleAst.from_identifier(p3), p4, p5)

    def parse_generic_inline_constraints(self) -> Asts.GenericTypeParameterInlineConstraintsAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_token_colon)
        p2 = self.parse_one_or_more(self.parse_type, self.parse_token_comma)
        return Asts.GenericTypeParameterInlineConstraintsAst(c1, p1, p2)

    # ===== WHERE =====

    def parse_where_block(self) -> Asts.WhereBlockAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_keyword_where)
        p2 = self.parse_once(self.parse_where_block_constraints_group)
        return Asts.WhereBlockAst(c1, p1, p2)

    def parse_where_block_constraints_group(self) -> Asts.WhereConstraintsGroupAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_token_left_square_bracket)
        p2 = self.parse_one_or_more(self.parse_where_block_constraints, self.parse_token_comma)
        p3 = self.parse_once(self.parse_token_right_square_bracket)
        return Asts.WhereConstraintsGroupAst(c1, p1, p2, p3)

    def parse_where_block_constraints(self) -> Asts.WhereConstraintsAst:
        c1 = self._pos
        p1 = self.parse_one_or_more(self.parse_type, self.parse_token_comma)
        p2 = self.parse_once(self.parse_token_colon)
        p3 = self.parse_once(self.parse_type)
        return Asts.WhereConstraintsAst(c1, p1, p2, p3)

    # ===== ANNOTATIONS =====

    def parse_annotation(self) -> Asts.AnnotationAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_token_at)
        p2 = self.parse_once(self.parse_identifier)
        return Asts.AnnotationAst(c1, p1, p2)

    # ===== EXPRESSIONS =====

    def parse_expression(self) -> Asts.ExpressionAst:
        p1 = self.parse_once(self.parse_binary_expression_precedence_level_1)
        return p1

    def parse_binary_expression_precedence_level_n_rhs(self, op, rhs) -> Tuple[Asts.TokenAst, Asts.ExpressionAst]:
        p1 = self.parse_once(op)
        p2 = self.parse_once(rhs)
        return p1, p2

    def parse_binary_expression_precedence_level_n(self, lhs, op, rhs) -> Asts.BinaryExpressionAst:
        c1 = self._pos
        p1 = self.parse_once(lhs)
        p2 = self.parse_optional(lambda: self.parse_binary_expression_precedence_level_n_rhs(op, rhs))
        return Asts.BinaryExpressionAst(c1, p1, p2[0], p2[1]) if p2 else p1

    def parse_binary_expression_precedence_level_1(self) -> Asts.ExpressionAst:
        return self.parse_binary_expression_precedence_level_n(self.parse_binary_expression_precedence_level_2, self.parse_binary_op_precedence_level_1, self.parse_binary_expression_precedence_level_1)

    def parse_binary_expression_precedence_level_2(self) -> Asts.ExpressionAst:
        return self.parse_binary_expression_precedence_level_n(self.parse_binary_expression_precedence_level_3, self.parse_binary_op_precedence_level_2, self.parse_binary_expression_precedence_level_2)

    def parse_binary_expression_precedence_level_3(self) -> Asts.ExpressionAst:
        return self.parse_binary_expression_precedence_level_n(self.parse_binary_expression_precedence_level_4, self.parse_binary_op_precedence_level_3, self.parse_pattern_group_destructure)

    def parse_binary_expression_precedence_level_4(self) -> Asts.ExpressionAst:
        return self.parse_binary_expression_precedence_level_n(self.parse_binary_expression_precedence_level_5, self.parse_binary_op_precedence_level_4, self.parse_binary_expression_precedence_level_4)

    def parse_binary_expression_precedence_level_5(self) -> Asts.ExpressionAst:
        return self.parse_binary_expression_precedence_level_n(self.parse_binary_expression_precedence_level_6, self.parse_binary_op_precedence_level_5, self.parse_binary_expression_precedence_level_5)

    def parse_binary_expression_precedence_level_6(self) -> Asts.ExpressionAst:
        return self.parse_binary_expression_precedence_level_n(self.parse_unary_expression, self.parse_binary_op_precedence_level_6, self.parse_binary_expression_precedence_level_6)

    def parse_unary_expression(self) -> Asts.ExpressionAst:
        c1 = self._pos
        p1 = self.parse_zero_or_more(self.parse_unary_op, self.parse_nothing)
        p2 = self.parse_once(self.parse_postfix_expression)
        return reduce(lambda acc, x: Asts.UnaryExpressionAst(c1, x, acc), p1.reverse().list(), p2)

    def parse_postfix_expression(self) -> Asts.ExpressionAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_primary_expression)
        p2 = self.parse_zero_or_more(self.parse_postfix_op, self.parse_nothing)
        return reduce(lambda acc, x: Asts.PostfixExpressionAst(c1, acc, x), p2.list(), p1)

    def parse_primary_expression(self) -> Asts.ExpressionAst:
        p1 = self.parse_alternate(
            self.parse_literal,
            self.parse_object_initializer,
            self.parse_parenthesized_expression,
            self.parse_case_expression,
            self.parse_loop_expression,
            self.parse_gen_expression,
            self.parse_type,
            self.parse_self_keyword,
            self.parse_identifier,
            self.parse_inner_scope,
            self.parse_token_double_dot)
        return p1

    def parse_parenthesized_expression(self) -> Asts.ParenthesizedExpressionAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_token_left_parenthesis)
        p2 = self.parse_once(self.parse_expression)
        p3 = self.parse_once(self.parse_token_right_parenthesis)
        return Asts.ParenthesizedExpressionAst(c1, p1, p2, p3)

    def parse_self_keyword(self) -> Asts.IdentifierAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_keyword_self_value)
        return Asts.IdentifierAst(c1, p1.token_data)

    # ===== EXPRESSION STATEMENTS =====

    def parse_case_expression(self) -> Asts.CaseExpressionAst:
        p1 = self.parse_alternate(
            self.parse_case_expression_patterns,
            self.parse_case_expression_simple)
        return p1

    def parse_case_expression_patterns(self) -> Asts.CaseExpressionAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_keyword_case)
        p2 = self.parse_once(self.parse_expression)
        p3 = self.parse_once(self.parse_keyword_of)
        p4 = self.parse_one_or_more(self.parse_case_expression_branch, self.parse_newline)
        return Asts.CaseExpressionAst(c1, p1, p2, p3, p4)

    def parse_case_expression_simple(self) -> Asts.CaseExpressionAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_keyword_case)
        p2 = self.parse_once(self.parse_expression)
        p3 = self.parse_once(self.parse_inner_scope)
        p4 = self.parse_zero_or_more(self.parse_case_expression_branch_simple, self.parse_newline)
        return Asts.CaseExpressionAst.from_simple(c1, p1, p2, p3, p4)

    def parse_loop_expression(self) -> Asts.LoopExpressionAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_keyword_loop)
        p2 = self.parse_once(self.parse_loop_expression_condition)
        p3 = self.parse_once(self.parse_inner_scope)
        p4 = self.parse_optional(self.parse_loop_else_statement)
        return Asts.LoopExpressionAst(c1, p1, p2, p3, p4)

    def parse_loop_expression_condition(self) -> Asts.LoopConditionAst:
        p1 = self.parse_alternate(
            self.parse_loop_expression_condition_iterable,
            self.parse_loop_expression_condition_boolean)
        return p1

    def parse_loop_expression_condition_boolean(self) -> Asts.LoopConditionBooleanAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_expression)
        return Asts.LoopConditionBooleanAst(c1, p1)

    def parse_loop_expression_condition_iterable(self) -> Asts.LoopConditionIterableAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_local_variable)
        p2 = self.parse_once(self.parse_keyword_in)
        p3 = self.parse_once(self.parse_expression)
        return Asts.LoopConditionIterableAst(c1, p1, p2, p3)

    def parse_loop_else_statement(self) -> Asts.LoopElseStatementAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_keyword_else)
        p2 = self.parse_once(self.parse_inner_scope)
        return Asts.LoopElseStatementAst(c1, p1, p2)

    def parse_gen_expression(self) -> Asts.GenExpressionAst:
        p1 = self.parse_alternate(
            self.parse_gen_expression_unroll,
            self.parse_gen_expression_normal)
        return p1

    def parse_gen_expression_normal(self) -> Asts.GenExpressionAst:
        p1 = self.parse_alternate(
            self.parse_gen_expression_normal_with_expression,
            self.parse_gen_expression_normal_no_expression)
        return p1

    def parse_gen_expression_normal_no_expression(self) -> Asts.GenExpressionAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_keyword_gen)
        return Asts.GenExpressionAst(c1, p1, None, Asts.ConventionMovAst(p1.pos), None)

    def parse_gen_expression_normal_with_expression(self) -> Asts.GenExpressionAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_keyword_gen)
        p2 = self.parse_once(self.parse_convention)
        p3 = self.parse_once(self.parse_expression)
        return Asts.GenExpressionAst(c1, p1, None, p2, p3)

    def parse_gen_expression_unroll(self) -> Asts.GenExpressionAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_keyword_gen)
        p2 = self.parse_once(self.parse_keyword_with)
        p3 = self.parse_once(self.parse_expression)
        return Asts.GenExpressionAst(c1, p1, p2, Asts.ConventionMovAst(p3.pos), p3)

    # ===== STATEMENTS =====

    def parse_ret_statement(self) -> Asts.RetStatementAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_keyword_ret)
        p2 = self.parse_optional(self.parse_expression)
        return Asts.RetStatementAst(c1, p1, p2)

    def parse_exit_statement(self) -> Asts.LoopControlFlowStatementAst:
        c1 = self._pos
        p1 = self.parse_one_or_more(self.parse_keyword_exit, self.parse_nothing)
        p2 = self.parse_optional(self.parse_exit_statement_final_action)
        return Asts.LoopControlFlowStatementAst(c1, p1, p2)

    def parse_exit_statement_final_action(self) -> Asts.TokenAst | Asts.ExpressionAst:
        p1 = self.parse_alternate(
            self.parse_keyword_skip,
            self.parse_expression)
        return p1

    def parse_skip_statement(self) -> Asts.LoopControlFlowStatementAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_keyword_skip)
        return Asts.LoopControlFlowStatementAst(c1, Seq(), p1)

    def parse_pin_statement(self) -> Asts.PinStatementAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_keyword_pin)
        p2 = self.parse_one_or_more(self.parse_expression, self.parse_token_comma)
        return Asts.PinStatementAst(c1, p1, p2)

    def parse_rel_statement(self) -> Asts.RelStatementAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_keyword_rel)
        p2 = self.parse_one_or_more(self.parse_expression, self.parse_token_comma)
        return Asts.RelStatementAst(c1, p1, p2)

    def parse_inner_scope(self) -> Asts.InnerScopeAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_token_left_curly_brace)
        p2 = self.parse_zero_or_more(self.parse_statement, self.parse_newline)
        p3 = self.parse_once(self.parse_token_right_curly_brace)
        return Asts.InnerScopeAst(c1, p1, p2, p3)

    def parse_statement(self) -> Asts.StatementAst:
        p1 = self.parse_alternate(
            self.parse_use_statement,
            self.parse_let_statement,
            self.parse_ret_statement,
            self.parse_exit_statement,
            self.parse_skip_statement,
            self.parse_pin_statement,
            self.parse_rel_statement,
            self.parse_assignment_statement,
            self.parse_expression)
        return p1

    # ===== TYPEDEFS =====

    def parse_global_use_statement(self) -> Asts.UseStatementAst:
        p1 = self.parse_zero_or_more(self.parse_annotation, self.parse_newline)
        p2 = self.parse_use_statement()
        p2.annotations = p1
        return p2

    def parse_use_statement(self) -> Asts.UseStatementAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_keyword_use)
        p2 = self.parse_once(self.parse_upper_identifier)
        p3 = self.parse_optional(self.parse_generic_parameters) or Asts.GenericParameterGroupAst(pos=c1)
        p4 = self.parse_once(self.parse_token_assign)
        p5 = self.parse_once(self.parse_type)
        return Asts.UseStatementAst(c1, Seq(), p1, Asts.TypeSingleAst.from_identifier(p2), p3, p4, p5)

    # ===== LET-DECLARATIONS =====

    def parse_global_constant(self) -> Asts.GlobalConstantAst:
        c1 = self._pos
        p1 = self.parse_zero_or_more(self.parse_annotation, self.parse_newline)
        p2 = self.parse_once(self.parse_keyword_cmp)
        p3 = self.parse_once(self.parse_identifier)
        p4 = self.parse_once(self.parse_token_colon)
        p5 = self.parse_once(self.parse_type)
        p6 = self.parse_once(self.parse_token_assign)
        p7 = self.parse_once(self.parse_global_constant_value)
        return Asts.GlobalConstantAst(c1, p1, p2, p3, p4, p5, p6, p7)

    def parse_let_statement(self) -> Asts.LetStatementAst:
        p1 = self.parse_alternate(
            self.parse_let_statement_initialized,
            self.parse_let_statement_uninitialized)
        return p1

    def parse_let_statement_initialized(self) -> Asts.LetStatementInitializedAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_keyword_let)
        p2 = self.parse_once(self.parse_local_variable)
        p3 = self.parse_once(self.parse_token_assign)
        p4 = self.parse_once(self.parse_expression)
        return Asts.LetStatementInitializedAst(c1, p1, p2, p3, p4)

    def parse_let_statement_uninitialized(self) -> Asts.LetStatementUninitializedAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_keyword_let)
        p2 = self.parse_once(self.parse_local_variable)
        p3 = self.parse_once(self.parse_token_colon)
        p4 = self.parse_once(self.parse_convention)
        p5 = self.parse_once(self.parse_type)
        return Asts.LetStatementUninitializedAst(c1, p1, p2, p3, p4, p5)

    def parse_local_variable(self) -> Asts.LocalVariableAst:
        p1 = self.parse_alternate(
            self.parse_local_variable_destructure_array,
            self.parse_local_variable_destructure_tuple,
            self.parse_local_variable_destructure_object,
            self.parse_local_variable_single_identifier)
        return p1

    def parse_local_variable_destructure_skip_argument(self) -> Asts.LocalVariableDestructureSkip1ArgumentAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_token_underscore)
        return Asts.LocalVariableDestructureSkip1ArgumentAst(c1, p1)

    def parse_local_variable_destructure_skip_arguments(self) -> Asts.LocalVariableDestructureSkipNArgumentsAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_token_double_dot)
        p2 = self.parse_optional(self.parse_local_variable_single_identifier)
        return Asts.LocalVariableDestructureSkipNArgumentsAst(c1, p1, p2)

    def parse_local_variable_single_identifier(self) -> Asts.LocalVariableSingleIdentifierAst:
        c1 = self._pos
        p1 = self.parse_optional(self.parse_keyword_mut)
        p2 = self.parse_once(self.parse_identifier)
        p3 = self.parse_optional(self.parse_local_variable_single_identifier_alias)
        return Asts.LocalVariableSingleIdentifierAst(c1, p1, p2, p3)

    def parse_local_variable_single_identifier_alias(self) -> Asts.LocalVariableSingleIdentifierAliasAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_keyword_as)
        p2 = self.parse_once(self.parse_identifier)
        return Asts.LocalVariableSingleIdentifierAliasAst(c1, p1, p2)

    def parse_local_variable_destructure_array(self) -> Asts.LocalVariableDestructureArrayAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_token_left_square_bracket)
        p2 = self.parse_one_or_more(self.parse_local_variable_nested_for_destructure_array, self.parse_token_comma)
        p3 = self.parse_once(self.parse_token_right_square_bracket)
        return Asts.LocalVariableDestructureArrayAst(c1, p1, p2, p3)

    def parse_local_variable_destructure_tuple(self) -> Asts.LocalVariableDestructureTupleAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_token_left_parenthesis)
        p2 = self.parse_one_or_more(self.parse_local_variable_nested_for_destructure_tuple, self.parse_token_comma)
        p3 = self.parse_once(self.parse_token_right_parenthesis)
        return Asts.LocalVariableDestructureTupleAst(c1, p1, p2, p3)

    def parse_local_variable_destructure_object(self) -> Asts.LocalVariableDestructureObjectAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_type_simple)
        p2 = self.parse_once(self.parse_token_left_parenthesis)
        p3 = self.parse_zero_or_more(self.parse_local_variable_nested_for_destructure_object, self.parse_token_comma)
        p4 = self.parse_once(self.parse_token_right_parenthesis)
        return Asts.LocalVariableDestructureObjectAst(c1, p1, p2, p3, p4)

    def parse_local_variable_attribute_binding(self) -> Asts.LocalVariableAttributeBindingAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_identifier)
        p2 = self.parse_once(self.parse_token_assign)
        p3 = self.parse_once(self.parse_local_variable_nested_for_attribute_binding)
        return Asts.LocalVariableAttributeBindingAst(c1, p1, p2, p3)

    def parse_local_variable_nested_for_destructure_array(self) -> Asts.LocalVariableNestedForDestructureArrayAst:
        p1 = self.parse_alternate(
            self.parse_local_variable_destructure_array,
            self.parse_local_variable_destructure_tuple,
            self.parse_local_variable_destructure_object,
            self.parse_local_variable_single_identifier,
            self.parse_local_variable_destructure_skip_arguments,
            self.parse_local_variable_destructure_skip_argument)
        return p1

    def parse_local_variable_nested_for_destructure_tuple(self) -> Asts.LocalVariableNestedForDestructureTupleAst:
        p1 = self.parse_alternate(
            self.parse_local_variable_destructure_array,
            self.parse_local_variable_destructure_tuple,
            self.parse_local_variable_destructure_object,
            self.parse_local_variable_single_identifier,
            self.parse_local_variable_destructure_skip_arguments,
            self.parse_local_variable_destructure_skip_argument)
        return p1

    def parse_local_variable_nested_for_destructure_object(self) -> Asts.LocalVariableNestedForDestructureObjectAst:
        p1 = self.parse_alternate(
            self.parse_local_variable_attribute_binding,
            self.parse_local_variable_single_identifier,
            self.parse_local_variable_destructure_skip_arguments)
        return p1

    def parse_local_variable_nested_for_attribute_binding(self) -> Asts.LocalVariableNestedForAttributeBindingAst:
        p1 = self.parse_alternate(
            self.parse_local_variable_destructure_array,
            self.parse_local_variable_destructure_tuple,
            self.parse_local_variable_destructure_object,
            self.parse_local_variable_single_identifier)
        return p1

    # ===== ASSIGNMENT =====

    def parse_assignment_statement(self) -> Asts.AssignmentStatementAst:
        c1 = self._pos
        p1 = self.parse_one_or_more(self.parse_expression, self.parse_token_comma)
        p2 = self.parse_once(self.parse_token_assign)
        p3 = self.parse_one_or_more(self.parse_expression, self.parse_token_comma)
        return Asts.AssignmentStatementAst(c1, p1, p2, p3)

    # ===== PATTERNS =====

    def parse_case_expression_branch_simple(self) -> Asts.CaseExpressionBranchAst:
        p1 = self.parse_alternate(
            self.parse_pattern_statement_flavour_else_case,
            self.parse_pattern_statement_flavour_else)
        return p1

    def parse_case_expression_branch(self) -> Asts.CaseExpressionBranchAst:
        p1 = self.parse_alternate(
            self.parse_pattern_statement_flavour_destructuring,
            self.parse_pattern_statement_flavour_non_destructuring,
            self.parse_pattern_statement_flavour_else_case,
            self.parse_pattern_statement_flavour_else)
        return p1

    def parse_pattern_statement_flavour_destructuring(self) -> Asts.CaseExpressionBranchAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_keyword_is)
        p2 = self.parse_one_or_more(self.parse_pattern_group_destructure, self.parse_token_comma)
        p3 = self.parse_optional(self.parse_pattern_guard)
        p4 = self.parse_once(self.parse_inner_scope)
        return Asts.CaseExpressionBranchAst(c1, p1, p2, p3, p4)

    def parse_pattern_statement_flavour_non_destructuring(self) -> Asts.CaseExpressionBranchAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_boolean_comparison_op)
        p2 = self.parse_one_or_more(self.parse_pattern_variant_expression, self.parse_token_comma)
        p3 = self.parse_once(self.parse_inner_scope)
        return Asts.CaseExpressionBranchAst(c1, p1, p2, None, p3)

    def parse_pattern_statement_flavour_else_case(self) -> Asts.CaseExpressionBranchAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_pattern_variant_else_case)
        return Asts.CaseExpressionBranchAst.from_else_to_else_case(c1, p1)

    def parse_pattern_statement_flavour_else(self) -> Asts.CaseExpressionBranchAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_pattern_variant_else)
        p2 = self.parse_once(self.parse_inner_scope)
        return Asts.CaseExpressionBranchAst(c1, None, Seq([p1]), None, p2)

    def parse_pattern_group_destructure(self) -> Asts.PatternGroupDestructureAst:
        p1 = self.parse_alternate(
            self.parse_pattern_variant_destructure_array,
            self.parse_pattern_variant_destructure_tuple,
            self.parse_pattern_variant_destructure_object)
        return p1

    def parse_pattern_variant_skip_argument(self) -> Asts.PatternVariantDestructureSkip1ArgumentAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_token_underscore)
        return Asts.PatternVariantDestructureSkip1ArgumentAst(c1, p1)

    def parse_pattern_variant_skip_arguments(self) -> Asts.PatternVariantDestructureSkipNArgumentsAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_token_double_dot)
        p2 = self.parse_optional(self.parse_pattern_variant_single_identifier)
        return Asts.PatternVariantDestructureSkipNArgumentsAst(c1, p1, p2)

    def parse_pattern_variant_single_identifier(self) -> Asts.PatternVariantSingleIdentifierAst:
        c1 = self._pos
        p1 = self.parse_optional(self.parse_keyword_mut)
        p2 = self.parse_once(self.parse_identifier)
        p3 = self.parse_optional(self.parse_local_variable_single_identifier_alias)
        return Asts.PatternVariantSingleIdentifierAst(c1, p1, p2, p3)

    def parse_pattern_variant_destructure_tuple(self) -> Asts.PatternVariantDestructureTupleAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_token_left_parenthesis)
        p2 = self.parse_one_or_more(self.parse_pattern_variant_nested_for_destructure_tuple, self.parse_token_comma)
        p3 = self.parse_once(self.parse_token_right_parenthesis)
        return Asts.PatternVariantDestructureTupleAst(c1, p1, p2, p3)

    def parse_pattern_variant_destructure_array(self) -> Asts.PatternVariantDestructureArrayAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_token_left_square_bracket)
        p2 = self.parse_one_or_more(self.parse_pattern_variant_nested_for_destructure_array, self.parse_token_comma)
        p3 = self.parse_once(self.parse_token_right_square_bracket)
        return Asts.PatternVariantDestructureArrayAst(c1, p1, p2, p3)

    def parse_pattern_variant_destructure_object(self) -> Asts.PatternVariantDestructureObjectAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_type_simple)
        p2 = self.parse_once(self.parse_token_left_parenthesis)
        p3 = self.parse_zero_or_more(self.parse_pattern_variant_nested_for_destructure_object, self.parse_token_comma)
        p4 = self.parse_once(self.parse_token_right_parenthesis)
        return Asts.PatternVariantDestructureObjectAst(c1, p1, p2, p3, p4)

    def parse_pattern_variant_attribute_binding(self) -> Asts.PatternVariantAttributeBindingAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_identifier)
        p2 = self.parse_once(self.parse_token_assign)
        p3 = self.parse_once(self.parse_pattern_variant_nested_for_attribute_binding)
        return Asts.PatternVariantAttributeBindingAst(c1, p1, p2, p3)

    def parse_pattern_variant_literal(self) -> Asts.PatternVariantLiteralAst:
        c1 = self._pos
        p1 = self.parse_alternate(
            self.parse_literal_float,
            self.parse_literal_integer,
            self.parse_literal_string,
            self.parse_literal_boolean)
        return Asts.PatternVariantLiteralAst(c1, p1)

    def parse_pattern_variant_expression(self) -> Asts.PatternVariantExpressionAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_expression)
        return Asts.PatternVariantExpressionAst(c1, p1)

    def parse_pattern_variant_else(self) -> Asts.PatternVariantElseAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_keyword_else)
        return Asts.PatternVariantElseAst(c1, p1)

    def parse_pattern_variant_else_case(self) -> Asts.PatternVariantElseCaseAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_keyword_else)
        p2 = self.parse_once(self.parse_case_expression)
        return Asts.PatternVariantElseCaseAst(c1, p1, p2)

    def parse_pattern_variant_nested_for_destructure_tuple(self) -> Asts.PatternVariantNestedForDestructureTupleAst:
        p1 = self.parse_alternate(
            self.parse_pattern_variant_destructure_array,
            self.parse_pattern_variant_destructure_tuple,
            self.parse_pattern_variant_destructure_object,
            self.parse_pattern_variant_single_identifier,
            self.parse_pattern_variant_literal,
            self.parse_pattern_variant_skip_arguments,
            self.parse_pattern_variant_skip_argument)
        return p1

    def parse_pattern_variant_nested_for_destructure_array(self) -> Asts.PatternVariantNestedForDestructureArrayAst:
        p1 = self.parse_alternate(
            self.parse_pattern_variant_destructure_array,
            self.parse_pattern_variant_destructure_tuple,
            self.parse_pattern_variant_destructure_object,
            self.parse_pattern_variant_single_identifier,
            self.parse_pattern_variant_literal,
            self.parse_pattern_variant_skip_arguments,
            self.parse_pattern_variant_skip_argument)
        return p1

    def parse_pattern_variant_nested_for_destructure_object(self) -> Asts.PatternVariantNestedForDestructureObjectAst:
        p1 = self.parse_alternate(
            self.parse_pattern_variant_attribute_binding,
            self.parse_pattern_variant_single_identifier,
            self.parse_pattern_variant_skip_arguments)
        return p1

    def parse_pattern_variant_nested_for_attribute_binding(self) -> Asts.PatternVariantNestedForAttributeBindingAst:
        p1 = self.parse_alternate(
            self.parse_pattern_variant_destructure_array,
            self.parse_pattern_variant_destructure_tuple,
            self.parse_pattern_variant_destructure_object,
            self.parse_pattern_variant_literal)
        return p1

    def parse_pattern_guard(self) -> Asts.PatternGuardAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_keyword_and)
        p2 = self.parse_once(self.parse_expression)
        return Asts.PatternGuardAst(c1, p1, p2)

    # ===== OPERATORS =====

    def parse_binary_op_precedence_level_1(self) -> Asts.TokenAst:
        p1 = self.parse_once(self.parse_keyword_or)
        return p1

    def parse_binary_op_precedence_level_2(self) -> Asts.TokenAst:
        p1 = self.parse_once(self.parse_keyword_and)
        return p1

    def parse_binary_op_precedence_level_3(self) -> Asts.TokenAst:
        p1 = self.parse_once(self.parse_keyword_is)
        return p1

    def parse_binary_op_precedence_level_4(self) -> Asts.TokenAst:
        p1 = self.parse_alternate(
            self.parse_token_equals,
            self.parse_token_not_equals,
            self.parse_token_less_than_or_equals,
            self.parse_token_greater_than_or_equals,
            self.parse_token_less_than,
            self.parse_token_greater_than,
            self.parse_token_spaceship)
        return p1

    def parse_binary_op_precedence_level_5(self) -> Asts.TokenAst:
        p1 = self.parse_alternate(
            self.parse_token_plus,
            self.parse_token_minus,
            self.parse_token_plus_assign,
            self.parse_token_minus_assign)
        return p1

    def parse_binary_op_precedence_level_6(self) -> Asts.TokenAst:
        p1 = self.parse_alternate(
            self.parse_token_multiply,
            self.parse_token_divide,
            self.parse_token_remainder,
            self.parse_token_modulo,
            self.parse_token_exponent,
            self.parse_token_multiply_assign,
            self.parse_token_divide_assign,
            self.parse_token_remainder_assign,
            self.parse_token_modulo_assign,
            self.parse_token_exponent_assign)
        return p1

    def parse_boolean_comparison_op(self) -> Asts.TokenAst:
        p1 = self.parse_alternate(
            self.parse_token_equals,
            self.parse_token_not_equals,
            self.parse_token_less_than_or_equals,
            self.parse_token_greater_than_or_equals,
            self.parse_token_less_than,
            self.parse_token_greater_than)
        return p1

    def parse_unary_op(self) -> Asts.UnaryExpressionOperatorAsyncAst:
        p1 = self.parse_once(self.parse_unary_op_async_call)
        return p1

    def parse_unary_op_async_call(self) -> Asts.UnaryExpressionOperatorAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_keyword_async)
        return Asts.UnaryExpressionOperatorAsyncAst(c1, p1)

    def parse_postfix_op(self) -> Asts.PostfixExpressionOperatorAst:
        p1 = self.parse_alternate(
            self.parse_postfix_op_function_call,
            self.parse_postfix_op_not_keyword,
            self.parse_postfix_op_step_keyword,
            self.parse_postfix_op_member_access,
            self.parse_postfix_op_early_return)
        return p1

    def parse_postfix_op_function_call(self) -> Asts.PostfixExpressionOperatorFunctionCallAst:
        c1 = self._pos
        p1 = self.parse_optional(self.parse_generic_arguments) or Asts.GenericArgumentGroupAst(pos=c1)
        p2 = self.parse_once(self.parse_function_call_arguments)
        p3 = self.parse_optional(self.parse_token_double_dot)
        return Asts.PostfixExpressionOperatorFunctionCallAst(c1, p1, p2, p3)

    def parse_postfix_op_member_access(self) -> Asts.PostfixExpressionOperatorMemberAccessAst:
        p1 = self.parse_alternate(
            self.parse_postfix_op_member_access_runtime,
            self.parse_postfix_op_member_access_static)
        return p1

    def parse_postfix_op_member_access_runtime(self) -> Asts.PostfixExpressionOperatorMemberAccessAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_token_dot)
        p2 = self.parse_alternate(
            self.parse_identifier,
            self.parse_lexeme_dec_integer)
        return Asts.PostfixExpressionOperatorMemberAccessAst(c1, p1, p2)

    def parse_postfix_op_member_access_static(self) -> Asts.PostfixExpressionOperatorMemberAccessAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_token_double_colon)
        p2 = self.parse_once(self.parse_identifier)
        return Asts.PostfixExpressionOperatorMemberAccessAst(c1, p1, p2)

    def parse_postfix_op_early_return(self) -> Asts.PostfixExpressionOperatorEarlyReturnAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_token_question_mark)
        return Asts.PostfixExpressionOperatorEarlyReturnAst(c1, p1)

    def parse_postfix_op_not_keyword(self) -> Asts.PostfixExpressionOperatorNotKeywordAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_token_dot)
        p2 = self.parse_once(self.parse_keyword_not)
        return Asts.PostfixExpressionOperatorNotKeywordAst(c1, p1, p2)

    def parse_postfix_op_step_keyword(self) -> Asts.PostfixExpressionOperatorStepKeywordAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_token_dot)
        p2 = self.parse_once(self.parse_keyword_step)
        return Asts.PostfixExpressionOperatorStepKeywordAst(c1, p1, p2)

    # ===== CONVENTIONS =====

    def parse_convention(self) -> Asts.ConventionAst:
        p1 = self.parse_alternate(
            self.parse_convention_mut,
            self.parse_convention_ref,
            self.parse_convention_mov)
        return p1

    def parse_convention_mov(self) -> Asts.ConventionMovAst:
        c1 = self._pos
        return Asts.ConventionMovAst(c1)

    def parse_convention_ref(self) -> Asts.ConventionRefAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_token_ampersand)
        return Asts.ConventionRefAst(c1, p1)

    def parse_convention_mut(self) -> Asts.ConventionMutAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_token_ampersand)
        p2 = self.parse_once(self.parse_keyword_mut)
        return Asts.ConventionMutAst(c1, p1, p2)

    # ===== OBJECT INITIALIZATION =====

    def parse_object_initializer(self) -> Asts.ObjectInitializerAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_type_simple)
        p2 = self.parse_once(self.parse_object_initializer_arguments)
        return Asts.ObjectInitializerAst(c1, p1, p2)

    def parse_object_initializer_arguments(self) -> Asts.ObjectInitializerArgumentGroupAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_token_left_parenthesis)
        p2 = self.parse_zero_or_more(self.parse_object_initializer_argument, self.parse_token_comma)
        p3 = self.parse_once(self.parse_token_right_parenthesis)
        return Asts.ObjectInitializerArgumentGroupAst(c1, p1, p2, p3)

    def parse_object_initializer_argument(self) -> Asts.ObjectInitializerArgumentAst:
        p1 = self.parse_alternate(
            self.parse_object_initializer_argument_named,
            self.parse_object_initializer_argument_unnamed)
        return p1

    def parse_object_initializer_argument_unnamed(self) -> Asts.ObjectInitializerArgumentUnnamedAst:
        c1 = self._pos
        p1 = self.parse_optional(self.parse_token_double_dot)
        p2 = self.parse_once(self.parse_identifier)
        return Asts.ObjectInitializerArgumentUnnamedAst(c1, p1, p2)

    def parse_object_initializer_argument_named(self) -> Asts.ObjectInitializerArgumentNamedAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_identifier)
        p2 = self.parse_once(self.parse_token_assign)
        p3 = self.parse_once(self.parse_expression)
        return Asts.ObjectInitializerArgumentNamedAst(c1, p1, p2, p3)

    # ===== LAMBDAS =====

    # @parser_rule
    # def parse_lambda_prototype(self) -> LambdaPrototypeAst:
    #     c1 = self._pos
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
    #     c1 = self._pos
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
    #     c1 = self._pos
    #     p1 = self.parse_convention().parse_once()
    #     p2 = self.parse_expression().parse_once()
    #     return LambdaCaptureItemNormalAst(c1, p1, p2)
    #
    # @parser_rule
    # def parse_lambda_capture_item_named(self) -> LambdaCaptureItemNamedAst:
    #     c1 = self._pos
    #     p1 = self.parse_identifier().parse_once()
    #     p2 = self.parse_token(SppTokenType.TkAssign).parse_once()
    #     p3 = self.parse_convention().parse_once()
    #     p4 = self.parse_expression().parse_once()
    #     return LambdaCaptureItemNamedAst(c1, p1, p2, p3, p4)

    # ===== TYPES =====

    def parse_binary_type_expression_precedence_level_n_rhs(self, op, rhs) -> Tuple[Asts.TokenAst, Asts.TypeSingleAst]:
        p1 = self.parse_once(op)
        p2 = self.parse_once(rhs)
        return p1, p2

    def parse_binary_type_expression_precedence_level_n(self, lhs, op, rhs) -> Asts.TypeSingleAst:
        c1 = self._pos
        p1 = self.parse_once(lhs)
        p2 = self.parse_optional(lambda: self.parse_binary_type_expression_precedence_level_n_rhs(op, rhs))
        return Asts.TypeBinaryExpressionAst(c1, p1, p2[0], p2[1]).convert() if p2 else p1

    def parse_type(self) -> Asts.TypeAst:
        p1 = self.parse_alternate(
            self.parse_type_parenthesized,
            self.parse_type_array,
            self.parse_type_tuple,
            self.parse_type_binary_expression_precedence_level_1)
        return p1

    def parse_type_simple(self) -> Asts.TypeSingleAst:
        c1 = self._pos
        p1 = self.parse_zero_or_more(self.parse_type_unary_op_namespace, self.parse_nothing)
        p2 = self.parse_once(self.parse_type_single)
        return reduce(lambda acc, x: Asts.TypeUnaryExpressionAst(c1, x, acc), p1.reverse().list(), p2)

    def parse_type_binary_expression_precedence_level_1(self) -> Asts.TypeAst:
        return self.parse_binary_type_expression_precedence_level_n(
            self.parse_type_binary_expression_precedence_level_2,
            self.parse_type_binary_op_precedence_level_1,
            self.parse_type_binary_expression_precedence_level_1)

    def parse_type_binary_expression_precedence_level_2(self) -> Asts.TypeAst:
        return self.parse_binary_type_expression_precedence_level_n(
            self.parse_type_unary_expression,
            self.parse_type_binary_op_precedence_level_2,
            self.parse_type_binary_expression_precedence_level_2)

    def parse_type_binary_op_precedence_level_1(self) -> Asts.TokenAst:
        p1 = self.parse_once(self.parse_keyword_and)
        return p1

    def parse_type_binary_op_precedence_level_2(self) -> Asts.TokenAst:
        p1 = self.parse_once(self.parse_keyword_or)
        return p1

    def parse_type_unary_expression(self) -> Asts.TypeAst:
        c1 = self._pos
        p1 = self.parse_zero_or_more(self.parse_type_unary_op, self.parse_nothing)
        p2 = self.parse_once(self.parse_type_postfix_expression)
        return reduce(lambda acc, x: Asts.TypeUnaryExpressionAst(c1, x, acc), p1.reverse().list(), p2)

    def parse_type_postfix_expression(self) -> Asts.TypeAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_type_single)
        p2 = self.parse_zero_or_more(self.parse_type_postfix_op, self.parse_nothing)
        return reduce(lambda acc, x: Asts.TypePostfixExpressionAst(c1, acc, x), p2.list(), p1)

    def parse_type_parenthesized(self) -> Asts.TypeSingleAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_token_left_parenthesis)
        p2 = self.parse_once(self.parse_type)
        p3 = self.parse_once(self.parse_token_right_parenthesis)
        return Asts.TypeParenthesizedAst(c1, p1, p2, p3).convert()

    def parse_type_tuple(self) -> Asts.TypeSingleAst:
        p1 = self.parse_alternate(
            self.parse_type_tuple_1_items,
            self.parse_type_tuple_n_items)
        return p1

    def parse_type_array(self) -> Asts.TypeSingleAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_token_left_square_bracket)
        p2 = self.parse_once(self.parse_type)
        p3 = self.parse_once(self.parse_token_comma)
        p4 = self.parse_once(self.parse_lexeme_dec_integer)
        p5 = self.parse_once(self.parse_token_right_square_bracket)
        return Asts.TypeArrayAst(c1, p1, p2, p3, p4, p5).convert()

    def parse_type_single(self) -> Asts.TypeSingleAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_generic_identifier)
        return Asts.TypeSingleAst(c1, p1)

    def parse_type_unary_op(self) -> Asts.TypeUnaryOperatorAst:
        p1 = self.parse_once(self.parse_type_unary_op_namespace)
        return p1

    def parse_type_unary_op_namespace(self) -> Asts.TypeUnaryOperatorNamespaceAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_identifier)
        p2 = self.parse_once(self.parse_token_double_colon)
        return Asts.TypeUnaryOperatorNamespaceAst(c1, p1, p2)

    def parse_type_postfix_op(self) -> Asts.TypePostfixOperatorAst:
        p1 = self.parse_alternate(
            self.parse_type_postfix_op_nested_type,
            self.parse_type_postfix_op_indexed_type,
            self.parse_type_postfix_op_optional_type)
        return p1

    def parse_type_postfix_op_nested_type(self) -> Asts.TypePostfixOperatorNestedTypeAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_token_double_colon)
        p2 = self.parse_once(self.parse_type_simple)
        return Asts.TypePostfixOperatorNestedTypeAst(c1, p1, p2)

    def parse_type_postfix_op_indexed_type(self) -> Asts.TypePostfixOperatorIndexedTypeAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_token_double_colon)
        p2 = self.parse_once(self.parse_lexeme_dec_integer)
        return Asts.TypePostfixOperatorIndexedTypeAst(c1, p1, p2)

    def parse_type_postfix_op_optional_type(self) -> Asts.TypePostfixOperatorOptionalTypeAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_token_question_mark)
        return Asts.TypePostfixOperatorOptionalTypeAst(c1, p1)

    def parse_type_tuple_1_items(self) -> Asts.TypeSingleAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_token_left_parenthesis)
        p2 = self.parse_once(self.parse_type)
        p3 = self.parse_once(self.parse_token_comma)
        p4 = self.parse_once(self.parse_token_right_parenthesis)
        return Asts.TypeTupleAst(c1, p1, Seq([p2]), p4).convert()

    def parse_type_tuple_n_items(self) -> Asts.TypeSingleAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_token_left_parenthesis)
        p2 = self.parse_one_or_more(self.parse_type, self.parse_token_comma)
        p3 = self.parse_once(self.parse_token_right_parenthesis)
        return Asts.TypeTupleAst(c1, p1, p2, p3).convert()

    # ===== IDENTIFIERS =====

    def parse_identifier(self) -> Asts.IdentifierAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_lexeme_identifier)
        return Asts.IdentifierAst(c1, p1.token_data)

    def parse_upper_identifier(self) -> Asts.IdentifierAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_lexeme_upper_identifier)
        return Asts.IdentifierAst(c1, p1.token_data)

    def parse_generic_identifier(self) -> Asts.GenericIdentifierAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_upper_identifier)
        p2 = self.parse_optional(self.parse_generic_arguments) or Asts.GenericArgumentGroupAst(pos=c1)
        return Asts.GenericIdentifierAst(c1, p1.value, p2)

    # ===== LITERALS =====

    def parse_literal(self) -> Asts.LiteralAst:
        p1 = self.parse_alternate(
            self.parse_literal_float,
            self.parse_literal_integer,
            self.parse_literal_string,
            lambda: self.parse_literal_tuple(self.parse_expression),
            lambda: self.parse_literal_array(self.parse_expression),
            self.parse_literal_boolean)
        return p1

    def parse_literal_float(self) -> Asts.FloatLiteralAst:
        p1 = self.parse_once(self.parse_literal_float_b10)
        return p1

    def parse_literal_integer(self) -> Asts.IntegerLiteralAst:
        p1 = self.parse_alternate(
            self.parse_literal_integer_b10,
            self.parse_literal_integer_b02,
            self.parse_literal_integer_b16)
        return p1

    def parse_literal_string(self) -> Asts.StringLiteralAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_lexeme_double_quote_string)
        return Asts.StringLiteralAst(c1, p1)

    def parse_literal_tuple(self, item=None) -> Asts.TupleLiteralAst:
        p1 = self.parse_alternate(
            self.parse_literal_tuple_0_items,
            lambda : self.parse_literal_tuple_1_items(item or self.parse_expression),
            lambda : self.parse_literal_tuple_n_items(item or self.parse_expression))
        return p1

    def parse_literal_array(self, item) -> Asts.ArrayLiteralAst:
        p1 = self.parse_alternate(
            self.parse_literal_array_0_items,
            lambda : self.parse_literal_array_n_items(item))
        return p1

    def parse_literal_boolean(self) -> Asts.BooleanLiteralAst:
        c1 = self._pos
        p1 = self.parse_alternate(
            self.parse_keyword_true,
            self.parse_keyword_false)
        return Asts.BooleanLiteralAst(c1, p1)

    # ===== NUMBERS =====

    def parse_literal_float_b10(self) -> Asts.FloatLiteralAst:
        c1 = self._pos
        p1 = self.parse_optional(self.parse_numeric_prefix_op)
        p2 = self.parse_once(self.parse_lexeme_dec_integer)
        p3 = self.parse_once(self.parse_token_dot)
        p4 = self.parse_once(self.parse_lexeme_dec_integer)
        p5 = self.parse_optional(self.parse_float_postfix_type)
        return Asts.FloatLiteralAst(c1, p1, p2, p3, p4, p5)

    def parse_literal_integer_b10(self) -> Asts.IntegerLiteralAst:
        c1 = self._pos
        p1 = self.parse_optional(self.parse_numeric_prefix_op)
        p2 = self.parse_once(self.parse_lexeme_dec_integer)
        p3 = self.parse_optional(self.parse_integer_postfix_type)
        return Asts.IntegerLiteralAst(c1, p1, p2, p3)

    def parse_literal_integer_b02(self) -> Asts.IntegerLiteralAst:
        c1 = self._pos
        p1 = self.parse_optional(self.parse_numeric_prefix_op)
        p2 = self.parse_once(self.parse_lexeme_bin_integer)
        p3 = self.parse_optional(self.parse_integer_postfix_type)
        return Asts.IntegerLiteralAst(c1, p1, p2, p3)

    def parse_literal_integer_b16(self) -> Asts.IntegerLiteralAst:
        c1 = self._pos
        p1 = self.parse_optional(self.parse_numeric_prefix_op)
        p2 = self.parse_once(self.parse_lexeme_hex_integer)
        p3 = self.parse_optional(self.parse_integer_postfix_type)
        return Asts.IntegerLiteralAst(c1, p1, p2, p3)

    def parse_numeric_prefix_op(self) -> Asts.TokenAst:
        p1 = self.parse_alternate(
            self.parse_token_minus,
            self.parse_token_plus)
        return p1

    def parse_integer_postfix_type(self) -> Asts.TypeAst:
        p1 = self.parse_once(self.parse_token_underscore)
        p2 = self.parse_alternate(
            lambda: self.parse_characters("i8"),
            lambda: self.parse_characters("i16"),
            lambda: self.parse_characters("i32"),
            lambda: self.parse_characters("i64"),
            lambda: self.parse_characters("i128"),
            lambda: self.parse_characters("i256"),
            lambda: self.parse_characters("u8"),
            lambda: self.parse_characters("u16"),
            lambda: self.parse_characters("u32"),
            lambda: self.parse_characters("u64"),
            lambda: self.parse_characters("u128"),
            lambda: self.parse_characters("u256"))
        return Asts.TypeSingleAst.from_token(p2)

    def parse_float_postfix_type(self) -> Asts.TypeAst:
        p1 = self.parse_once(self.parse_token_underscore)
        p2 = self.parse_alternate(
            lambda: self.parse_characters("f8"),
            lambda: self.parse_characters("f16"),
            lambda: self.parse_characters("f32"),
            lambda: self.parse_characters("f64"),
            lambda: self.parse_characters("f128"),
            lambda: self.parse_characters("f256"))
        return Asts.TypeSingleAst.from_token(p2)

    # ===== TUPLES =====

    def parse_literal_tuple_0_items(self) -> Asts.TupleLiteralAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_token_left_parenthesis)
        p2 = self.parse_once(self.parse_token_right_parenthesis)
        return Asts.TupleLiteralAst(c1, p1, Seq(), p2)

    def parse_literal_tuple_1_items(self, item) -> Asts.TupleLiteralAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_token_left_parenthesis)
        p2 = self.parse_once(item)
        p3 = self.parse_once(self.parse_token_comma)
        p4 = self.parse_once(self.parse_token_right_parenthesis)
        return Asts.TupleLiteralAst(c1, p1, Seq([p2]), p4)

    def parse_literal_tuple_n_items(self, item) -> Asts.TupleLiteralAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_token_left_parenthesis)
        p2 = self.parse_two_or_more(item, self.parse_token_comma)
        p3 = self.parse_once(self.parse_token_right_parenthesis)
        return Asts.TupleLiteralAst(c1, p1, Seq(p2), p3)

    # ===== ARRAYS =====

    def parse_literal_array_0_items(self) -> Asts.ArrayLiteral0ElementAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_token_left_square_bracket)
        p2 = self.parse_once(self.parse_type)
        p3 = self.parse_once(self.parse_token_comma)
        p4 = self.parse_once(self.parse_lexeme_dec_integer)
        p5 = self.parse_once(self.parse_token_right_square_bracket)
        return Asts.ArrayLiteral0ElementAst(c1, p1, p2, p3, p4, p5)

    def parse_literal_array_n_items(self, item) -> Asts.ArrayLiteralNElementAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_token_left_square_bracket)
        p2 = self.parse_one_or_more(item, self.parse_token_comma)
        p3 = self.parse_once(self.parse_token_right_square_bracket)
        return Asts.ArrayLiteralNElementAst(c1, p1, Seq(p2), p3)

    # ===== GLOBAL CONSTANTS =====

    def parse_global_constant_value(self) -> Asts.ExpressionAst:
        p1 = self.parse_alternate(
            self.parse_literal_float,
            self.parse_literal_integer,
            self.parse_literal_string,
            lambda: self.parse_literal_tuple(self.parse_global_constant_value),
            lambda: self.parse_literal_array(self.parse_global_constant_value),
            self.parse_literal_boolean,
            self.parse_global_object_initializer,
            self.parse_identifier)
        return p1

    def parse_global_object_initializer(self) -> Asts.ObjectInitializerAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_type_simple)
        p2 = self.parse_once(self.parse_global_object_initializer_arguments)
        return Asts.ObjectInitializerAst(c1, p1, p2)

    def parse_global_object_initializer_arguments(self) -> Asts.ObjectInitializerArgumentGroupAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_token_left_parenthesis)
        p2 = self.parse_zero_or_more(self.parse_global_object_initializer_argument_named, self.parse_token_comma)
        p3 = self.parse_once(self.parse_token_right_parenthesis)
        return Asts.ObjectInitializerArgumentGroupAst(c1, p1, Seq(p2), p3)

    def parse_global_object_initializer_argument_named(self) -> Asts.ObjectInitializerArgumentNamedAst:
        c1 = self._pos
        p1 = self.parse_once(self.parse_identifier)
        p2 = self.parse_once(self.parse_token_assign)
        p3 = self.parse_once(self.parse_global_constant_value)
        return Asts.ObjectInitializerArgumentNamedAst(c1, p1, p2, p3)

    # ===== TOKENS =====

    def parse_nothing(self) -> Asts.TokenAst:
        return self.parse_token_raw(RawTokenType.NoToken, SppTokenType.NoToken)

    def parse_newline(self) -> Asts.TokenAst:
        return self.parse_token_raw(RawTokenType.TkNewLine, SppTokenType.TkNewLine)

    def parse_token_left_curly_brace(self) -> Asts.TokenAst:
        return self.parse_token_raw(RawTokenType.TkLeftCurlyBrace, SppTokenType.TkLeftCurlyBrace)

    def parse_token_right_curly_brace(self) -> Asts.TokenAst:
        return self.parse_token_raw(RawTokenType.TkRightCurlyBrace, SppTokenType.TkRightCurlyBrace)

    def parse_token_colon(self) -> Asts.TokenAst:
        return self.parse_token_raw(RawTokenType.TkColon, SppTokenType.TkColon)

    def parse_token_left_parenthesis(self) -> Asts.TokenAst:
        return self.parse_token_raw(RawTokenType.TkLeftParenthesis, SppTokenType.TkLeftParenthesis)

    def parse_token_right_parenthesis(self) -> Asts.TokenAst:
        return self.parse_token_raw(RawTokenType.TkRightParenthesis, SppTokenType.TkRightParenthesis)

    def parse_token_comma(self) -> Asts.TokenAst:
        return self.parse_token_raw(RawTokenType.TkComma, SppTokenType.TkComma)

    def parse_token_assign(self) -> Asts.TokenAst:
        return self.parse_token_raw(RawTokenType.TkEqualsSign, SppTokenType.TkAssign)

    def parse_token_left_square_bracket(self) -> Asts.TokenAst:
        return self.parse_token_raw(RawTokenType.TkLeftSquareBracket, SppTokenType.TkLeftSquareBracket)

    def parse_token_right_square_bracket(self) -> Asts.TokenAst:
        return self.parse_token_raw(RawTokenType.TkRightSquareBracket, SppTokenType.TkRightSquareBracket)

    def parse_token_at(self) -> Asts.TokenAst:
        return self.parse_token_raw(RawTokenType.TkAt, SppTokenType.TkAt)

    def parse_token_underscore(self) -> Asts.TokenAst:
        return self.parse_token_raw(RawTokenType.TkUnderscore, SppTokenType.TkUnderscore)

    def parse_token_less_than(self) -> Asts.TokenAst:
        return self.parse_token_raw(RawTokenType.TkLessThanSign, SppTokenType.TkLt)

    def parse_token_greater_than(self) -> Asts.TokenAst:
        return self.parse_token_raw(RawTokenType.TkGreaterThanSign, SppTokenType.TkGt)

    def parse_token_plus(self) -> Asts.TokenAst:
        return self.parse_token_raw(RawTokenType.TkPlusSign, SppTokenType.TkPlus)

    def parse_token_minus(self) -> Asts.TokenAst:
        return self.parse_token_raw(RawTokenType.TkMinusSign, SppTokenType.TkMinus)

    def parse_token_multiply(self) -> Asts.TokenAst:
        return self.parse_token_raw(RawTokenType.TkAsterisk, SppTokenType.TkMultiply)

    def parse_token_divide(self) -> Asts.TokenAst:
        return self.parse_token_raw(RawTokenType.TkForwardSlash, SppTokenType.TkDivide)

    def parse_token_modulo(self) -> Asts.TokenAst:
        return self.parse_token_raw(RawTokenType.TkPercentSign, SppTokenType.TkModulo)

    def parse_token_dot(self) -> Asts.TokenAst:
        return self.parse_token_raw(RawTokenType.TkDot, SppTokenType.TkDot)

    def parse_token_question_mark(self) -> Asts.TokenAst:
        return self.parse_token_raw(RawTokenType.TkQuestionMark, SppTokenType.TkQuestionMark)

    def parse_token_ampersand(self) -> Asts.TokenAst:
        return self.parse_token_raw(RawTokenType.TkAmpersand, SppTokenType.TkAmpersand)

    def parse_token_quote(self) -> Asts.TokenAst:
        return self.parse_token_raw(RawTokenType.TkSpeechMark, SppTokenType.TkSpeechMark)

    def parse_token_dollar(self) -> Asts.TokenAst:
        return self.parse_token_raw(RawTokenType.TkDollar, SppTokenType.TkDollar)

    def parse_token_arrow_right(self) -> Asts.TokenAst:
        p1 = self.parse_token_raw(RawTokenType.TkMinusSign, SppTokenType.TkArrowR)
        p2 = self.parse_token_raw(RawTokenType.TkGreaterThanSign, SppTokenType.TkArrowR)
        return p1

    def parse_token_double_dot(self) -> Asts.TokenAst:
        p1 = self.parse_token_raw(RawTokenType.TkDot, SppTokenType.TkDoubleDot)
        p2 = self.parse_token_raw(RawTokenType.TkDot, SppTokenType.TkDoubleDot)
        return p1

    def parse_token_equals(self) -> Asts.TokenAst:
        p1 = self.parse_token_raw(RawTokenType.TkEqualsSign, SppTokenType.TkEq)
        p2 = self.parse_token_raw(RawTokenType.TkEqualsSign, SppTokenType.TkEq)
        return p1

    def parse_token_not_equals(self) -> Asts.TokenAst:
        p1 = self.parse_token_raw(RawTokenType.TkExclamationMark, SppTokenType.TkNe)
        p2 = self.parse_token_raw(RawTokenType.TkEqualsSign, SppTokenType.TkNe)
        return p1

    def parse_token_less_than_or_equals(self) -> Asts.TokenAst:
        p1 = self.parse_token_raw(RawTokenType.TkLessThanSign, SppTokenType.TkLe)
        p2 = self.parse_token_raw(RawTokenType.TkEqualsSign, SppTokenType.TkLe)
        return p1

    def parse_token_plus_assign(self) -> Asts.TokenAst:
        p1 = self.parse_token_raw(RawTokenType.TkPlusSign, SppTokenType.TkPlusAssign)
        p2 = self.parse_token_raw(RawTokenType.TkEqualsSign, SppTokenType.TkPlusAssign)
        return p1

    def parse_token_minus_assign(self) -> Asts.TokenAst:
        p1 = self.parse_token_raw(RawTokenType.TkMinusSign, SppTokenType.TkMinusAssign)
        p2 = self.parse_token_raw(RawTokenType.TkEqualsSign, SppTokenType.TkMinusAssign)
        return p1

    def parse_token_multiply_assign(self) -> Asts.TokenAst:
        p1 = self.parse_token_raw(RawTokenType.TkAsterisk, SppTokenType.TkMultiplyAssign)
        p2 = self.parse_token_raw(RawTokenType.TkEqualsSign, SppTokenType.TkMultiplyAssign)
        return p1

    def parse_token_divide_assign(self) -> Asts.TokenAst:
        p1 = self.parse_token_raw(RawTokenType.TkForwardSlash, SppTokenType.TkDivideAssign)
        p2 = self.parse_token_raw(RawTokenType.TkEqualsSign, SppTokenType.TkDivideAssign)
        return p1

    def parse_token_modulo_assign(self) -> Asts.TokenAst:
        p1 = self.parse_token_raw(RawTokenType.TkPercentSign, SppTokenType.TkModuloAssign)
        p2 = self.parse_token_raw(RawTokenType.TkEqualsSign, SppTokenType.TkModuloAssign)
        return p1

    def parse_token_greater_than_or_equals(self) -> Asts.TokenAst:
        p1 = self.parse_token_raw(RawTokenType.TkGreaterThanSign, SppTokenType.TkGe)
        p2 = self.parse_token_raw(RawTokenType.TkEqualsSign, SppTokenType.TkGe)
        return p1

    def parse_token_remainder(self) -> Asts.TokenAst:
        p1 = self.parse_token_raw(RawTokenType.TkPercentSign, SppTokenType.TkRemainder)
        p2 = self.parse_token_raw(RawTokenType.TkPercentSign, SppTokenType.TkRemainder)
        return p1

    def parse_token_exponent(self) -> Asts.TokenAst:
        p1 = self.parse_token_raw(RawTokenType.TkAsterisk, SppTokenType.TkExponent)
        p2 = self.parse_token_raw(RawTokenType.TkAsterisk, SppTokenType.TkExponent)
        return p1

    def parse_token_double_colon(self) -> Asts.TokenAst:
        p1 = self.parse_token_raw(RawTokenType.TkColon, SppTokenType.TkDoubleColon)
        p2 = self.parse_token_raw(RawTokenType.TkColon, SppTokenType.TkDoubleColon)
        return p1

    def parse_token_spaceship(self) -> Asts.TokenAst:
        p1 = self.parse_token_raw(RawTokenType.TkLessThanSign, SppTokenType.TkSs)
        p2 = self.parse_token_raw(RawTokenType.TkEqualsSign, SppTokenType.TkSs)
        p3 = self.parse_token_raw(RawTokenType.TkGreaterThanSign, SppTokenType.TkSs)
        return p1

    def parse_token_remainder_assign(self) -> Asts.TokenAst:
        p1 = self.parse_token_raw(RawTokenType.TkPercentSign, SppTokenType.TkRemainderAssign)
        p2 = self.parse_token_raw(RawTokenType.TkPercentSign, SppTokenType.TkRemainderAssign)
        p3 = self.parse_token_raw(RawTokenType.TkEqualsSign, SppTokenType.TkRemainderAssign)
        return p1

    def parse_token_exponent_assign(self) -> Asts.TokenAst:
        p1 = self.parse_token_raw(RawTokenType.TkAsterisk, SppTokenType.TkExponentAssign)
        p2 = self.parse_token_raw(RawTokenType.TkAsterisk, SppTokenType.TkExponentAssign)
        p3 = self.parse_token_raw(RawTokenType.TkEqualsSign, SppTokenType.TkExponentAssign)
        return p1

    # ===== KEYWORDS =====

    def parse_keyword_cls(self) -> Asts.TokenAst:
        return self.parse_keyword_raw(RawKeywordType.Cls, SppTokenType.KwCls, requires_following_space=True)

    def parse_keyword_sup(self) -> Asts.TokenAst:
        return self.parse_keyword_raw(RawKeywordType.Sup, SppTokenType.KwSup, requires_following_space=True)

    def parse_keyword_ext(self) -> Asts.TokenAst:
        return self.parse_keyword_raw(RawKeywordType.Ext, SppTokenType.KwExt, requires_following_space=True)

    def parse_keyword_fun(self) -> Asts.TokenAst:
        return self.parse_keyword_raw(RawKeywordType.Fun, SppTokenType.KwFun, requires_following_space=True)

    def parse_keyword_cor(self) -> Asts.TokenAst:
        return self.parse_keyword_raw(RawKeywordType.Cor, SppTokenType.KwCor, requires_following_space=True)

    def parse_keyword_mut(self) -> Asts.TokenAst:
        return self.parse_keyword_raw(RawKeywordType.Mut, SppTokenType.KwMut, requires_following_space=True)

    def parse_keyword_cmp(self) -> Asts.TokenAst:
        return self.parse_keyword_raw(RawKeywordType.Cmp, SppTokenType.KwCmp, requires_following_space=True)

    def parse_keyword_where(self) -> Asts.TokenAst:
        return self.parse_keyword_raw(RawKeywordType.Where, SppTokenType.KwWhere, requires_following_space=True)

    def parse_keyword_self_value(self) -> Asts.TokenAst:
        return self.parse_keyword_raw(RawKeywordType.SelfVal, SppTokenType.KwSelfVal, requires_following_space=False)

    def parse_keyword_case(self) -> Asts.TokenAst:
        return self.parse_keyword_raw(RawKeywordType.Case, SppTokenType.KwCase, requires_following_space=True)

    def parse_keyword_of(self) -> Asts.TokenAst:
        return self.parse_keyword_raw(RawKeywordType.Of, SppTokenType.KwOf, requires_following_space=False)  # space ? (\n)

    def parse_keyword_loop(self) -> Asts.TokenAst:
        return self.parse_keyword_raw(RawKeywordType.Loop, SppTokenType.KwLoop, requires_following_space=True)

    def parse_keyword_in(self) -> Asts.TokenAst:
        return self.parse_keyword_raw(RawKeywordType.In, SppTokenType.KwIn, requires_following_space=True)

    def parse_keyword_else(self) -> Asts.TokenAst:
        return self.parse_keyword_raw(RawKeywordType.Else, SppTokenType.KwElse, requires_following_space=True)

    def parse_keyword_gen(self) -> Asts.TokenAst:
        return self.parse_keyword_raw(RawKeywordType.Gen, SppTokenType.KwGen, requires_following_space=True)

    def parse_keyword_with(self) -> Asts.TokenAst:
        return self.parse_keyword_raw(RawKeywordType.With, SppTokenType.KwWith, requires_following_space=True)

    def parse_keyword_ret(self) -> Asts.TokenAst:
        return self.parse_keyword_raw(RawKeywordType.Ret, SppTokenType.KwRet, requires_following_space=False)  # =True, unless newline?

    def parse_keyword_exit(self) -> Asts.TokenAst:
        return self.parse_keyword_raw(RawKeywordType.Exit, SppTokenType.KwExit, requires_following_space=False)

    def parse_keyword_skip(self) -> Asts.TokenAst:
        return self.parse_keyword_raw(RawKeywordType.Skip, SppTokenType.KwSkip, requires_following_space=False)

    def parse_keyword_pin(self) -> Asts.TokenAst:
        return self.parse_keyword_raw(RawKeywordType.Pin, SppTokenType.KwPin, requires_following_space=True)

    def parse_keyword_rel(self) -> Asts.TokenAst:
        return self.parse_keyword_raw(RawKeywordType.Rel, SppTokenType.KwRel, requires_following_space=True)

    def parse_keyword_use(self) -> Asts.TokenAst:
        return self.parse_keyword_raw(RawKeywordType.Use, SppTokenType.KwUse, requires_following_space=True)

    def parse_keyword_let(self) -> Asts.TokenAst:
        return self.parse_keyword_raw(RawKeywordType.Let, SppTokenType.KwLet, requires_following_space=True)

    def parse_keyword_as(self) -> Asts.TokenAst:
        return self.parse_keyword_raw(RawKeywordType.As, SppTokenType.KwAs, requires_following_space=True)

    def parse_keyword_is(self) -> Asts.TokenAst:
        return self.parse_keyword_raw(RawKeywordType.Is, SppTokenType.KwIs, requires_following_space=True)

    def parse_keyword_and(self) -> Asts.TokenAst:
        return self.parse_keyword_raw(RawKeywordType.And, SppTokenType.KwAnd, requires_following_space=True)

    def parse_keyword_or(self) -> Asts.TokenAst:
        return self.parse_keyword_raw(RawKeywordType.Or, SppTokenType.KwOr, requires_following_space=True)

    def parse_keyword_async(self) -> Asts.TokenAst:
        return self.parse_keyword_raw(RawKeywordType.Async, SppTokenType.KwAsync, requires_following_space=True)

    def parse_keyword_not(self) -> Asts.TokenAst:
        return self.parse_keyword_raw(RawKeywordType.Not, SppTokenType.KwNot, requires_following_space=False)

    def parse_keyword_step(self) -> Asts.TokenAst:
        return self.parse_keyword_raw(RawKeywordType.Step, SppTokenType.KwStep, requires_following_space=False)

    def parse_keyword_true(self) -> Asts.TokenAst:
        return self.parse_keyword_raw(RawKeywordType.True_, SppTokenType.KwTrue, requires_following_space=False)

    def parse_keyword_false(self) -> Asts.TokenAst:
        return self.parse_keyword_raw(RawKeywordType.False_, SppTokenType.KwFalse, requires_following_space=False)

    # ===== LEXEMES =====

    def parse_lexeme_character(self) -> Asts.TokenAst:
        return self.parse_token_raw(RawTokenType.TkCharacter, SppTokenType.LxNumber)

    def parse_lexeme_digit(self) -> Asts.TokenAst:
        return self.parse_token_raw(RawTokenType.TkDigit, SppTokenType.LxNumber)

    def parse_lexeme_character_or_digit(self) -> Asts.TokenAst:
        return self.parse_alternate(self.parse_lexeme_character, self.parse_lexeme_digit)

    def parse_lexeme_character_or_digit_or_underscore(self) -> Asts.TokenAst:
        return self.parse_alternate(self.parse_lexeme_character, self.parse_lexeme_digit, self.parse_token_underscore)

    def parse_lexeme_dec_integer(self) -> Asts.TokenAst:
        self.parse_nothing()
        out = Asts.TokenAst(self._pos, SppTokenType.LxNumber, "")

        match self.current_tok().token_type:
            case RawTokenType.TkDigit:
                out.token_data += self.parse_once(self.parse_lexeme_digit).token_data
            case _:
                self.store_error(self._pos, "Invalid decimal integer literal")
                raise self._error

        while self.current_tok().token_type == RawTokenType.TkDigit:
            out.token_data += self.parse_once(self.parse_lexeme_digit).token_data

        return out

    def parse_lexeme_bin_integer(self) -> Asts.TokenAst:
        self.parse_nothing()
        out = Asts.TokenAst(self._pos, SppTokenType.LxNumber, "")

        p1 = self.parse_once(self.parse_lexeme_digit)
        if p1.token_data != "0":
            self.store_error(p1.pos, "Invalid binary integer literal")
            raise self._error

        p2 = self.parse_once(self.parse_lexeme_character)
        if p2.token_data != "b":
            self.store_error(p2.pos, "Invalid binary integer literal")
            raise self._error

        while self.current_tok().token_type == RawTokenType.TkDigit:
            p3 = self.parse_once(self.parse_lexeme_digit)
            if p3.token_data not in "01":
                self.store_error(p3.pos, "Invalid binary integer literal")
                raise self._error
            out.token_data += p3.token_data

        return out

    def parse_lexeme_hex_integer(self) -> Asts.TokenAst:
        self.parse_nothing()
        out = Asts.TokenAst(self._pos, SppTokenType.LxNumber, "")

        p1 = self.parse_once(self.parse_lexeme_digit)
        if p1.token_data != "0":
            self.store_error(p1.pos, "Invalid hexadecimal integer literal")
            raise self._error

        p2 = self.parse_once(self.parse_lexeme_character)
        if p2.token_data not in "x":
            self.store_error(p2.pos, "Invalid hexadecimal integer literal")
            raise self._error

        while self.current_tok().token_type in [RawTokenType.TkCharacter, RawTokenType.TkDigit]:
            p3 = self.parse_once(self.parse_lexeme_character_or_digit)
            if p3.token_data not in "0123456789abcdefABCDEF":
                self.store_error(p3.pos, "Invalid hexadecimal integer literal")
                raise self._error
            out.token_data += p3.token_data

        return out

    def parse_lexeme_double_quote_string(self) -> Asts.TokenAst:
        out = Asts.TokenAst(self._pos, SppTokenType.LxString, "")
        out.token_data += self.parse_once(self.parse_token_quote).token_data

        while self.current_tok().token_type == RawTokenType.TkCharacter:
            out.token_data += self.parse_once(self.parse_lexeme_character).token_data

        out.token_data += self.parse_once(self.parse_token_quote).token_data
        return out

    def parse_lexeme_identifier(self) -> Asts.TokenAst:
        self.parse_nothing()
        out = Asts.TokenAst(self._pos, SppTokenType.LxString, "")

        p0 = self.parse_optional(self.parse_token_dollar)
        if p0:
            out.token_data += p0.token_data

        p1 = self.parse_once(self.parse_lexeme_character)
        if not p1.token_data.islower():
            self.store_error(p1.pos, "Invalid identifier")
            raise self._error
        out.token_data += p1.token_data

        while self.current_tok().token_type in self._identifier_characters:
            p2 = self.parse_once(self.parse_lexeme_character_or_digit_or_underscore)
            out.token_data += p2.token_data

        return out

    def parse_lexeme_upper_identifier(self) -> Asts.TokenAst:
        self.parse_nothing()
        out = Asts.TokenAst(self._pos, SppTokenType.LxString, "")

        p0 = self.parse_optional(self.parse_token_dollar)
        if p0:
            out.token_data += p0.token_data

        p1 = self.parse_once(self.parse_lexeme_character)
        if not p1.token_data.isupper():
            self.store_error(p1.pos, "Invalid upper identifier")
            raise self._error
        out.token_data += p1.token_data

        while self.current_tok().token_type in self._upper_identifier_characters:
            p2 = self.parse_once(self.parse_lexeme_character_or_digit)
            out.token_data += p2.token_data

        return out

    # ===== TOKENS, KEYWORDS, & LEXEMES =====

    def store_error(self, pos: int, error: str) -> bool:
        if pos > self._error.pos:
            self._error.expected_tokens.clear()
            self._error.pos = pos
            self._error.args = (error,)
            return True
        return False

    def parse_characters(self, value: str) -> Asts.TokenAst:
        self.parse_nothing()
        p1 = Asts.TokenAst(self._pos, SppTokenType.LxString, value)

        for c in value:
            p2 = self.parse_once(lambda: self.parse_character(c))
        return p1

    def parse_character(self, value: str) -> Asts.TokenAst:
        p1 = self.parse_once(self.parse_lexeme_character_or_digit)
        if p1.token_data != value:
            self.store_error(p1.pos, f"Expected '{value}'")
            raise self._error
        return p1

    def parse_keyword_raw(self, keyword: RawKeywordType, mapped_keyword: SppTokenType, *, requires_following_space: bool) -> Asts.TokenAst:
        p1 = Asts.TokenAst(self._pos, mapped_keyword, keyword.value)
        self.parse_characters(keyword.value)
        if requires_following_space:
            self.parse_token_raw(RawTokenType.TkWhitespace, SppTokenType.NoToken)
        return p1

    def parse_token_raw(self, token: RawTokenType, mapped_token: SppTokenType) -> Asts.TokenAst:
        if self._pos > self._tokens_len:
            self.store_error(self._pos, "Unexpected end of input")
            raise self._error

        if token != RawTokenType.TkNewLine and token != RawTokenType.TkWhitespace:
            while self.current_tok().token_type in self._skip_all_characters:
                self._pos += 1

        elif token == RawTokenType.TkNewLine:
            while self.current_tok().token_type == self._skip_whitespace_character:
                self._pos += 1

        elif token == RawTokenType.TkWhitespace:
            while self.current_tok().token_type == self._skip_newline_character:
                self._pos += 1

        if token == RawTokenType.NoToken:
            return Asts.TokenAst(self._pos, SppTokenType.NoToken, "")

        if self.current_tok().token_type != token:
            if self._error.pos == self._pos:
                self._error.expected_tokens.append(mapped_token.value)
                raise self._error

            if self.store_error(self._pos, f"Expected £, got '{self.current_tok().token_data}'"):
                self._error.expected_tokens.append(mapped_token.value)
            raise self._error

        token_ast = Asts.TokenAst(self._pos, mapped_token, self.current_tok().token_data if mapped_token in [SppTokenType.LxNumber, SppTokenType.LxString] else mapped_token.value)
        self._pos += 1
        return token_ast


__all__ = ["SppParser"]
