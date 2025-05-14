from __future__ import annotations

from typing import Callable, List, Optional, Tuple, Union

from inline.inline_runtime import inline, inline_cls

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType, RawToken, RawTokenType, RawKeywordType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SyntacticAnalysis.ParserErrors import ParserErrors
from SPPCompiler.Utils.ErrorFormatter import ErrorFormatter
from SPPCompiler.Utils.Functools import reduce
from SPPCompiler.Utils.Sequence import Seq


@inline_cls
class SppParser:
    _pos: int
    _tokens: List[RawToken]
    _token_types: List[RawTokenType]
    _tokens_len: int
    _error: ParserErrors.SyntaxError
    _error_formatter: ErrorFormatter
    _injection_adjust_pos: int

    _identifier_characters: List[RawTokenType]
    _upper_identifier_characters: List[RawTokenType]
    _nl_ws_characters: List[RawTokenType]
    _nl_characters: RawTokenType
    _ws_characters: RawTokenType
    _stringable_characters: List[SppTokenType]

    _mask_nl_ws: List[bool]
    _mask_nl: List[bool]
    _mask_ws: List[bool]

    def __init__(self, tokens: List[RawToken], file_name: str = "", error_formatter: Optional[ErrorFormatter] = None, injection_adjust_pos: int = 0) -> None:
        self._pos = 0
        self._tokens = tokens
        self._token_types = [token.token_type for token in tokens]
        self._tokens_len = len(tokens)
        self._error = ParserErrors.SyntaxError()
        self._error_formatter = error_formatter or ErrorFormatter(tokens, file_name)
        self._injection_adjust_pos = injection_adjust_pos

        self._identifier_characters = [RawTokenType.TkCharacter, RawTokenType.TkDigit, RawTokenType.TkUnderscore]
        self._upper_identifier_characters = [RawTokenType.TkCharacter, RawTokenType.TkDigit]
        self._nl_ws_characters = [RawTokenType.TkWhitespace, RawTokenType.TkNewLine]
        self._nl_characters = RawTokenType.TkNewLine
        self._ws_characters = RawTokenType.TkWhitespace
        self._stringable_characters = [SppTokenType.LxNumber, SppTokenType.LxString]

        self._mask_nl_ws = [t not in [RawTokenType.TkNewLine, RawTokenType.TkWhitespace] for t in self._token_types]
        self._mask_nl    = [t not in [RawTokenType.TkNewLine] for t in self._token_types]
        self._mask_ws    = [t not in [RawTokenType.TkWhitespace] for t in self._token_types]

    @inline
    def current_pos(self) -> int:
        return self._pos + self._injection_adjust_pos

    # ===== TECHNIQUES =====

    @inline
    def parse_once[T](self, method: Callable[..., T]) -> T:
        pos = self._pos
        result = method()
        if result is None:
            self._pos = pos
        return result

    @inline
    def parse_optional[T](self, method: Callable[..., T]) -> Optional[T]:
        pos = self._pos
        result = method()
        if result is None:
            self._pos = pos
        return result

    @inline
    def parse_zero_or_more[T, S](self, method: Callable[..., T], separator: Callable[..., S]) -> Seq[T]:
        done_1_parse = False
        results = []
        temp_pos = self._pos

        while True:
            if done_1_parse:
                sep = self.parse_optional(separator)
                if sep is None:
                    break

            ast = self.parse_optional(method)
            if ast is not None:
                results.append(ast)
                done_1_parse = True
                temp_pos = self._pos
            else:
                self._pos = temp_pos
                break

        return results

    @inline
    def parse_one_or_more[T, S](self, method: Callable[..., T], separator: Callable[..., S]) -> Optional[Seq[T]]:
        results = self.parse_zero_or_more(method, separator)
        if len(results) < 1:
            self.store_error(self._pos, "Expected at least one element")
        return results if len(results) > 0 else None

    @inline
    def parse_two_or_more[T, S](self, method: Callable[..., T], separator: Callable[..., S]) -> Optional[Seq[T]]:
        results = self.parse_zero_or_more(method, separator)
        if len(results) < 2:
            self.store_error(self._pos, "Expected at least two elements")
        return results if len(results) > 1 else None

    @inline
    def parse_alternate[Ts](self, methods: List[Callable[..., *Ts]]) -> Union[*Ts]:
        ast = None
        for method in methods:
            ast = self.parse_optional(method)
            if ast is not None:
                break
        if ast is None:
            self.store_error(self._pos, "Expected one of the alternatives")
        return ast

    # ===== PROGRAM =====

    def parse(self):
        root = self.parse_root()
        if root is None:
            self._error.throw(self._error_formatter)
        return root

    def parse_root(self) -> Optional[Asts.ModulePrototypeAst]:
        p1 = self.parse_once(self.parse_module_prototype)
        if p1 is None: return None
        p2 = self.parse_eof()
        if p2 is None: return None
        return p1

    def parse_eof(self) -> Optional[Asts.TokenAst]:
        return self.parse_token_raw(RawTokenType.EndOfFile, SppTokenType.NoToken)

    # ===== MODULES =====

    def parse_module_prototype(self) -> Optional[Asts.ModulePrototypeAst]:
        p1 = self.parse_once(self.parse_module_implementation)
        if p1 is None: return None
        return Asts.ModulePrototypeAst(p1.pos, p1)

    def parse_module_implementation(self) -> Optional[Asts.ModuleImplementationAst]:
        p1 = self.parse_zero_or_more(self.parse_module_member, self.parse_newline)
        return Asts.ModuleImplementationAst(p1[0].pos if p1 else 0, p1)

    def parse_module_member(self) -> Optional[Asts.ModuleMemberAst]:
        p1 = self.parse_alternate([
            self.parse_function_prototype,
            self.parse_class_prototype,
            self.parse_sup_prototype_extension,
            self.parse_sup_prototype_functions,
            self.parse_global_use_statement,
            self.parse_global_cmp_statement])
        return p1

    # ===== CLASSES =====

    def parse_class_prototype(self) -> Optional[Asts.ClassPrototypeAst]:
        p1 = self.parse_zero_or_more(self.parse_annotation, self.parse_newline)
        p2 = self.parse_once(self.parse_keyword_cls)
        if p2 is None: return None
        p3 = self.parse_once(self.parse_upper_identifier)
        if p3 is None: return None
        p4 = self.parse_optional(self.parse_generic_parameters)
        p5 = self.parse_optional(self.parse_where_block)
        p6 = self.parse_once(self.parse_class_implementation)
        if p6 is None: return None
        return Asts.ClassPrototypeAst((p1[0] if p1 else p2).pos, p1, p2, Asts.TypeSingleAst.from_identifier(p3), p4, p5, p6)

    def parse_class_implementation(self) -> Optional[Asts.ClassImplementationAst]:
        p1 = self.parse_once(self.parse_token_left_curly_brace)
        if p1 is None: return None
        p2 = self.parse_zero_or_more(self.parse_class_member, self.parse_newline)
        p3 = self.parse_once(self.parse_token_right_curly_brace)
        if p3 is None: return None
        return Asts.ClassImplementationAst(p1.pos, p1, p2, p3)

    def parse_class_member(self) -> Optional[Asts.ClassMemberAst]:
        p1 = self.parse_once(self.parse_class_attribute)
        if p1 is None: return None
        return p1

    def parse_class_attribute(self) -> Optional[Asts.ClassAttributeAst]:
        p1 = self.parse_zero_or_more(self.parse_annotation, self.parse_newline)
        p2 = self.parse_once(self.parse_identifier)
        if p2 is None: return None
        p3 = self.parse_once(self.parse_token_colon)
        if p3 is None: return None
        p4 = self.parse_once(self.parse_type)
        if p4 is None: return None
        p5 = self.parse_optional(self.parse_class_attribute_default_value)
        return Asts.ClassAttributeAst((p1[0] if p1 else p2).pos, p1, p2, p3, p4, p5)

    def parse_class_attribute_default_value(self) -> Optional[Asts.ExpressionAst]:
        p1 = self.parse_once(self.parse_token_assign)
        if p1 is None: return None
        p2 = self.parse_once(self.parse_cmp_value)
        if p2 is None: return None
        return p2

    # ===== SUPERIMPOSITION =====

    def parse_sup_prototype_functions(self) -> Optional[Asts.SupPrototypeFunctionsAst]:
        p1 = self.parse_once(self.parse_keyword_sup)
        if p1 is None: return None
        p2 = self.parse_optional(self.parse_generic_parameters)
        p3 = self.parse_once(self.parse_type)
        if p3 is None: return None
        p4 = self.parse_optional(self.parse_where_block)
        p5 = self.parse_once(self.parse_sup_implementation)
        if p5 is None: return None
        return Asts.SupPrototypeFunctionsAst(p1.pos, p1, p2, p3, p4, p5)

    def parse_sup_prototype_extension(self) -> Optional[Asts.SupPrototypeExtensionAst]:
        p1 = self.parse_once(self.parse_keyword_sup)
        if p1 is None: return None
        p2 = self.parse_optional(self.parse_generic_parameters)
        p3 = self.parse_once(self.parse_type)
        if p3 is None: return None
        p4 = self.parse_once(self.parse_keyword_ext)
        if p4 is None: return None
        p5 = self.parse_once(self.parse_type)
        if p5 is None: return None
        p6 = self.parse_optional(self.parse_where_block)
        p7 = self.parse_once(self.parse_sup_implementation)
        if p7 is None: return None
        return Asts.SupPrototypeExtensionAst(p1.pos, p1, p2, p3, p4, p5, p6, p7)

    def parse_sup_implementation(self) -> Optional[Asts.SupImplementationAst]:
        p1 = self.parse_once(self.parse_token_left_curly_brace)
        if p1 is None: return None
        p2 = self.parse_zero_or_more(self.parse_sup_member, self.parse_newline)
        p3 = self.parse_once(self.parse_token_right_curly_brace)
        if p3 is None: return None
        return Asts.SupImplementationAst(p1.pos, p1, p2, p3)

    def parse_sup_member(self) -> Optional[Asts.SupMemberAst]:
        p1 = self.parse_alternate([
            self.parse_sup_method_prototype,
            self.parse_sup_use_statement,
            self.parse_sup_cmp_statement])
        return p1

    def parse_sup_method_prototype(self) -> Optional[Asts.FunctionPrototypeAst]:
        p1 = self.parse_once(self.parse_function_prototype)
        if p1 is None: return None
        return p1

    def parse_sup_use_statement(self) -> Optional[Asts.SupUseStatementAst]:
        p1 = self.parse_zero_or_more(self.parse_annotation, self.parse_newline)
        p2 = self.parse_once(self.parse_use_alias_statement)
        if p2 is None: return None
        p2.annotations = p1
        return p2

    def parse_sup_cmp_statement(self) -> Optional[Asts.SupCmpStatementAst]:
        p1 = self.parse_zero_or_more(self.parse_annotation, self.parse_newline)
        p2 = self.parse_once(self.parse_cmp_statement)
        if p2 is None: return None
        p2.annotations = p1
        return p2

    # ===== FUNCTIONS =====

    def parse_function_prototype(self) -> Optional[Asts.FunctionPrototypeAst]:
        p1 = self.parse_alternate([
            self.parse_subroutine_prototype,
            self.parse_coroutine_prototype])
        return p1

    def parse_subroutine_prototype(self) -> Optional[Asts.SubroutinePrototypeAst]:
        p1 = self.parse_zero_or_more(self.parse_annotation, self.parse_newline)
        p2 = self.parse_once(self.parse_keyword_fun)
        if p2 is None: return None
        p3 = self.parse_once(self.parse_identifier)
        if p3 is None: return None
        p4 = self.parse_optional(self.parse_generic_parameters)
        p5 = self.parse_once(self.parse_function_parameters)
        if p5 is None: return None
        p6 = self.parse_once(self.parse_token_arrow_right)
        if p6 is None: return None
        p7 = self.parse_once(self.parse_type)
        if p7 is None: return None
        p8 = self.parse_optional(self.parse_where_block)
        p9 = self.parse_once(self.parse_function_implementation)
        if p9 is None: return None
        return Asts.SubroutinePrototypeAst((p1[0] if p1 else p2).pos, p1, p2, p3, p4, p5, p6, p7, p8, p9)

    def parse_coroutine_prototype(self) -> Optional[Asts.CoroutinePrototypeAst]:
        p1 = self.parse_zero_or_more(self.parse_annotation, self.parse_newline)
        p2 = self.parse_once(self.parse_keyword_cor)
        if p2 is None: return None
        p3 = self.parse_once(self.parse_identifier)
        if p3 is None: return None
        p4 = self.parse_optional(self.parse_generic_parameters)
        p5 = self.parse_once(self.parse_function_parameters)
        if p5 is None: return None
        p6 = self.parse_once(self.parse_token_arrow_right)
        if p6 is None: return None
        p7 = self.parse_once(self.parse_type)
        if p7 is None: return None
        p8 = self.parse_optional(self.parse_where_block)
        p9 = self.parse_once(self.parse_function_implementation)
        if p9 is None: return None
        return Asts.CoroutinePrototypeAst((p1[0] if p1 else p2).pos, p1, p2, p3, p4, p5, p6, p7, p8, p9)

    def parse_function_implementation(self) -> Optional[Asts.FunctionImplementationAst]:
        p1 = self.parse_once(self.parse_token_left_curly_brace)
        if p1 is None: return None
        p2 = self.parse_zero_or_more(self.parse_function_member, self.parse_newline)
        p3 = self.parse_once(self.parse_token_right_curly_brace)
        if p3 is None: return None
        return Asts.FunctionImplementationAst(p1.pos, p1, p2, p3)

    def parse_function_member(self) -> Optional[Asts.FunctionMemberAst]:
        p1 = self.parse_once(self.parse_statement)
        if p1 is None: return None
        return p1

    def parse_function_call_arguments(self) -> Optional[Asts.FunctionCallArgumentGroupAst]:
        p1 = self.parse_once(self.parse_token_left_parenthesis)
        if p1 is None: return None
        p2 = self.parse_zero_or_more(self.parse_function_call_argument, self.parse_token_comma)
        p3 = self.parse_once(self.parse_token_right_parenthesis)
        if p3 is None: return None
        return Asts.FunctionCallArgumentGroupAst(p1.pos, p1, p2, p3)

    def parse_function_call_argument(self) -> Optional[Asts.FunctionCallArgumentAst]:
        p1 = self.parse_alternate([
            self.parse_function_call_argument_named,
            self.parse_function_call_argument_unnamed])
        return p1

    def parse_function_call_argument_unnamed(self) -> Optional[Asts.FunctionCallArgumentUnnamedAst]:
        p1 = self.parse_optional(self.parse_convention)
        p2 = self.parse_optional(self.parse_token_double_dot)
        p3 = self.parse_once(self.parse_expression)
        if p3 is None: return None
        return Asts.FunctionCallArgumentUnnamedAst((p1 or p2 or p3).pos, p1, p2, p3)

    def parse_function_call_argument_named(self) -> Optional[Asts.FunctionCallArgumentNamedAst]:
        p1 = self.parse_once(self.parse_identifier)
        if p1 is None: return None
        p2 = self.parse_once(self.parse_token_assign)
        if p2 is None: return None
        p3 = self.parse_optional(self.parse_convention)
        p4 = self.parse_once(self.parse_expression)
        if p4 is None: return None
        return Asts.FunctionCallArgumentNamedAst(p1.pos, p1, p2, p3, p4)

    def parse_function_parameters(self) -> Optional[Asts.FunctionParameterGroupAst]:
        p1 = self.parse_once(self.parse_token_left_parenthesis)
        if p1 is None: return None
        p2 = self.parse_zero_or_more(self.parse_function_parameter, self.parse_token_comma)
        p3 = self.parse_once(self.parse_token_right_parenthesis)
        if p3 is None: return None
        return Asts.FunctionParameterGroupAst(p1.pos, p1, p2, p3)

    def parse_function_parameter(self) -> Optional[Asts.FunctionParameterAst]:
        p1 = self.parse_alternate([
            self.parse_function_parameter_self_with_arbitrary_type,
            self.parse_function_parameter_variadic,
            self.parse_function_parameter_optional,
            self.parse_function_parameter_required,
            self.parse_function_parameter_self])
        return p1

    def parse_function_parameter_self(self) -> Optional[Asts.FunctionParameterSelfAst]:
        p1 = self.parse_optional(self.parse_keyword_mut)
        p2 = self.parse_optional(self.parse_convention)
        p3 = self.parse_once(self.parse_self_keyword)
        if p3 is None: return None
        return Asts.FunctionParameterSelfAst((p1 or p2 or p3).pos, p1, p2, p3)

    def parse_function_parameter_self_with_arbitrary_type(self) -> Optional[Asts.FunctionParameterSelfAst]:
        p1 = self.parse_optional(self.parse_keyword_mut)
        p2 = self.parse_once(self.parse_self_keyword)
        if p2 is None: return None
        p3 = self.parse_once(self.parse_token_colon)
        if p3 is None: return None
        p4 = self.parse_once(self.parse_type)
        if p4 is None: return None
        return Asts.FunctionParameterSelfAst((p1 or p2).pos, p1, None, p2, p4)

    def parse_function_parameter_required(self) -> Optional[Asts.FunctionParameterRequiredAst]:
        p1 = self.parse_once(self.parse_local_variable)
        if p1 is None: return None
        p2 = self.parse_once(self.parse_token_colon)
        if p2 is None: return None
        p3 = self.parse_once(self.parse_type)
        if p3 is None: return None
        return Asts.FunctionParameterRequiredAst(p1.pos, p1, p2, p3)

    def parse_function_parameter_optional(self) -> Optional[Asts.FunctionParameterOptionalAst]:
        p1 = self.parse_once(self.parse_local_variable)
        if p1 is None: return None
        p2 = self.parse_once(self.parse_token_colon)
        if p2 is None: return None
        p3 = self.parse_once(self.parse_type)
        if p3 is None: return None
        p4 = self.parse_once(self.parse_token_assign)
        if p4 is None: return None
        p5 = self.parse_once(self.parse_cmp_value)
        if p5 is None: return None
        return Asts.FunctionParameterOptionalAst(p1.pos, p1, p2, p3, p4, p5)

    def parse_function_parameter_variadic(self) -> Optional[Asts.FunctionParameterVariadicAst]:
        p1 = self.parse_once(self.parse_token_double_dot)
        if p1 is None: return None
        p2 = self.parse_once(self.parse_local_variable)
        if p2 is None: return None
        p3 = self.parse_once(self.parse_token_colon)
        if p3 is None: return None
        p4 = self.parse_once(self.parse_type)
        if p4 is None: return None
        return Asts.FunctionParameterVariadicAst(p1.pos, p1, p2, p3, p4)

    # ===== GENERICS =====

    def parse_generic_arguments(self) -> Optional[Asts.GenericArgumentGroupAst]:
        p1 = self.parse_once(self.parse_token_left_square_bracket)
        if p1 is None: return None
        p2 = self.parse_zero_or_more(self.parse_generic_argument, self.parse_token_comma)
        p3 = self.parse_once(self.parse_token_right_square_bracket)
        if p3 is None: return None
        return Asts.GenericArgumentGroupAst(p1.pos, p1, p2, p3)

    def parse_generic_argument(self) -> Optional[Asts.GenericArgumentAst]:
        p1 = self.parse_alternate([
            self.parse_generic_type_argument_named,
            self.parse_generic_type_argument_unnamed,
            self.parse_generic_comp_argument_named,
            self.parse_generic_comp_argument_unnamed])
        return p1

    def parse_generic_type_argument_named(self) -> Optional[Asts.GenericTypeArgumentNamedAst]:
        p1 = self.parse_once(self.parse_upper_identifier)
        if p1 is None: return None
        p2 = self.parse_once(self.parse_token_assign)
        if p2 is None: return None
        p3 = self.parse_once(self.parse_type)
        if p3 is None: return None
        return Asts.GenericTypeArgumentNamedAst(p1.pos, Asts.TypeSingleAst.from_identifier(p1), p2, p3)

    def parse_generic_type_argument_unnamed(self) -> Optional[Asts.GenericTypeArgumentUnnamedAst]:
        p1 = self.parse_once(self.parse_type)
        if p1 is None: return None
        return Asts.GenericTypeArgumentUnnamedAst(p1.pos, p1)

    def parse_generic_comp_argument_named(self) -> Optional[Asts.GenericCompArgumentNamedAst]:
        p1 = self.parse_once(self.parse_identifier)
        if p1 is None: return None
        p2 = self.parse_once(self.parse_token_assign)
        if p2 is None: return None
        p3 = self.parse_once(self.parse_cmp_value)
        if p3 is None: return None
        return Asts.GenericCompArgumentNamedAst(p1.pos, Asts.TypeSingleAst.from_identifier(p1), p2, p3)

    def parse_generic_comp_argument_unnamed(self) -> Optional[Asts.GenericCompArgumentUnnamedAst]:
        p1 = self.parse_once(self.parse_cmp_value)
        if p1 is None: return None
        return Asts.GenericCompArgumentUnnamedAst(p1.pos, p1)

    def parse_generic_parameters(self) -> Optional[Asts.GenericParameterGroupAst]:
        p1 = self.parse_once(self.parse_token_left_square_bracket)
        if p1 is None: return None
        p2 = self.parse_one_or_more(self.parse_generic_parameter, self.parse_token_comma)
        if p2 is None: return None
        p3 = self.parse_once(self.parse_token_right_square_bracket)
        if p3 is None: return None
        return Asts.GenericParameterGroupAst(p1.pos, p1, p2, p3)

    def parse_generic_parameter(self) -> Optional[Asts.GenericParameterAst]:
        p1 = self.parse_alternate([
            self.parse_generic_type_parameter_variadic,
            self.parse_generic_type_parameter_optional,
            self.parse_generic_type_parameter_required,
            self.parse_generic_comp_parameter_variadic,
            self.parse_generic_comp_parameter_optional,
            self.parse_generic_comp_parameter_required])
        return p1

    def parse_generic_type_parameter_required(self) -> Optional[Asts.GenericTypeParameterRequiredAst]:
        p1 = self.parse_once(self.parse_upper_identifier)
        if p1 is None: return None
        p2 = self.parse_optional(self.parse_generic_inline_constraints)
        return Asts.GenericTypeParameterRequiredAst(p1.pos, Asts.TypeSingleAst.from_identifier(p1), p2)

    def parse_generic_type_parameter_optional(self) -> Optional[Asts.GenericTypeParameterOptionalAst]:
        p1 = self.parse_once(self.parse_upper_identifier)
        if p1 is None: return None
        p2 = self.parse_optional(self.parse_generic_inline_constraints)
        p3 = self.parse_once(self.parse_token_assign)
        if p3 is None: return None
        p4 = self.parse_once(self.parse_type)
        if p4 is None: return None
        return Asts.GenericTypeParameterOptionalAst(p1.pos, Asts.TypeSingleAst.from_identifier(p1), p2, p3, p4)

    def parse_generic_type_parameter_variadic(self) -> Optional[Asts.GenericTypeParameterVariadicAst]:
        p1 = self.parse_once(self.parse_token_double_dot)
        if p1 is None: return None
        p2 = self.parse_once(self.parse_upper_identifier)
        if p2 is None: return None
        p3 = self.parse_optional(self.parse_generic_inline_constraints)
        return Asts.GenericTypeParameterVariadicAst(p1.pos, p1, Asts.TypeSingleAst.from_identifier(p2), p3)

    def parse_generic_comp_parameter_required(self) -> Optional[Asts.GenericCompParameterRequiredAst]:
        p1 = self.parse_once(self.parse_keyword_cmp)
        if p1 is None: return None
        p2 = self.parse_once(self.parse_identifier)
        if p2 is None: return None
        p3 = self.parse_once(self.parse_token_colon)
        if p3 is None: return None
        p4 = self.parse_once(self.parse_type)
        if p4 is None: return None
        return Asts.GenericCompParameterRequiredAst(p1.pos, p1, Asts.TypeSingleAst.from_identifier(p2), p3, p4)

    def parse_generic_comp_parameter_optional(self) -> Optional[Asts.GenericCompParameterOptionalAst]:
        p1 = self.parse_once(self.parse_keyword_cmp)
        if p1 is None: return None
        p2 = self.parse_once(self.parse_identifier)
        if p2 is None: return None
        p3 = self.parse_once(self.parse_token_colon)
        if p3 is None: return None
        p4 = self.parse_once(self.parse_type)
        if p4 is None: return None
        p5 = self.parse_once(self.parse_token_assign)
        if p5 is None: return None
        p6 = self.parse_once(self.parse_cmp_value)
        if p6 is None: return None
        return Asts.GenericCompParameterOptionalAst(p1.pos, p1, Asts.TypeSingleAst.from_identifier(p2), p3, p4, p5, p6)

    def parse_generic_comp_parameter_variadic(self) -> Optional[Asts.GenericCompParameterVariadicAst]:
        p1 = self.parse_once(self.parse_keyword_cmp)
        if p1 is None: return None
        p2 = self.parse_once(self.parse_token_double_dot)
        if p2 is None: return None
        p3 = self.parse_once(self.parse_identifier)
        if p3 is None: return None
        p4 = self.parse_once(self.parse_token_colon)
        if p4 is None: return None
        p5 = self.parse_once(self.parse_type)
        if p5 is None: return None
        return Asts.GenericCompParameterVariadicAst(p1.pos, p1, p2, Asts.TypeSingleAst.from_identifier(p3), p4, p5)

    def parse_generic_inline_constraints(self) -> Optional[Asts.GenericTypeParameterInlineConstraintsAst]:
        p1 = self.parse_once(self.parse_token_colon)
        if p1 is None: return None
        p2 = self.parse_one_or_more(self.parse_type, self.parse_token_comma)
        if p2 is None: return None
        return Asts.GenericTypeParameterInlineConstraintsAst(p1.pos, p1, p2)

    # ===== WHERE =====

    def parse_where_block(self) -> Optional[Asts.WhereBlockAst]:
        p1 = self.parse_once(self.parse_keyword_where)
        if p1 is None: return None
        p2 = self.parse_once(self.parse_where_block_constraints_group)
        if p2 is None: return None
        return Asts.WhereBlockAst(p1.pos, p1, p2)

    def parse_where_block_constraints_group(self) -> Optional[Asts.WhereConstraintsGroupAst]:
        p1 = self.parse_once(self.parse_token_left_square_bracket)
        if p1 is None: return None
        p2 = self.parse_one_or_more(self.parse_where_block_constraints, self.parse_token_comma)
        if p2 is None: return None
        p3 = self.parse_once(self.parse_token_right_square_bracket)
        if p3 is None: return None
        return Asts.WhereConstraintsGroupAst(p1.pos, p1, p2, p3)

    def parse_where_block_constraints(self) -> Optional[Asts.WhereConstraintsAst]:
        p1 = self.parse_one_or_more(self.parse_type, self.parse_token_comma)
        if p1 is None: return None
        p2 = self.parse_once(self.parse_token_colon)
        if p2 is None: return None
        p3 = self.parse_once(self.parse_type)
        if p3 is None: return None  # ban conventions in semantic analysis here
        return Asts.WhereConstraintsAst(p1[0].pos, p1, p2, p3)

    # ===== ANNOTATIONS =====

    def parse_annotation(self) -> Optional[Asts.AnnotationAst]:
        p1 = self.parse_once(self.parse_token_at)
        if p1 is None: return None
        p2 = self.parse_once(self.parse_identifier)
        if p2 is None: return None
        return Asts.AnnotationAst(p1.pos, p1, p2)

    # ===== EXPRESSIONS =====

    def parse_expression(self) -> Optional[Asts.ExpressionAst]:
        p1 = self.parse_once(self.parse_binary_expression_precedence_level_1)
        if p1 is None: return None
        return p1

    def parse_binary_expression_precedence_level_n_rhs(self, op, rhs) -> Optional[Tuple[Asts.TokenAst, Asts.ExpressionAst]]:
        p1 = self.parse_once(op)
        if p1 is None: return None
        p2 = self.parse_once(rhs)
        if p2 is None: return None
        return p1, p2

    def parse_binary_expression_precedence_level_n(self, lhs, op, rhs, is_: bool = False) -> Optional[Asts.BinaryExpressionAst | Asts.IsExpressionAst]:
        p1 = self.parse_once(lhs)
        if p1 is None: return None
        p2 = self.parse_optional(lambda: self.parse_binary_expression_precedence_level_n_rhs(op, rhs))
        if p2 is None: return p1
        Constructor: type = Asts.BinaryExpressionAst if not is_ else Asts.IsExpressionAst
        return Constructor(p1.pos, p1, p2[0], p2[1])

    def parse_binary_expression_precedence_level_1(self) -> Optional[Asts.ExpressionAst]:
        return self.parse_binary_expression_precedence_level_n(self.parse_binary_expression_precedence_level_2, self.parse_binary_op_precedence_level_1, self.parse_binary_expression_precedence_level_1)

    def parse_binary_expression_precedence_level_2(self) -> Optional[Asts.ExpressionAst]:
        return self.parse_binary_expression_precedence_level_n(self.parse_binary_expression_precedence_level_3, self.parse_binary_op_precedence_level_2, self.parse_binary_expression_precedence_level_2)

    def parse_binary_expression_precedence_level_3(self) -> Optional[Asts.ExpressionAst]:
        return self.parse_binary_expression_precedence_level_n(self.parse_binary_expression_precedence_level_4, self.parse_binary_op_precedence_level_3, self.parse_pattern_group_destructure, is_=True)

    def parse_binary_expression_precedence_level_4(self) -> Optional[Asts.ExpressionAst]:
        return self.parse_binary_expression_precedence_level_n(self.parse_binary_expression_precedence_level_5, self.parse_binary_op_precedence_level_4, self.parse_binary_expression_precedence_level_4)

    def parse_binary_expression_precedence_level_5(self) -> Optional[Asts.ExpressionAst]:
        return self.parse_binary_expression_precedence_level_n(self.parse_binary_expression_precedence_level_6, self.parse_binary_op_precedence_level_5, self.parse_binary_expression_precedence_level_5)

    def parse_binary_expression_precedence_level_6(self) -> Optional[Asts.ExpressionAst]:
        return self.parse_binary_expression_precedence_level_n(self.parse_unary_expression, self.parse_binary_op_precedence_level_6, self.parse_binary_expression_precedence_level_6)

    def parse_unary_expression(self) -> Optional[Asts.ExpressionAst]:
        p1 = self.parse_zero_or_more(self.parse_unary_op, self.parse_nothing)
        p2 = self.parse_once(self.parse_postfix_expression)
        if p2 is None: return None
        return reduce(lambda acc, x: Asts.UnaryExpressionAst(x.pos, x, acc), p1[::-1], p2)

    def parse_postfix_expression(self) -> Optional[Asts.ExpressionAst]:
        p1 = self.parse_once(self.parse_primary_expression)
        if p1 is None: return None
        p2 = self.parse_zero_or_more(self.parse_postfix_op, self.parse_nothing)
        return reduce(lambda acc, x: Asts.PostfixExpressionAst(acc.pos, acc, x), p2, p1)

    def parse_primary_expression(self) -> Optional[Asts.ExpressionAst]:
        p1 = self.parse_alternate([
            self.parse_lambda_expression,
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
            self.parse_token_double_dot])
        return p1

    def parse_parenthesized_expression(self) -> Optional[Asts.ParenthesizedExpressionAst]:
        p1 = self.parse_once(self.parse_token_left_parenthesis)
        if p1 is None: return None
        p2 = self.parse_once(self.parse_expression)
        if p2 is None: return None
        p3 = self.parse_once(self.parse_token_right_parenthesis)
        if p3 is None: return None
        return Asts.ParenthesizedExpressionAst(p1.pos, p1, p2, p3)

    def parse_self_keyword(self) -> Optional[Asts.IdentifierAst]:
        p1 = self.parse_once(self.parse_keyword_self_value)
        if p1 is None: return None
        return Asts.IdentifierAst(p1.pos, p1.token_data)

    # ===== EXPRESSION STATEMENTS =====

    def parse_case_expression(self) -> Optional[Asts.CaseExpressionAst]:
        p1 = self.parse_alternate([
            self.parse_case_expression_patterns,
            self.parse_case_expression_simple])
        return p1

    def parse_case_expression_patterns(self) -> Optional[Asts.CaseExpressionAst]:
        p1 = self.parse_once(self.parse_keyword_case)
        if p1 is None: return None
        p2 = self.parse_once(self.parse_expression)
        if p2 is None: return None
        p3 = self.parse_once(self.parse_keyword_of)
        if p3 is None: return None
        p4 = self.parse_one_or_more(self.parse_case_expression_branch, self.parse_newline)
        if p4 is None: return None
        return Asts.CaseExpressionAst(p1.pos, p1, p2, p3, p4)

    def parse_case_expression_simple(self) -> Optional[Asts.CaseExpressionAst]:
        p1 = self.parse_once(self.parse_keyword_case)
        if p1 is None: return None
        p2 = self.parse_once(self.parse_expression)
        if p2 is None: return None
        p3 = self.parse_once(self.parse_inner_scope)
        if p3 is None: return None
        p4 = self.parse_zero_or_more(self.parse_case_expression_branch_simple, self.parse_newline)
        return Asts.CaseExpressionAst.from_simple(p1, p2, p3, p4)

    def parse_loop_expression(self) -> Optional[Asts.LoopExpressionAst]:
        p1 = self.parse_once(self.parse_keyword_loop)
        if p1 is None: return None
        p2 = self.parse_once(self.parse_loop_expression_condition)
        if p2 is None: return None
        p3 = self.parse_once(self.parse_inner_scope)
        if p3 is None: return None
        p4 = self.parse_optional(self.parse_loop_else_statement)
        return Asts.LoopExpressionAst(p1.pos, p1, p2, p3, p4)

    def parse_loop_expression_condition(self) -> Optional[Asts.LoopConditionAst]:
        p1 = self.parse_alternate([
            self.parse_loop_expression_condition_iterable,
            self.parse_loop_expression_condition_boolean])
        return p1

    def parse_loop_expression_condition_boolean(self) -> Optional[Asts.LoopConditionBooleanAst]:
        p1 = self.parse_once(self.parse_expression)
        if p1 is None: return None
        return Asts.LoopConditionBooleanAst(p1.pos, p1)

    def parse_loop_expression_condition_iterable(self) -> Optional[Asts.LoopConditionIterableAst]:
        p1 = self.parse_once(self.parse_local_variable)
        if p1 is None: return None
        p2 = self.parse_once(self.parse_keyword_in)
        if p2 is None: return None
        p3 = self.parse_once(self.parse_expression)
        if p3 is None: return None
        return Asts.LoopConditionIterableAst(p1.pos, p1, p2, p3)

    def parse_loop_else_statement(self) -> Optional[Asts.LoopElseStatementAst]:
        p1 = self.parse_once(self.parse_keyword_else)
        if p1 is None: return None
        p2 = self.parse_once(self.parse_inner_scope)
        if p2 is None: return None
        return Asts.LoopElseStatementAst(p1.pos, p1, p2)

    def parse_gen_expression(self) -> Optional[Asts.GenExpressionAst]:
        p1 = self.parse_alternate([
            self.parse_gen_expression_unroll,
            self.parse_gen_expression_normal])
        return p1

    def parse_gen_expression_normal(self) -> Optional[Asts.GenExpressionAst]:
        p1 = self.parse_alternate([
            self.parse_gen_expression_normal_with_expression,
            self.parse_gen_expression_normal_no_expression])
        return p1

    def parse_gen_expression_normal_no_expression(self) -> Optional[Asts.GenExpressionAst]:
        p1 = self.parse_once(self.parse_keyword_gen)
        if p1 is None: return None
        return Asts.GenExpressionAst(p1.pos, p1, None, None, None)

    def parse_gen_expression_normal_with_expression(self) -> Optional[Asts.GenExpressionAst]:
        p1 = self.parse_once(self.parse_keyword_gen)
        if p1 is None: return None
        p2 = self.parse_optional(self.parse_convention)
        p3 = self.parse_once(self.parse_expression)
        if p3 is None: return None
        return Asts.GenExpressionAst(p1.pos, p1, None, p2, p3)

    def parse_gen_expression_unroll(self) -> Optional[Asts.GenExpressionAst]:
        p1 = self.parse_once(self.parse_keyword_gen)
        if p1 is None: return None
        p2 = self.parse_once(self.parse_keyword_with)
        if p2 is None: return None
        p3 = self.parse_once(self.parse_expression)
        if p3 is None: return None
        return Asts.GenExpressionAst(p1.pos, p1, p2, None, p3)

    # ===== STATEMENTS =====

    def parse_ret_statement(self) -> Optional[Asts.RetStatementAst]:
        p1 = self.parse_once(self.parse_keyword_ret)
        if p1 is None: return None
        p2 = self.parse_optional(self.parse_expression)
        return Asts.RetStatementAst(p1.pos, p1, p2)

    def parse_exit_statement(self) -> Optional[Asts.LoopControlFlowStatementAst]:
        p1 = self.parse_one_or_more(self.parse_keyword_exit, self.parse_nothing)
        if p1 is None: return None
        p2 = self.parse_optional(self.parse_exit_statement_final_action)
        return Asts.LoopControlFlowStatementAst(p1[0].pos, p1, p2)

    def parse_exit_statement_final_action(self) -> Optional[Asts.TokenAst | Asts.ExpressionAst]:
        p1 = self.parse_alternate([
            self.parse_keyword_skip,
            self.parse_expression])
        return p1

    def parse_skip_statement(self) -> Optional[Asts.LoopControlFlowStatementAst]:
        p1 = self.parse_once(self.parse_keyword_skip)
        if p1 is None: return None
        return Asts.LoopControlFlowStatementAst(p1.pos, [], p1)

    def parse_inner_scope(self) -> Optional[Asts.InnerScopeAst]:
        p1 = self.parse_once(self.parse_token_left_curly_brace)
        if p1 is None: return None
        p2 = self.parse_zero_or_more(self.parse_statement, self.parse_newline)
        p3 = self.parse_once(self.parse_token_right_curly_brace)
        if p3 is None: return None
        return Asts.InnerScopeAst(p1.pos, p1, p2, p3)

    def parse_statement(self) -> Optional[Asts.StatementAst]:
        p1 = self.parse_alternate([
            self.parse_use_statement,
            self.parse_let_statement,
            self.parse_ret_statement,
            self.parse_exit_statement,
            self.parse_skip_statement,
            self.parse_assignment_statement,
            self.parse_expression])
        return p1

    # ===== TYPEDEFS =====

    def parse_global_use_statement(self) -> Optional[Asts.UseStatementAst]:
        p1 = self.parse_zero_or_more(self.parse_annotation, self.parse_newline)
        p2 = self.parse_once(self.parse_use_statement)
        if p2 is None: return None
        p2.annotations = p1
        return p2

    def parse_use_statement(self) -> Optional[Asts.UseStatementAst]:
        p1 = self.parse_alternate([
            self.parse_use_alias_statement,
            self.parse_use_redux_statement])
        return p1

    def parse_use_alias_statement(self) -> Optional[Asts.UseStatementAliasAst]:
        p1 = self.parse_once(self.parse_keyword_use)
        if p1 is None: return None
        p2 = self.parse_once(self.parse_upper_identifier)
        if p2 is None: return None
        p3 = self.parse_optional(self.parse_generic_parameters)
        p4 = self.parse_once(self.parse_token_assign)
        if p4 is None: return None
        p5 = self.parse_once(self.parse_type)
        if p5 is None: return None
        return Asts.UseStatementAliasAst(p1.pos, [], p1, Asts.TypeSingleAst.from_identifier(p2), p3, p4, p5)

    def parse_use_redux_statement(self) -> Optional[Asts.UseStatementReduxAst]:
        p1 = self.parse_once(self.parse_keyword_use)
        if p1 is None: return None
        p2 = self.parse_once(self.parse_type_simple)
        if p2 is None: return None
        return Asts.UseStatementReduxAst(p1.pos, [], p1, p2)

    # ===== CMP-DECLARATIONS =====

    def parse_global_cmp_statement(self) -> Optional[Asts.CmpStatementAst]:
        p1 = self.parse_zero_or_more(self.parse_annotation, self.parse_newline)
        p2 = self.parse_once(self.parse_cmp_statement)
        if p2 is None: return None
        p2.annotations = p1
        return p2

    def parse_cmp_statement(self) -> Optional[Asts.CmpStatementAst]:
        p1 = self.parse_once(self.parse_keyword_cmp)
        if p1 is None: return None
        p2 = self.parse_once(self.parse_identifier)
        if p2 is None: return None
        p3 = self.parse_once(self.parse_token_colon)
        if p3 is None: return None
        p4 = self.parse_once(self.parse_type)
        if p4 is None: return None
        p5 = self.parse_once(self.parse_token_assign)
        if p5 is None: return None
        p6 = self.parse_once(self.parse_cmp_value)
        if p6 is None: return None
        return Asts.CmpStatementAst(p1.pos, [], p1, p2, p3, p4, p5, p6)

    # ===== LET-DECLARATIONS =====

    def parse_let_statement(self) -> Optional[Asts.LetStatementAst]:
        p1 = self.parse_alternate([
            self.parse_let_statement_initialized,
            self.parse_let_statement_uninitialized])
        return p1

    def parse_let_statement_initialized(self) -> Optional[Asts.LetStatementInitializedAst]:
        p1 = self.parse_once(self.parse_keyword_let)
        if p1 is None: return None
        p2 = self.parse_once(self.parse_local_variable)
        if p2 is None: return None
        p3 = self.parse_optional(self.parse_let_statement_initialized_type)
        p4 = self.parse_once(self.parse_token_assign)
        if p4 is None: return None
        p5 = self.parse_once(self.parse_expression)
        if p5 is None: return None
        return Asts.LetStatementInitializedAst(p1.pos, p1, p2, p3, p4, p5)

    def parse_let_statement_initialized_type(self) -> Optional[Asts.TypeAst]:
        p1 = self.parse_once(self.parse_token_colon)
        if p1 is None: return None
        p2 = self.parse_once(self.parse_type)
        if p2 is None: return None
        return p2

    def parse_let_statement_uninitialized(self) -> Optional[Asts.LetStatementUninitializedAst]:
        p1 = self.parse_once(self.parse_keyword_let)
        if p1 is None: return None
        p2 = self.parse_once(self.parse_local_variable)
        if p2 is None: return None
        p3 = self.parse_once(self.parse_token_colon)
        if p3 is None: return None
        p4 = self.parse_once(self.parse_type)
        if p4 is None: return None
        return Asts.LetStatementUninitializedAst(p1.pos, p1, p2, p3, p4)

    def parse_local_variable(self) -> Asts.LocalVariableAst:
        p1 = self.parse_alternate([
            self.parse_local_variable_destructure_array,
            self.parse_local_variable_destructure_tuple,
            self.parse_local_variable_destructure_object,
            self.parse_local_variable_single_identifier])
        return p1

    def parse_local_variable_destructure_skip_argument(self) -> Optional[Asts.LocalVariableDestructureSkip1ArgumentAst]:
        p1 = self.parse_once(self.parse_token_underscore)
        if p1 is None: return None
        return Asts.LocalVariableDestructureSkip1ArgumentAst(p1.pos, p1)

    def parse_local_variable_destructure_skip_arguments(self) -> Optional[Asts.LocalVariableDestructureSkipNArgumentsAst]:
        p1 = self.parse_once(self.parse_token_double_dot)
        if p1 is None: return None
        p2 = self.parse_optional(self.parse_local_variable_single_identifier)
        return Asts.LocalVariableDestructureSkipNArgumentsAst(p1.pos, p1, p2)

    def parse_local_variable_single_identifier(self) -> Optional[Asts.LocalVariableSingleIdentifierAst]:
        p1 = self.parse_optional(self.parse_keyword_mut)
        p2 = self.parse_once(self.parse_identifier)
        if p2 is None: return None
        p3 = self.parse_optional(self.parse_local_variable_single_identifier_alias)
        return Asts.LocalVariableSingleIdentifierAst((p1 or p2).pos, p1, p2, p3)

    def parse_local_variable_single_identifier_alias(self) -> Optional[Asts.LocalVariableSingleIdentifierAliasAst]:
        p1 = self.parse_once(self.parse_keyword_as)
        if p1 is None: return None
        p2 = self.parse_once(self.parse_identifier)
        if p2 is None: return None
        return Asts.LocalVariableSingleIdentifierAliasAst(p1.pos, p1, p2)

    def parse_local_variable_destructure_array(self) -> Optional[Asts.LocalVariableDestructureArrayAst]:
        p1 = self.parse_once(self.parse_token_left_square_bracket)
        if p1 is None: return None
        p2 = self.parse_one_or_more(self.parse_local_variable_nested_for_destructure_array, self.parse_token_comma)
        if p2 is None: return None
        p3 = self.parse_once(self.parse_token_right_square_bracket)
        if p3 is None: return None
        return Asts.LocalVariableDestructureArrayAst(p1.pos, p1, p2, p3)

    def parse_local_variable_destructure_tuple(self) -> Optional[Asts.LocalVariableDestructureTupleAst]:
        p1 = self.parse_once(self.parse_token_left_parenthesis)
        if p1 is None: return None
        p2 = self.parse_one_or_more(self.parse_local_variable_nested_for_destructure_tuple, self.parse_token_comma)
        if p2 is None: return None
        p3 = self.parse_once(self.parse_token_right_parenthesis)
        if p3 is None: return None
        return Asts.LocalVariableDestructureTupleAst(p1.pos, p1, p2, p3)

    def parse_local_variable_destructure_object(self) -> Optional[Asts.LocalVariableDestructureObjectAst]:
        p1 = self.parse_once(self.parse_type_simple)
        if p1 is None: return None
        p2 = self.parse_once(self.parse_token_left_parenthesis)
        if p2 is None: return None
        p3 = self.parse_zero_or_more(self.parse_local_variable_nested_for_destructure_object, self.parse_token_comma)
        p4 = self.parse_once(self.parse_token_right_parenthesis)
        if p4 is None: return None
        return Asts.LocalVariableDestructureObjectAst(p1.pos, p1, p2, p3, p4)

    def parse_local_variable_attribute_binding(self) -> Optional[Asts.LocalVariableAttributeBindingAst]:
        p1 = self.parse_once(self.parse_identifier)
        if p1 is None: return None
        p2 = self.parse_once(self.parse_token_assign)
        if p2 is None: return None
        p3 = self.parse_once(self.parse_local_variable_nested_for_attribute_binding)
        if p3 is None: return None
        return Asts.LocalVariableAttributeBindingAst(p1.pos, p1, p2, p3)

    def parse_local_variable_nested_for_destructure_array(self) -> Optional[Asts.LocalVariableNestedForDestructureArrayAst]:
        p1 = self.parse_alternate([
            self.parse_local_variable_destructure_array,
            self.parse_local_variable_destructure_tuple,
            self.parse_local_variable_destructure_object,
            self.parse_local_variable_single_identifier,
            self.parse_local_variable_destructure_skip_arguments,
            self.parse_local_variable_destructure_skip_argument])
        return p1

    def parse_local_variable_nested_for_destructure_tuple(self) -> Optional[Asts.LocalVariableNestedForDestructureTupleAst]:
        p1 = self.parse_alternate([
            self.parse_local_variable_destructure_array,
            self.parse_local_variable_destructure_tuple,
            self.parse_local_variable_destructure_object,
            self.parse_local_variable_single_identifier,
            self.parse_local_variable_destructure_skip_arguments,
            self.parse_local_variable_destructure_skip_argument])
        return p1

    def parse_local_variable_nested_for_destructure_object(self) -> Optional[Asts.LocalVariableNestedForDestructureObjectAst]:
        p1 = self.parse_alternate([
            self.parse_local_variable_attribute_binding,
            self.parse_local_variable_single_identifier,
            self.parse_local_variable_destructure_skip_arguments])
        return p1

    def parse_local_variable_nested_for_attribute_binding(self) -> Optional[Asts.LocalVariableNestedForAttributeBindingAst]:
        p1 = self.parse_alternate([
            self.parse_local_variable_destructure_array,
            self.parse_local_variable_destructure_tuple,
            self.parse_local_variable_destructure_object,
            self.parse_local_variable_single_identifier])
        return p1

    # ===== ASSIGNMENT =====

    def parse_assignment_statement(self) -> Optional[Asts.AssignmentStatementAst]:
        p1 = self.parse_one_or_more(self.parse_expression, self.parse_token_comma)
        if p1 is None: return None
        p2 = self.parse_once(self.parse_token_assign)
        if p2 is None: return None
        p3 = self.parse_one_or_more(self.parse_expression, self.parse_token_comma)
        if p3 is None: return None
        return Asts.AssignmentStatementAst(p1[0].pos, p1, p2, p3)

    # ===== PATTERNS =====

    def parse_case_expression_branch_simple(self) -> Optional[Asts.CaseExpressionBranchAst]:
        p1 = self.parse_alternate([
            self.parse_pattern_statement_flavour_else_case,
            self.parse_pattern_statement_flavour_else])
        return p1

    def parse_case_expression_branch(self) -> Optional[Asts.CaseExpressionBranchAst]:
        p1 = self.parse_alternate([
            self.parse_pattern_statement_flavour_destructuring,
            self.parse_pattern_statement_flavour_non_destructuring,
            self.parse_pattern_statement_flavour_else_case,
            self.parse_pattern_statement_flavour_else])
        return p1

    def parse_pattern_statement_flavour_destructuring(self) -> Optional[Asts.CaseExpressionBranchAst]:
        p1 = self.parse_once(self.parse_keyword_is)
        if p1 is None: return None
        p2 = self.parse_one_or_more(self.parse_pattern_group_destructure, self.parse_token_comma)
        if p2 is None: return None
        p3 = self.parse_optional(self.parse_pattern_guard)
        p4 = self.parse_once(self.parse_inner_scope)
        if p4 is None: return None
        return Asts.CaseExpressionBranchAst(p1.pos, p1, p2, p3, p4)

    def parse_pattern_statement_flavour_non_destructuring(self) -> Optional[Asts.CaseExpressionBranchAst]:
        p1 = self.parse_once(self.parse_boolean_comparison_op)
        if p1 is None: return None
        p2 = self.parse_one_or_more(self.parse_pattern_variant_expression, self.parse_token_comma)
        if p2 is None: return None
        p3 = self.parse_once(self.parse_inner_scope)
        if p3 is None: return None
        return Asts.CaseExpressionBranchAst(p1.pos, p1, p2, None, p3)

    def parse_pattern_statement_flavour_else_case(self) -> Optional[Asts.CaseExpressionBranchAst]:
        p1 = self.parse_once(self.parse_pattern_variant_else_case)
        if p1 is None: return None
        return Asts.CaseExpressionBranchAst.from_else_to_else_case(p1.pos, p1)

    def parse_pattern_statement_flavour_else(self) -> Optional[Asts.CaseExpressionBranchAst]:
        p1 = self.parse_once(self.parse_pattern_variant_else)
        if p1 is None: return None
        p2 = self.parse_once(self.parse_inner_scope)
        if p2 is None: return None
        return Asts.CaseExpressionBranchAst(p1.pos, None, [p1], None, p2)

    def parse_pattern_group_destructure(self) -> Optional[Asts.PatternGroupDestructureAst]:
        p1 = self.parse_alternate([
            self.parse_pattern_variant_destructure_array,
            self.parse_pattern_variant_destructure_tuple,
            self.parse_pattern_variant_destructure_object])
        return p1

    def parse_pattern_variant_skip_argument(self) -> Optional[Asts.PatternVariantDestructureSkip1ArgumentAst]:
        p1 = self.parse_once(self.parse_token_underscore)
        if p1 is None: return None
        return Asts.PatternVariantDestructureSkip1ArgumentAst(p1.pos, p1)

    def parse_pattern_variant_skip_arguments(self) -> Optional[Asts.PatternVariantDestructureSkipNArgumentsAst]:
        p1 = self.parse_once(self.parse_token_double_dot)
        if p1 is None: return None
        p2 = self.parse_optional(self.parse_pattern_variant_single_identifier)
        return Asts.PatternVariantDestructureSkipNArgumentsAst(p1.pos, p1, p2)

    def parse_pattern_variant_single_identifier(self) -> Optional[Asts.PatternVariantSingleIdentifierAst]:
        p1 = self.parse_optional(self.parse_keyword_mut)
        p2 = self.parse_once(self.parse_identifier)
        if p2 is None: return None
        p3 = self.parse_optional(self.parse_local_variable_single_identifier_alias)
        return Asts.PatternVariantSingleIdentifierAst((p1 or p2).pos, p1, p2, p3)

    def parse_pattern_variant_destructure_tuple(self) -> Optional[Asts.PatternVariantDestructureTupleAst]:
        p1 = self.parse_once(self.parse_token_left_parenthesis)
        if p1 is None: return None
        p2 = self.parse_one_or_more(self.parse_pattern_variant_nested_for_destructure_tuple, self.parse_token_comma)
        if p2 is None: return None
        p3 = self.parse_once(self.parse_token_right_parenthesis)
        if p3 is None: return None
        return Asts.PatternVariantDestructureTupleAst(p1.pos, p1, p2, p3)

    def parse_pattern_variant_destructure_array(self) -> Optional[Asts.PatternVariantDestructureArrayAst]:
        p1 = self.parse_once(self.parse_token_left_square_bracket)
        if p1 is None: return None
        p2 = self.parse_one_or_more(self.parse_pattern_variant_nested_for_destructure_array, self.parse_token_comma)
        if p2 is None: return None
        p3 = self.parse_once(self.parse_token_right_square_bracket)
        if p3 is None: return None
        return Asts.PatternVariantDestructureArrayAst(p1.pos, p1, p2, p3)

    def parse_pattern_variant_destructure_object(self) -> Optional[Asts.PatternVariantDestructureObjectAst]:
        p1 = self.parse_once(self.parse_type)
        if p1 is None: return None
        p2 = self.parse_once(self.parse_token_left_parenthesis)
        if p2 is None: return None
        p3 = self.parse_zero_or_more(self.parse_pattern_variant_nested_for_destructure_object, self.parse_token_comma)
        p4 = self.parse_once(self.parse_token_right_parenthesis)
        if p4 is None: return None
        return Asts.PatternVariantDestructureObjectAst(p1.pos, p1, p2, p3, p4)

    def parse_pattern_variant_attribute_binding(self) -> Optional[Asts.PatternVariantAttributeBindingAst]:
        p1 = self.parse_once(self.parse_identifier)
        if p1 is None: return None
        p2 = self.parse_once(self.parse_token_assign)
        if p2 is None: return None
        p3 = self.parse_once(self.parse_pattern_variant_nested_for_attribute_binding)
        if p3 is None: return None
        return Asts.PatternVariantAttributeBindingAst(p1.pos, p1, p2, p3)

    def parse_pattern_variant_literal(self) -> Optional[Asts.PatternVariantLiteralAst]:
        p1 = self.parse_alternate([
            self.parse_literal_float,
            self.parse_literal_integer,
            self.parse_literal_string,
            self.parse_literal_boolean])
        return Asts.PatternVariantLiteralAst(p1.pos, p1)

    def parse_pattern_variant_expression(self) -> Optional[Asts.PatternVariantExpressionAst]:
        p1 = self.parse_once(self.parse_expression)
        if p1 is None: return None
        return Asts.PatternVariantExpressionAst(p1.pos, p1)

    def parse_pattern_variant_else(self) -> Optional[Asts.PatternVariantElseAst]:
        p1 = self.parse_once(self.parse_keyword_else)
        if p1 is None: return None
        return Asts.PatternVariantElseAst(p1.pos, p1)

    def parse_pattern_variant_else_case(self) -> Optional[Asts.PatternVariantElseCaseAst]:
        p1 = self.parse_once(self.parse_keyword_else)
        if p1 is None: return None
        p2 = self.parse_once(self.parse_case_expression)
        if p2 is None: return None
        return Asts.PatternVariantElseCaseAst(p1.pos, p1, p2)

    def parse_pattern_variant_nested_for_destructure_tuple(self) -> Optional[Asts.PatternVariantNestedForDestructureTupleAst]:
        p1 = self.parse_alternate([
            self.parse_pattern_variant_skip_arguments,
            self.parse_pattern_variant_skip_argument,
            self.parse_pattern_variant_destructure_array,
            self.parse_pattern_variant_destructure_tuple,
            self.parse_pattern_variant_destructure_object,
            self.parse_pattern_variant_single_identifier,
            self.parse_pattern_variant_literal])
        return p1

    def parse_pattern_variant_nested_for_destructure_array(self) -> Optional[Asts.PatternVariantNestedForDestructureArrayAst]:
        p1 = self.parse_alternate([
            self.parse_pattern_variant_skip_arguments,
            self.parse_pattern_variant_skip_argument,
            self.parse_pattern_variant_destructure_array,
            self.parse_pattern_variant_destructure_tuple,
            self.parse_pattern_variant_destructure_object,
            self.parse_pattern_variant_single_identifier,
            self.parse_pattern_variant_literal])
        return p1

    def parse_pattern_variant_nested_for_destructure_object(self) -> Optional[Asts.PatternVariantNestedForDestructureObjectAst]:
        p1 = self.parse_alternate([
            self.parse_pattern_variant_skip_arguments,
            self.parse_pattern_variant_attribute_binding,
            self.parse_pattern_variant_single_identifier])
        return p1

    def parse_pattern_variant_nested_for_attribute_binding(self) -> Optional[Asts.PatternVariantNestedForAttributeBindingAst]:
        p1 = self.parse_alternate([
            self.parse_pattern_variant_destructure_array,
            self.parse_pattern_variant_destructure_tuple,
            self.parse_pattern_variant_destructure_object,
            self.parse_pattern_variant_literal])
        return p1

    def parse_pattern_guard(self) -> Optional[Asts.PatternGuardAst]:
        p1 = self.parse_once(self.parse_keyword_and)
        if p1 is None: return None
        p2 = self.parse_once(self.parse_expression)
        if p2 is None: return None
        return Asts.PatternGuardAst(p1.pos, p1, p2)

    # ===== OPERATORS =====

    def parse_binary_op_precedence_level_1(self) -> Optional[Asts.TokenAst]:
        p1 = self.parse_once(self.parse_keyword_or)
        if p1 is None: return None
        return p1

    def parse_binary_op_precedence_level_2(self) -> Optional[Asts.TokenAst]:
        p1 = self.parse_once(self.parse_keyword_and)
        if p1 is None: return None
        return p1

    def parse_binary_op_precedence_level_3(self) -> Optional[Asts.TokenAst]:
        p1 = self.parse_once(self.parse_keyword_is)
        if p1 is None: return None
        return p1

    def parse_binary_op_precedence_level_4(self) -> Optional[Asts.TokenAst]:
        p1 = self.parse_alternate([
            self.parse_token_equals,
            self.parse_token_not_equals,
            self.parse_token_less_than_or_equals,
            self.parse_token_greater_than_or_equals,
            self.parse_token_less_than,
            self.parse_token_greater_than])
        return p1

    def parse_binary_op_precedence_level_5(self) -> Optional[Asts.TokenAst]:
        p1 = self.parse_alternate([
            self.parse_token_plus_assign,
            self.parse_token_minus_assign,
            self.parse_token_plus,
            self.parse_token_minus])
        return p1

    def parse_binary_op_precedence_level_6(self) -> Optional[Asts.TokenAst]:
        p1 = self.parse_alternate([
            self.parse_token_multiply_assign,
            self.parse_token_divide_assign,
            self.parse_token_modulo_assign,
            self.parse_token_remainder_assign,
            self.parse_token_exponent_assign,
            self.parse_token_multiply,
            self.parse_token_divide,
            self.parse_token_modulo,
            self.parse_token_remainder,
            self.parse_token_exponent])
        return p1

    def parse_boolean_comparison_op(self) -> Optional[Asts.TokenAst]:
        p1 = self.parse_alternate([
            self.parse_token_equals,
            self.parse_token_not_equals,
            self.parse_token_less_than_or_equals,
            self.parse_token_greater_than_or_equals,
            self.parse_token_less_than,
            self.parse_token_greater_than])
        return p1

    def parse_unary_op(self) -> Optional[Asts.UnaryExpressionOperatorAsyncAst]:
        p1 = self.parse_once(self.parse_unary_op_async_call)
        if p1 is not None: return p1
        return p1

    def parse_unary_op_async_call(self) -> Optional[Asts.UnaryExpressionOperatorAst]:
        p1 = self.parse_once(self.parse_keyword_async)
        if p1 is None: return None
        return Asts.UnaryExpressionOperatorAsyncAst(p1.pos, p1)

    def parse_postfix_op(self) -> Optional[Asts.PostfixExpressionOperatorAst]:
        p1 = self.parse_alternate([
            self.parse_postfix_op_resume_coroutine,
            self.parse_postfix_op_function_call,
            self.parse_postfix_op_index,
            self.parse_postfix_op_not_keyword,
            self.parse_postfix_op_member_access,
            self.parse_postfix_op_early_return])
        return p1

    def parse_postfix_op_resume_coroutine(self) -> Optional[Asts.PostfixExpressionOperatorResumeCoroutineAst]:
        p1 = self.parse_once(self.parse_token_dot)
        if p1 is None: return None
        p2 = self.parse_once(self.parse_keyword_res)
        if p2 is None: return None
        p3 = self.parse_once(self.parse_function_call_arguments)
        if p3 is None: return None
        return Asts.PostfixExpressionOperatorResumeCoroutineAst(p1.pos, p1, p2, p3)

    def parse_postfix_op_function_call(self) -> Optional[Asts.PostfixExpressionOperatorFunctionCallAst]:
        p1 = self.parse_optional(self.parse_generic_arguments)
        p2 = self.parse_once(self.parse_function_call_arguments)
        if p2 is None: return None
        p3 = self.parse_optional(self.parse_token_double_dot)
        return Asts.PostfixExpressionOperatorFunctionCallAst((p1 or p2).pos, p1, p2, p3)

    def parse_postfix_op_index(self) -> Optional[Asts.PostfixExpressionOperatorIndexAst]:
        p1 = self.parse_once(self.parse_token_left_square_bracket)
        if p1 is None: return None
        p2 = self.parse_once(self.parse_keyword_mut)
        p3 = self.parse_once(self.parse_expression)
        if not p3: return None
        p4 = self.parse_once(self.parse_token_right_square_bracket)
        if p4 is None: return None
        return Asts.PostfixExpressionOperatorIndexAst(p1.pos, p1, p2, p3, p4)

    def parse_postfix_op_member_access(self) -> Optional[Asts.PostfixExpressionOperatorMemberAccessAst]:
        p1 = self.parse_alternate([
            self.parse_postfix_op_member_access_runtime,
            self.parse_postfix_op_member_access_static])
        return p1

    def parse_postfix_op_member_access_runtime(self) -> Optional[Asts.PostfixExpressionOperatorMemberAccessAst]:
        p1 = self.parse_once(self.parse_token_dot)
        if p1 is None: return None
        p2 = self.parse_alternate([
            self.parse_identifier,
            self.parse_lexeme_dec_integer])
        if p2 is None: return None
        return Asts.PostfixExpressionOperatorMemberAccessAst(p1.pos, p1, p2)

    def parse_postfix_op_member_access_static(self) -> Optional[Asts.PostfixExpressionOperatorMemberAccessAst]:
        p1 = self.parse_once(self.parse_token_double_colon)
        if p1 is None: return None
        p2 = self.parse_once(self.parse_identifier)
        if p2 is None: return None
        return Asts.PostfixExpressionOperatorMemberAccessAst(p1.pos, p1, p2)

    def parse_postfix_op_early_return(self) -> Optional[Asts.PostfixExpressionOperatorEarlyReturnAst]:
        p1 = self.parse_once(self.parse_token_question_mark)
        if p1 is None: return None
        return Asts.PostfixExpressionOperatorEarlyReturnAst(p1.pos, p1)

    def parse_postfix_op_not_keyword(self) -> Optional[Asts.PostfixExpressionOperatorNotKeywordAst]:
        p1 = self.parse_once(self.parse_token_dot)
        if p1 is None: return None
        p2 = self.parse_once(self.parse_keyword_not)
        if p2 is None: return None
        return Asts.PostfixExpressionOperatorNotKeywordAst(p1.pos, p1, p2)

    # ===== CONVENTIONS =====

    def parse_convention(self) -> Optional[Asts.ConventionAst]:
        p1 = self.parse_alternate([
            self.parse_convention_mut,
            self.parse_convention_ref])
        return p1

    def parse_convention_ref(self) -> Optional[Asts.ConventionRefAst]:
        p1 = self.parse_once(self.parse_token_ampersand)
        if p1 is None: return None
        return Asts.ConventionRefAst(p1.pos, p1)

    def parse_convention_mut(self) -> Optional[Asts.ConventionMutAst]:
        p1 = self.parse_once(self.parse_token_ampersand)
        if p1 is None: return None
        p2 = self.parse_once(self.parse_keyword_mut)
        if p2 is None: return None
        return Asts.ConventionMutAst(p1.pos, p1, p2)

    # ===== OBJECT INITIALIZATION =====

    def parse_object_initializer(self) -> Optional[Asts.ObjectInitializerAst]:
        p1 = self.parse_once(self.parse_type_simple)
        if p1 is None: return None
        p2 = self.parse_once(self.parse_object_initializer_arguments)
        if p2 is None: return None
        return Asts.ObjectInitializerAst(p1.pos, p1, p2)

    def parse_object_initializer_arguments(self) -> Optional[Asts.ObjectInitializerArgumentGroupAst]:
        p1 = self.parse_once(self.parse_token_left_parenthesis)
        if p1 is None: return None
        p2 = self.parse_zero_or_more(self.parse_object_initializer_argument, self.parse_token_comma)
        p3 = self.parse_once(self.parse_token_right_parenthesis)
        if p3 is None: return None
        return Asts.ObjectInitializerArgumentGroupAst(p1.pos, p1, p2, p3)

    def parse_object_initializer_argument(self) -> Optional[Asts.ObjectInitializerArgumentAst]:
        p1 = self.parse_alternate([
            self.parse_object_initializer_argument_named,
            self.parse_object_initializer_argument_unnamed])
        return p1

    def parse_object_initializer_argument_unnamed(self) -> Optional[Asts.ObjectInitializerArgumentUnnamedAst]:
        p1 = self.parse_optional(self.parse_token_double_dot)
        p2 = self.parse_once(self.parse_expression)
        if p2 is None: return None
        return Asts.ObjectInitializerArgumentUnnamedAst((p1 or p2).pos, p1, p2)

    def parse_object_initializer_argument_named(self) -> Optional[Asts.ObjectInitializerArgumentNamedAst]:
        p1 = self.parse_once(self.parse_identifier)
        if p1 is None: return None
        p2 = self.parse_once(self.parse_token_assign)
        if p2 is None: return None
        p3 = self.parse_once(self.parse_expression)
        if p3 is None: return None
        return Asts.ObjectInitializerArgumentNamedAst(p1.pos, p1, p2, p3)

    # ===== LAMBDAS =====

    def parse_lambda_expression(self) -> Optional[Asts.LambdaExpressionAst]:
        p1 = self.parse_optional(self.parse_keyword_cor)
        p2 = self.parse_once(self.parse_lambda_expression_parameter_and_capture_group)
        if p2 is None: return None
        p3 = self.parse_once(self.parse_expression)
        if p3 is None: return None
        return Asts.LambdaExpressionAst((p1 or p2).pos, p1, p2, p3)

    def parse_lambda_expression_parameter_and_capture_group(self) -> Optional[Asts.LambdaExpressionParameterAndCaptureGroupAst]:
        p1 = self.parse_once(self.parse_token_vertical_bar)
        if p1 is None: return None
        p2 = self.parse_zero_or_more(self.parse_lambda_expression_parameter, self.parse_token_comma)
        p3 = self.parse_once(self.parse_lambda_expression_capture_group)
        p4 = self.parse_once(self.parse_token_vertical_bar)
        if p4 is None: return None
        return Asts.LambdaExpressionParameterAndCaptureGroupAst(p1.pos, p1, p2, p3, p4)

    def parse_lambda_expression_capture_item(self) -> Optional[Asts.LambdaExpressionCaptureItemAst]:
        p1 = self.parse_optional(self.parse_convention)
        p2 = self.parse_once(self.parse_identifier)
        if p2 is None: return None
        return Asts.LambdaExpressionCaptureItemAst((p1 or p2).pos, p1, p2)

    def parse_lambda_expression_capture_group(self) -> Seq[Asts.LambdaExpressionCaptureItemAst]:
        p1 = self.parse_once(self.parse_keyword_caps)
        if p1 is None: return []
        p2 = self.parse_zero_or_more(self.parse_lambda_expression_capture_item, self.parse_token_comma)
        return p2

    def parse_lambda_expression_parameter(self) -> Optional[Asts.LambdaExpressionParameterAst]:
        p1 = self.parse_alternate([
            self.parse_function_parameter_variadic,
            self.parse_function_parameter_optional,
            self.parse_function_parameter_required])
        return p1

    # ===== TYPES =====

    def parse_binary_type_expression_precedence_level_n_rhs(self, op, rhs) -> Optional[Tuple[Asts.TokenAst, Asts.TypeSingleAst]]:
        p1 = self.parse_once(op)
        if p1 is None: return None
        p2 = self.parse_once(rhs)
        if p2 is None: return None
        return p1, p2

    def parse_binary_type_expression_precedence_level_n(self, lhs, op, rhs) -> Optional[Asts.TypeSingleAst]:
        p1 = self.parse_once(lhs)
        if p1 is None: return None
        p2 = self.parse_optional(lambda: self.parse_binary_type_expression_precedence_level_n_rhs(op, rhs))
        if p2 is None: return p1
        return Asts.TypeBinaryExpressionAst(p1.pos, p1, p2[0], p2[1]).convert()

    def parse_type(self) -> Optional[Asts.TypeAst]:
        p1 = self.parse_alternate([
            self.parse_type_parenthesized,
            self.parse_type_array,
            self.parse_type_tuple,
            self.parse_type_binary_expression_precedence_level_1])
        return p1

    def parse_type_simple(self) -> Optional[Asts.TypeAst]:
        p1 = self.parse_zero_or_more(self.parse_type_unary_op_namespace, self.parse_nothing)
        p2 = self.parse_once(self.parse_type_single)
        if p2 is None: return None
        return reduce(lambda acc, x: Asts.TypeUnaryExpressionAst(x.pos, x, acc), p1[::-1], p2)

    def parse_type_binary_expression_precedence_level_1(self) -> Optional[Asts.TypeAst]:
        return self.parse_binary_type_expression_precedence_level_n(self.parse_type_binary_expression_precedence_level_2, self.parse_type_binary_op_precedence_level_1, self.parse_type_binary_expression_precedence_level_1)

    def parse_type_binary_expression_precedence_level_2(self) -> Optional[Asts.TypeAst]:
        return self.parse_binary_type_expression_precedence_level_n(self.parse_type_postfix_expression, self.parse_type_binary_op_precedence_level_2, self.parse_type_binary_expression_precedence_level_2)

    def parse_type_binary_op_precedence_level_1(self) -> Optional[Asts.TokenAst]:
        p1 = self.parse_once(self.parse_keyword_and)
        if p1 is None: return None
        return p1

    def parse_type_binary_op_precedence_level_2(self) -> Optional[Asts.TokenAst]:
        p1 = self.parse_once(self.parse_keyword_or)
        if p1 is None: return None
        return p1

    def parse_type_postfix_expression(self) -> Optional[Asts.TypeAst]:
        p1 = self.parse_once(self.parse_type_unary_expression)
        if p1 is None: return None
        p2 = self.parse_zero_or_more(self.parse_type_postfix_op, self.parse_nothing)
        return reduce(lambda acc, x: Asts.TypePostfixExpressionAst(acc.pos, acc, x), p2, p1).convert()

    def parse_type_unary_expression(self) -> Optional[Asts.TypeAst]:
        # Todo: this doesn't allow for &[T, n], has to be &std::Arr[T, n] atm.
        p1 = self.parse_optional(self.parse_type_unary_op_borrow)
        p2 = self.parse_zero_or_more(self.parse_type_unary_op_namespace, self.parse_nothing)
        p3 = self.parse_once(self.parse_type_single)
        if p3 is None: return None
        p2.insert(0, p1) if p1 else None
        return reduce(lambda acc, x: Asts.TypeUnaryExpressionAst(x.pos, x, acc), p2[::-1], p3).convert()

    def parse_type_parenthesized(self) -> Optional[Asts.TypeSingleAst]:
        p1 = self.parse_once(self.parse_token_left_parenthesis)
        if p1 is None: return None
        p2 = self.parse_once(self.parse_type)
        if p2 is None: return None
        p3 = self.parse_once(self.parse_token_right_parenthesis)
        if p3 is None: return None
        return Asts.TypeParenthesizedAst(p1.pos, p1, p2, p3).convert()

    def parse_type_tuple(self) -> Optional[Asts.TypeSingleAst]:
        p1 = self.parse_alternate([
            self.parse_type_tuple_0_items,
            self.parse_type_tuple_1_items,
            self.parse_type_tuple_n_items])
        return p1

    def parse_type_array(self) -> Optional[Asts.TypeSingleAst]:
        p1 = self.parse_once(self.parse_token_left_square_bracket)
        if p1 is None: return None
        p2 = self.parse_once(self.parse_type)
        if p2 is None: return None
        p3 = self.parse_once(self.parse_token_comma)
        if p3 is None: return None
        p4 = self.parse_once(self.parse_lexeme_dec_integer)
        if p4 is None: return None
        p5 = self.parse_once(self.parse_token_right_square_bracket)
        if p5 is None: return None
        return Asts.TypeArrayAst(p1.pos, p1, p2, p3, p4, p5).convert()

    def parse_type_single(self) -> Optional[Asts.TypeSingleAst]:
        p1 = self.parse_alternate([
            self.parse_generic_identifier,
            self.parse_type_self])
        if p1 is None: return None
        return Asts.TypeSingleAst(p1.pos, p1)

    def parse_type_self(self) -> Optional[Asts.GenericIdentifierAst]:
        p1 = self.parse_once(self.parse_keyword_self_type)
        if p1 is None: return None
        return Asts.GenericIdentifierAst(p1.pos, p1.token_data, Asts.GenericArgumentGroupAst(pos=p1.pos))

    def parse_type_unary_op(self) -> Optional[Asts.TypeUnaryOperatorAst]:
        p1 = self.parse_alternate([
            self.parse_type_unary_op_namespace,
            self.parse_type_unary_op_borrow])
        return p1

    def parse_type_unary_op_namespace(self) -> Optional[Asts.TypeUnaryOperatorNamespaceAst]:
        p1 = self.parse_once(self.parse_identifier)
        if p1 is None: return None
        p2 = self.parse_once(self.parse_token_double_colon)
        if p2 is None: return None
        return Asts.TypeUnaryOperatorNamespaceAst(p1.pos, p1, p2)

    def parse_type_unary_op_borrow(self) -> Optional[Asts.TypeUnaryOperatorBorrowAst]:
        p1 = self.parse_once(self.parse_convention)
        if p1 is None: return None
        return Asts.TypeUnaryOperatorBorrowAst(p1.pos, p1)

    def parse_type_postfix_op(self) -> Optional[Asts.TypePostfixOperatorAst]:
        p1 = self.parse_alternate([
            self.parse_type_postfix_op_nested_type,
            self.parse_type_postfix_op_optional_type])
        return p1

    def parse_type_postfix_op_nested_type(self) -> Optional[Asts.TypePostfixOperatorNestedTypeAst]:
        p1 = self.parse_once(self.parse_token_double_colon)
        if p1 is None: return None
        p2 = self.parse_once(self.parse_type_single)
        if p2 is None: return None
        return Asts.TypePostfixOperatorNestedTypeAst(p1.pos, p1, p2)

    def parse_type_postfix_op_optional_type(self) -> Optional[Asts.TypePostfixOperatorOptionalTypeAst]:
        p1 = self.parse_once(self.parse_token_question_mark)
        if p1 is None: return None
        return Asts.TypePostfixOperatorOptionalTypeAst(p1.pos, p1)

    def parse_type_tuple_0_items(self) -> Optional[Asts.TypeSingleAst]:
        p1 = self.parse_once(self.parse_token_left_parenthesis)
        if p1 is None: return None
        p2 = self.parse_once(self.parse_token_right_parenthesis)
        if p2 is None: return None
        return Asts.TypeTupleAst(p1.pos, p1, [], p2).convert()

    def parse_type_tuple_1_items(self) -> Optional[Asts.TypeSingleAst]:
        p1 = self.parse_once(self.parse_token_left_parenthesis)
        if p1 is None: return None
        p2 = self.parse_once(self.parse_type)
        if p2 is None: return None
        p3 = self.parse_once(self.parse_token_comma)
        if p3 is None: return None
        p4 = self.parse_once(self.parse_token_right_parenthesis)
        if p4 is None: return None
        return Asts.TypeTupleAst(p1.pos, p1, [p2], p4).convert()

    def parse_type_tuple_n_items(self) -> Optional[Asts.TypeSingleAst]:
        p1 = self.parse_once(self.parse_token_left_parenthesis)
        if p1 is None: return None
        p2 = self.parse_two_or_more(self.parse_type, self.parse_token_comma)
        if p2 is None: return None
        p3 = self.parse_once(self.parse_token_right_parenthesis)
        if p3 is None: return None
        return Asts.TypeTupleAst(p1.pos, p1, p2, p3).convert()

    # ===== IDENTIFIERS =====

    def parse_identifier(self) -> Optional[Asts.IdentifierAst]:
        p1 = self.parse_once(self.parse_lexeme_identifier)
        if p1 is None: return None
        return Asts.IdentifierAst(p1.pos, p1.token_data)

    def parse_upper_identifier(self) -> Optional[Asts.IdentifierAst]:
        p1 = self.parse_once(self.parse_lexeme_upper_identifier)
        if p1 is None: return None
        return Asts.IdentifierAst(p1.pos, p1.token_data)

    def parse_generic_identifier(self) -> Optional[Asts.GenericIdentifierAst]:
        p1 = self.parse_once(self.parse_upper_identifier)
        if p1 is None: return None
        p2 = self.parse_optional(self.parse_generic_arguments)
        return Asts.GenericIdentifierAst(p1.pos, p1.value, p2)

    # ===== LITERALS =====

    def parse_literal(self) -> Optional[Asts.LiteralAst]:
        p1 = self.parse_alternate([
            self.parse_literal_float,
            self.parse_literal_integer,
            self.parse_literal_string,
            lambda: self.parse_literal_tuple(self.parse_expression),
            lambda: self.parse_literal_array(self.parse_expression),
            self.parse_literal_boolean])
        return p1

    def parse_literal_float(self) -> Optional[Asts.FloatLiteralAst]:
        p1 = self.parse_once(self.parse_literal_float_b10)
        if p1 is None: return None
        return p1

    def parse_literal_integer(self) -> Optional[Asts.IntegerLiteralAst]:
        p1 = self.parse_alternate([
            self.parse_literal_integer_b10,
            self.parse_literal_integer_b02,
            self.parse_literal_integer_b16])
        return p1

    def parse_literal_string(self) -> Optional[Asts.StringLiteralAst]:
        p1 = self.parse_once(self.parse_lexeme_double_quote_string)
        if p1 is None: return None
        return Asts.StringLiteralAst(p1.pos, p1)

    def parse_literal_tuple(self, item=None) -> Optional[Asts.TupleLiteralAst]:
        p1 = self.parse_alternate([
            lambda : self.parse_literal_tuple_1_items(item or self.parse_expression),
            lambda : self.parse_literal_tuple_n_items(item or self.parse_expression)])
        return p1

    def parse_literal_array(self, item) -> Optional[Asts.ArrayLiteralAst]:
        p1 = self.parse_alternate([
            self.parse_literal_array_0_items,
            lambda : self.parse_literal_array_n_items(item)])
        return p1

    def parse_literal_boolean(self) -> Optional[Asts.BooleanLiteralAst]:
        p1 = self.parse_alternate([
            self.parse_keyword_true,
            self.parse_keyword_false])
        if p1 is None: return None
        return Asts.BooleanLiteralAst(p1.pos, p1)

    # ===== NUMBERS =====

    def parse_literal_float_b10(self) -> Optional[Asts.FloatLiteralAst]:
        p1 = self.parse_optional(self.parse_numeric_prefix_op)
        p2 = self.parse_once(self.parse_lexeme_dec_integer)
        if p2 is None: return None
        p3 = self.parse_once(self.parse_token_dot)
        if p3 is None: return None
        p4 = self.parse_once(self.parse_lexeme_dec_integer)
        if p4 is None: return None
        p5 = self.parse_optional(self.parse_float_postfix_type)
        return Asts.FloatLiteralAst((p1 or p2).pos, p1, p2, p3, p4, p5)

    def parse_literal_integer_b10(self) -> Optional[Asts.IntegerLiteralAst]:
        p1 = self.parse_optional(self.parse_numeric_prefix_op)
        p2 = self.parse_once(self.parse_lexeme_dec_integer)
        if p2 is None: return None
        p3 = self.parse_optional(self.parse_integer_postfix_type)
        return Asts.IntegerLiteralAst((p1 or p2).pos, p1, p2, p3)

    def parse_literal_integer_b02(self) -> Optional[Asts.IntegerLiteralAst]:
        p1 = self.parse_optional(self.parse_numeric_prefix_op)
        p2 = self.parse_once(self.parse_lexeme_bin_integer)
        if p2 is None: return None
        p3 = self.parse_optional(self.parse_integer_postfix_type)
        return Asts.IntegerLiteralAst((p1 or p2).pos, p1, p2, p3)

    def parse_literal_integer_b16(self) -> Optional[Asts.IntegerLiteralAst]:
        p1 = self.parse_optional(self.parse_numeric_prefix_op)
        p2 = self.parse_once(self.parse_lexeme_hex_integer)
        if p2 is None: return None
        p3 = self.parse_optional(self.parse_integer_postfix_type)
        return Asts.IntegerLiteralAst((p1 or p2).pos, p1, p2, p3)

    def parse_numeric_prefix_op(self) -> Optional[Asts.TokenAst]:
        p1 = self.parse_alternate([
            self.parse_token_minus,
            self.parse_token_plus])
        return p1

    def parse_integer_postfix_type(self) -> Optional[Asts.TypeAst]:
        p1 = self.parse_once(self.parse_token_underscore)
        if p1 is None: return None
        p2 = self.parse_alternate([
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
            lambda: self.parse_characters("u256"),
            lambda: self.parse_characters("uz")])
        if p2 is None: return None
        return Asts.TypeSingleAst.from_token(p2)

    def parse_float_postfix_type(self) -> Optional[Asts.TypeAst]:
        p1 = self.parse_once(self.parse_token_underscore)
        if p1 is None: return None
        p2 = self.parse_alternate([
            lambda: self.parse_characters("f8"),
            lambda: self.parse_characters("f16"),
            lambda: self.parse_characters("f32"),
            lambda: self.parse_characters("f64"),
            lambda: self.parse_characters("f128"),
            lambda: self.parse_characters("f256")])
        if p2 is None: return None
        return Asts.TypeSingleAst.from_token(p2)

    # ===== TUPLES =====

    def parse_literal_tuple_1_items(self, item) -> Optional[Asts.TupleLiteralAst]:
        p1 = self.parse_once(self.parse_token_left_parenthesis)
        if p1 is None: return None
        p2 = self.parse_once(item)
        if p2 is None: return None
        p3 = self.parse_once(self.parse_token_comma)
        if p3 is None: return None
        p4 = self.parse_once(self.parse_token_right_parenthesis)
        if p4 is None: return None
        return Asts.TupleLiteralAst(p1.pos, p1, [p2], p4)

    def parse_literal_tuple_n_items(self, item) -> Optional[Asts.TupleLiteralAst]:
        p1 = self.parse_once(self.parse_token_left_parenthesis)
        if p1 is None: return None
        p2 = self.parse_two_or_more(item, self.parse_token_comma)
        if p2 is None: return None
        p3 = self.parse_once(self.parse_token_right_parenthesis)
        if p3 is None: return None
        return Asts.TupleLiteralAst(p1.pos, p1, p2, p3)

    # ===== ARRAYS =====

    def parse_literal_array_0_items(self) -> Optional[Asts.ArrayLiteral0ElementAst]:
        p1 = self.parse_once(self.parse_token_left_square_bracket)
        if p1 is None: return None
        p2 = self.parse_once(self.parse_type)
        if p2 is None: return None
        p3 = self.parse_once(self.parse_token_comma)
        if p3 is None: return None
        p4 = self.parse_once(self.parse_lexeme_dec_integer)
        if p4 is None: return None
        p5 = self.parse_once(self.parse_token_right_square_bracket)
        if p5 is None: return None
        return Asts.ArrayLiteral0ElementAst(p1.pos, p1, p2, p3, p4, p5)

    def parse_literal_array_n_items(self, item) -> Optional[Asts.ArrayLiteralNElementAst]:
        p1 = self.parse_once(self.parse_token_left_square_bracket)
        if p1 is None: return None
        p2 = self.parse_one_or_more(item, self.parse_token_comma)
        if p2 is None: return None
        p3 = self.parse_once(self.parse_token_right_square_bracket)
        if p3 is None: return None
        return Asts.ArrayLiteralNElementAst(p1.pos, p1, p2, p3)

    # ===== GLOBAL CONSTANTS =====

    def parse_cmp_value(self) -> Optional[Asts.ExpressionAst]:
        p1 = self.parse_alternate([
            self.parse_literal_float,
            self.parse_literal_integer,
            self.parse_literal_string,
            lambda: self.parse_literal_tuple(self.parse_cmp_value),
            lambda: self.parse_literal_array(self.parse_cmp_value),
            self.parse_literal_boolean,
            self.parse_cmp_object_initializer,
            self.parse_identifier])
        return p1

    def parse_cmp_object_initializer(self) -> Optional[Asts.ObjectInitializerAst]:
        p1 = self.parse_once(self.parse_type_simple)
        if p1 is None: return None
        p2 = self.parse_once(self.parse_cmp_object_initializer_arguments)
        if p2 is None: return None
        return Asts.ObjectInitializerAst(p1.pos, p1, p2)

    def parse_cmp_object_initializer_arguments(self) -> Optional[Asts.ObjectInitializerArgumentGroupAst]:
        p1 = self.parse_once(self.parse_token_left_parenthesis)
        if p1 is None: return None
        p2 = self.parse_zero_or_more(self.parse_cmp_object_initializer_argument_named, self.parse_token_comma)
        p3 = self.parse_once(self.parse_token_right_parenthesis)
        if p3 is None: return None
        return Asts.ObjectInitializerArgumentGroupAst(p1.pos, p1, p2, p3)

    def parse_cmp_object_initializer_argument_named(self) -> Optional[Asts.ObjectInitializerArgumentNamedAst]:
        p1 = self.parse_once(self.parse_identifier)
        if p1 is None: return None
        p2 = self.parse_once(self.parse_token_assign)
        if p2 is None: return None
        p3 = self.parse_once(self.parse_cmp_value)
        if p3 is None: return None
        return Asts.ObjectInitializerArgumentNamedAst(p1.pos, p1, p2, p3)

    # ===== TOKENS =====

    def parse_nothing(self) -> Optional[Asts.TokenAst]:
        return self.parse_token_raw(RawTokenType.NoToken, SppTokenType.NoToken)

    def parse_newline(self) -> Optional[Asts.TokenAst]:
        return self.parse_token_raw(RawTokenType.TkNewLine, SppTokenType.TkNewLine)

    def parse_token_left_curly_brace(self) -> Optional[Asts.TokenAst]:
        return self.parse_token_raw(RawTokenType.TkLeftCurlyBrace, SppTokenType.TkLeftCurlyBrace)

    def parse_token_right_curly_brace(self) -> Optional[Asts.TokenAst]:
        return self.parse_token_raw(RawTokenType.TkRightCurlyBrace, SppTokenType.TkRightCurlyBrace)

    def parse_token_colon(self) -> Optional[Asts.TokenAst]:
        return self.parse_token_raw(RawTokenType.TkColon, SppTokenType.TkColon)

    def parse_token_left_parenthesis(self) -> Optional[Asts.TokenAst]:
        return self.parse_token_raw(RawTokenType.TkLeftParenthesis, SppTokenType.TkLeftParenthesis)

    def parse_token_right_parenthesis(self) -> Optional[Asts.TokenAst]:
        return self.parse_token_raw(RawTokenType.TkRightParenthesis, SppTokenType.TkRightParenthesis)

    def parse_token_comma(self) -> Optional[Asts.TokenAst]:
        return self.parse_token_raw(RawTokenType.TkComma, SppTokenType.TkComma)

    def parse_token_assign(self) -> Optional[Asts.TokenAst]:
        return self.parse_token_raw(RawTokenType.TkEqualsSign, SppTokenType.TkAssign)

    def parse_token_left_square_bracket(self) -> Optional[Asts.TokenAst]:
        return self.parse_token_raw(RawTokenType.TkLeftSquareBracket, SppTokenType.TkLeftSquareBracket)

    def parse_token_right_square_bracket(self) -> Optional[Asts.TokenAst]:
        return self.parse_token_raw(RawTokenType.TkRightSquareBracket, SppTokenType.TkRightSquareBracket)

    def parse_token_at(self) -> Optional[Asts.TokenAst]:
        return self.parse_token_raw(RawTokenType.TkAt, SppTokenType.TkAt)

    def parse_token_underscore(self) -> Optional[Asts.TokenAst]:
        return self.parse_token_raw(RawTokenType.TkUnderscore, SppTokenType.TkUnderscore)

    def parse_token_less_than(self) -> Optional[Asts.TokenAst]:
        return self.parse_token_raw(RawTokenType.TkLessThanSign, SppTokenType.TkLt)

    def parse_token_greater_than(self) -> Optional[Asts.TokenAst]:
        return self.parse_token_raw(RawTokenType.TkGreaterThanSign, SppTokenType.TkGt)

    def parse_token_plus(self) -> Optional[Asts.TokenAst]:
        return self.parse_token_raw(RawTokenType.TkPlusSign, SppTokenType.TkPlus)

    def parse_token_minus(self) -> Optional[Asts.TokenAst]:
        return self.parse_token_raw(RawTokenType.TkMinusSign, SppTokenType.TkMinus)

    def parse_token_multiply(self) -> Optional[Asts.TokenAst]:
        return self.parse_token_raw(RawTokenType.TkAsterisk, SppTokenType.TkMultiply)

    def parse_token_divide(self) -> Optional[Asts.TokenAst]:
        return self.parse_token_raw(RawTokenType.TkForwardSlash, SppTokenType.TkDivide)

    def parse_token_remainder(self) -> Optional[Asts.TokenAst]:
        return self.parse_token_raw(RawTokenType.TkPercentSign, SppTokenType.TkRemainder)

    def parse_token_dot(self) -> Optional[Asts.TokenAst]:
        return self.parse_token_raw(RawTokenType.TkDot, SppTokenType.TkDot)

    def parse_token_question_mark(self) -> Optional[Asts.TokenAst]:
        return self.parse_token_raw(RawTokenType.TkQuestionMark, SppTokenType.TkQuestionMark)

    def parse_token_ampersand(self) -> Optional[Asts.TokenAst]:
        return self.parse_token_raw(RawTokenType.TkAmpersand, SppTokenType.TkAmpersand)

    def parse_token_vertical_bar(self) -> Optional[Asts.TokenAst]:
        return self.parse_token_raw(RawTokenType.TkVerticalBar, SppTokenType.TkVerticalBar)

    def parse_token_quote(self) -> Optional[Asts.TokenAst]:
        return self.parse_token_raw(RawTokenType.TkSpeechMark, SppTokenType.TkSpeechMark)

    def parse_token_dollar(self) -> Optional[Asts.TokenAst]:
        return self.parse_token_raw(RawTokenType.TkDollar, SppTokenType.TkDollar)

    def parse_token_arrow_right(self) -> Optional[Asts.TokenAst]:
        p1 = self.parse_token_raw(RawTokenType.TkMinusSign, SppTokenType.TkArrowR)
        if p1 is None: return None
        p2 = self.parse_token_raw(RawTokenType.TkGreaterThanSign, SppTokenType.TkArrowR)
        if p2 is None: return None
        p2.pos = p1.pos
        return p2

    def parse_token_double_dot(self) -> Optional[Asts.TokenAst]:
        p1 = self.parse_token_raw(RawTokenType.TkDot, SppTokenType.TkDoubleDot)
        if p1 is None: return None
        p2 = self.parse_token_raw(RawTokenType.TkDot, SppTokenType.TkDoubleDot)
        if p2 is None: return None
        p2.pos = p1.pos
        return p2

    def parse_token_equals(self) -> Optional[Asts.TokenAst]:
        p1 = self.parse_token_raw(RawTokenType.TkEqualsSign, SppTokenType.TkEq)
        if p1 is None: return None
        p2 = self.parse_token_raw(RawTokenType.TkEqualsSign, SppTokenType.TkEq)
        if p2 is None: return None
        p2.pos = p1.pos
        return p2

    def parse_token_not_equals(self) -> Optional[Asts.TokenAst]:
        p1 = self.parse_token_raw(RawTokenType.TkExclamationMark, SppTokenType.TkNe)
        if p1 is None: return None
        p2 = self.parse_token_raw(RawTokenType.TkEqualsSign, SppTokenType.TkNe)
        if p2 is None: return None
        p2.pos = p1.pos
        return p2

    def parse_token_less_than_or_equals(self) -> Optional[Asts.TokenAst]:
        p1 = self.parse_token_raw(RawTokenType.TkLessThanSign, SppTokenType.TkLe)
        if p1 is None: return None
        p2 = self.parse_token_raw(RawTokenType.TkEqualsSign, SppTokenType.TkLe)
        if p2 is None: return None
        p2.pos = p1.pos
        return p2

    def parse_token_plus_assign(self) -> Optional[Asts.TokenAst]:
        p1 = self.parse_token_raw(RawTokenType.TkPlusSign, SppTokenType.TkPlusAssign)
        if p1 is None: return None
        p2 = self.parse_token_raw(RawTokenType.TkEqualsSign, SppTokenType.TkPlusAssign)
        if p2 is None: return None
        p2.pos = p1.pos
        return p2

    def parse_token_minus_assign(self) -> Optional[Asts.TokenAst]:
        p1 = self.parse_token_raw(RawTokenType.TkMinusSign, SppTokenType.TkMinusAssign)
        if p1 is None: return None
        p2 = self.parse_token_raw(RawTokenType.TkEqualsSign, SppTokenType.TkMinusAssign)
        if p2 is None: return None
        p2.pos = p1.pos
        return p2

    def parse_token_multiply_assign(self) -> Optional[Asts.TokenAst]:
        p1 = self.parse_token_raw(RawTokenType.TkAsterisk, SppTokenType.TkMultiplyAssign)
        if p1 is None: return None
        p2 = self.parse_token_raw(RawTokenType.TkEqualsSign, SppTokenType.TkMultiplyAssign)
        if p2 is None: return None
        p2.pos = p1.pos
        return p2

    def parse_token_divide_assign(self) -> Optional[Asts.TokenAst]:
        p1 = self.parse_token_raw(RawTokenType.TkForwardSlash, SppTokenType.TkDivideAssign)
        if p1 is None: return None
        p2 = self.parse_token_raw(RawTokenType.TkEqualsSign, SppTokenType.TkDivideAssign)
        if p2 is None: return None
        p2.pos = p1.pos
        return p2

    def parse_token_remainder_assign(self) -> Optional[Asts.TokenAst]:
        p1 = self.parse_token_raw(RawTokenType.TkPercentSign, SppTokenType.TkRemainderAssign)
        if p1 is None: return None
        p3 = self.parse_token_raw(RawTokenType.TkEqualsSign, SppTokenType.TkRemainderAssign)
        if p3 is None: return None
        p3.pos = p1.pos
        return p3

    def parse_token_greater_than_or_equals(self) -> Optional[Asts.TokenAst]:
        p1 = self.parse_token_raw(RawTokenType.TkGreaterThanSign, SppTokenType.TkGe)
        if p1 is None: return None
        p2 = self.parse_token_raw(RawTokenType.TkEqualsSign, SppTokenType.TkGe)
        if p2 is None: return None
        p2.pos = p1.pos
        return p2

    def parse_token_modulo(self) -> Optional[Asts.TokenAst]:
        p1 = self.parse_token_raw(RawTokenType.TkPercentSign, SppTokenType.TkModulo)
        if p1 is None: return None
        p2 = self.parse_token_raw(RawTokenType.TkPercentSign, SppTokenType.TkModulo)
        if p2 is None: return None
        p2.pos = p1.pos
        return p2

    def parse_token_exponent(self) -> Optional[Asts.TokenAst]:
        p1 = self.parse_token_raw(RawTokenType.TkAsterisk, SppTokenType.TkExponent)
        if p1 is None: return None
        p2 = self.parse_token_raw(RawTokenType.TkAsterisk, SppTokenType.TkExponent)
        if p2 is None: return None
        p2.pos = p1.pos
        return p2

    def parse_token_double_colon(self) -> Optional[Asts.TokenAst]:
        p1 = self.parse_token_raw(RawTokenType.TkColon, SppTokenType.TkDoubleColon)
        if p1 is None: return None
        p2 = self.parse_token_raw(RawTokenType.TkColon, SppTokenType.TkDoubleColon)
        if p2 is None: return None
        p2.pos = p1.pos
        return p2

    def parse_token_modulo_assign(self) -> Optional[Asts.TokenAst]:
        p1 = self.parse_token_raw(RawTokenType.TkPercentSign, SppTokenType.TkModuloAssign)
        if p1 is None: return None
        p2 = self.parse_token_raw(RawTokenType.TkPercentSign, SppTokenType.TkModuloAssign)
        if p2 is None: return None
        p3 = self.parse_token_raw(RawTokenType.TkEqualsSign, SppTokenType.TkModuloAssign)
        if p3 is None: return None
        p3.pos = p1.pos
        return p3

    def parse_token_exponent_assign(self) -> Optional[Asts.TokenAst]:
        p1 = self.parse_token_raw(RawTokenType.TkAsterisk, SppTokenType.TkExponentAssign)
        if p1 is None: return None
        p2 = self.parse_token_raw(RawTokenType.TkAsterisk, SppTokenType.TkExponentAssign)
        if p2 is None: return None
        p3 = self.parse_token_raw(RawTokenType.TkEqualsSign, SppTokenType.TkExponentAssign)
        if p3 is None: return None
        p3.pos = p1.pos
        return p3

    # ===== KEYWORDS =====

    def parse_keyword_cls(self) -> Optional[Asts.TokenAst]:
        return self.parse_keyword_raw(RawKeywordType.Cls, SppTokenType.KwCls, True)

    def parse_keyword_sup(self) -> Optional[Asts.TokenAst]:
        return self.parse_keyword_raw(RawKeywordType.Sup, SppTokenType.KwSup, True)

    def parse_keyword_ext(self) -> Optional[Asts.TokenAst]:
        return self.parse_keyword_raw(RawKeywordType.Ext, SppTokenType.KwExt, True)

    def parse_keyword_fun(self) -> Optional[Asts.TokenAst]:
        return self.parse_keyword_raw(RawKeywordType.Fun, SppTokenType.KwFun, True)

    def parse_keyword_cor(self) -> Optional[Asts.TokenAst]:
        return self.parse_keyword_raw(RawKeywordType.Cor, SppTokenType.KwCor, True)

    def parse_keyword_mut(self) -> Optional[Asts.TokenAst]:
        return self.parse_keyword_raw(RawKeywordType.Mut, SppTokenType.KwMut, True)

    def parse_keyword_cmp(self) -> Optional[Asts.TokenAst]:
        return self.parse_keyword_raw(RawKeywordType.Cmp, SppTokenType.KwCmp, True)

    def parse_keyword_where(self) -> Optional[Asts.TokenAst]:
        return self.parse_keyword_raw(RawKeywordType.Where, SppTokenType.KwWhere, True)

    def parse_keyword_self_value(self) -> Optional[Asts.TokenAst]:
        return self.parse_keyword_raw(RawKeywordType.SelfVal, SppTokenType.KwSelfVal, False)

    def parse_keyword_self_type(self) -> Optional[Asts.TokenAst]:
        return self.parse_keyword_raw(RawKeywordType.SelfType, SppTokenType.KwSelfType, False)

    def parse_keyword_case(self) -> Optional[Asts.TokenAst]:
        return self.parse_keyword_raw(RawKeywordType.Case, SppTokenType.KwCase, True)

    def parse_keyword_of(self) -> Optional[Asts.TokenAst]:
        return self.parse_keyword_raw(RawKeywordType.Of, SppTokenType.KwOf, False)  # space ? (\n)

    def parse_keyword_loop(self) -> Optional[Asts.TokenAst]:
        return self.parse_keyword_raw(RawKeywordType.Loop, SppTokenType.KwLoop, True)

    def parse_keyword_in(self) -> Optional[Asts.TokenAst]:
        return self.parse_keyword_raw(RawKeywordType.In, SppTokenType.KwIn, True)

    def parse_keyword_else(self) -> Optional[Asts.TokenAst]:
        return self.parse_keyword_raw(RawKeywordType.Else, SppTokenType.KwElse, True)

    def parse_keyword_gen(self) -> Optional[Asts.TokenAst]:
        return self.parse_keyword_raw(RawKeywordType.Gen, SppTokenType.KwGen, True)

    def parse_keyword_with(self) -> Optional[Asts.TokenAst]:
        return self.parse_keyword_raw(RawKeywordType.With, SppTokenType.KwWith, True)

    def parse_keyword_ret(self) -> Optional[Asts.TokenAst]:
        return self.parse_keyword_raw(RawKeywordType.Ret, SppTokenType.KwRet, False)  # =True, unless newline?

    def parse_keyword_exit(self) -> Optional[Asts.TokenAst]:
        return self.parse_keyword_raw(RawKeywordType.Exit, SppTokenType.KwExit, False)

    def parse_keyword_skip(self) -> Optional[Asts.TokenAst]:
        return self.parse_keyword_raw(RawKeywordType.Skip, SppTokenType.KwSkip, False)

    def parse_keyword_use(self) -> Optional[Asts.TokenAst]:
        return self.parse_keyword_raw(RawKeywordType.Use, SppTokenType.KwUse, True)

    def parse_keyword_let(self) -> Optional[Asts.TokenAst]:
        return self.parse_keyword_raw(RawKeywordType.Let, SppTokenType.KwLet, True)

    def parse_keyword_as(self) -> Optional[Asts.TokenAst]:
        return self.parse_keyword_raw(RawKeywordType.As, SppTokenType.KwAs, True)

    def parse_keyword_is(self) -> Optional[Asts.TokenAst]:
        return self.parse_keyword_raw(RawKeywordType.Is, SppTokenType.KwIs, True)

    def parse_keyword_and(self) -> Optional[Asts.TokenAst]:
        return self.parse_keyword_raw(RawKeywordType.And, SppTokenType.KwAnd, True)

    def parse_keyword_or(self) -> Optional[Asts.TokenAst]:
        return self.parse_keyword_raw(RawKeywordType.Or, SppTokenType.KwOr, True)

    def parse_keyword_async(self) -> Optional[Asts.TokenAst]:
        return self.parse_keyword_raw(RawKeywordType.Async, SppTokenType.KwAsync, True)

    def parse_keyword_not(self) -> Optional[Asts.TokenAst]:
        return self.parse_keyword_raw(RawKeywordType.Not, SppTokenType.KwNot, False)

    def parse_keyword_true(self) -> Optional[Asts.TokenAst]:
        return self.parse_keyword_raw(RawKeywordType.True_, SppTokenType.KwTrue, False)

    def parse_keyword_false(self) -> Optional[Asts.TokenAst]:
        return self.parse_keyword_raw(RawKeywordType.False_, SppTokenType.KwFalse, False)

    def parse_keyword_res(self) -> Optional[Asts.TokenAst]:
        return self.parse_keyword_raw(RawKeywordType.Res, SppTokenType.KwRes, False)

    def parse_keyword_caps(self) -> Optional[Asts.TokenAst]:
        return self.parse_keyword_raw(RawKeywordType.Caps, SppTokenType.KwCaps, True)

    # ===== LEXEMES =====

    def parse_lexeme_character(self) -> Optional[Asts.TokenAst]:
        return self.parse_token_raw(RawTokenType.TkCharacter, SppTokenType.LxNumber)

    def parse_lexeme_digit(self) -> Optional[Asts.TokenAst]:
        return self.parse_token_raw(RawTokenType.TkDigit, SppTokenType.LxNumber)

    def parse_lexeme_character_or_digit(self) -> Optional[Asts.TokenAst]:
        return self.parse_alternate([self.parse_lexeme_character, self.parse_lexeme_digit])

    def parse_lexeme_character_or_digit_or_underscore(self) -> Optional[Asts.TokenAst]:
        return self.parse_alternate([self.parse_lexeme_character, self.parse_lexeme_digit, self.parse_token_underscore])

    def parse_lexeme_dec_integer(self) -> Optional[Asts.TokenAst]:
        self.parse_nothing()
        out = Asts.TokenAst(self.current_pos(), SppTokenType.LxNumber, "")

        p1 = self.parse_once(self.parse_lexeme_digit)
        if p1 is None:
            self.store_error(self.current_pos(), "Invalid binary integer literal")
            return None
        out.token_data += p1.token_data

        while self._token_types[self._pos] == RawTokenType.TkDigit:
            p2 = self.parse_once(self.parse_lexeme_digit)
            out.token_data += p2.token_data

        return out

    def parse_lexeme_bin_integer(self) -> Optional[Asts.TokenAst]:
        self.parse_nothing()
        out = Asts.TokenAst(self.current_pos(), SppTokenType.LxNumber, "")

        p1 = self.parse_once(self.parse_lexeme_digit)
        if p1 is None or p1.token_data != "0":
            self.store_error(self.current_pos(), "Invalid binary integer literal")
            return None
        out.token_data += p1.token_data

        p2 = self.parse_once(self.parse_lexeme_character)
        if p2 is None or p2.token_data != "b":
            self.store_error(self.current_pos(), "Invalid binary integer literal")
            return None
        out.token_data += p2.token_data

        p3 = self.parse_once(self.parse_lexeme_digit)
        if p3 is None or p3.token_data not in "01":
            self.store_error(self.current_pos(), "Invalid binary integer literal")
            return None
        out.token_data += p3.token_data

        while self._token_types[self._pos] == RawTokenType.TkDigit:
            p3 = self.parse_once(self.parse_lexeme_digit)
            if p3 is None or p3.token_data not in "01":
                self.store_error(self.current_pos(), "Invalid binary integer literal")
                return out
            out.token_data += p3.token_data

        return out

    def parse_lexeme_hex_integer(self) -> Optional[Asts.TokenAst]:
        self.parse_nothing()
        out = Asts.TokenAst(self.current_pos(), SppTokenType.LxNumber, "")

        p1 = self.parse_once(self.parse_lexeme_digit)
        if p1 is None or p1.token_data != "0":
            self.store_error(self.current_pos(), "Invalid hexadecimal integer literal")
            return None
        out.token_data += p1.token_data

        p2 = self.parse_once(self.parse_lexeme_character)
        if p2 is None or p2.token_data not in "x":
            self.store_error(self.current_pos(), "Invalid hexadecimal integer literal")
            return None
        out.token_data += p2.token_data

        p3 = self.parse_once(self.parse_lexeme_character)
        if p3 is None or p3.token_data not in "0123456789abcdefABCDEF":
            self.store_error(self.current_pos(), "Invalid hexadecimal integer literal")
            return None

        while self._token_types[self._pos] in [RawTokenType.TkCharacter, RawTokenType.TkDigit]:
            p3 = self.parse_once(self.parse_lexeme_character_or_digit)
            if p3 is None or p3.token_data not in "0123456789abcdefABCDEF":
                self.store_error(self.current_pos(), "Invalid hexadecimal integer literal")
                return out
            out.token_data += p3.token_data

        return out

    def parse_lexeme_double_quote_string(self) -> Optional[Asts.TokenAst]:
        self.parse_nothing()
        out = Asts.TokenAst(self.current_pos(), SppTokenType.LxString, "")

        p1 = self.parse_once(self.parse_token_quote)
        if p1 is None: return None
        out.token_data += p1.token_data

        while self._token_types[self._pos] == RawTokenType.TkCharacter:
            p2 = self.parse_once(self.parse_lexeme_character)
            out.token_data += p2.token_data

        p3 = self.parse_once(self.parse_token_quote)
        if p3 is None: return None
        out.token_data += p3.token_data
        return out

    def parse_lexeme_identifier(self) -> Optional[Asts.TokenAst]:
        self.parse_nothing()
        out = Asts.TokenAst(self.current_pos(), SppTokenType.LxString, "")

        p0 = self.parse_optional(self.parse_token_dollar)
        if p0:
            out.token_data += p0.token_data

        p1 = self.parse_once(self.parse_lexeme_character)
        if p1 is None or not p1.token_data.islower():
            self.store_error(self.current_pos(), "Invalid identifier")
            return None
        out.token_data += p1.token_data

        while self._token_types[self._pos] in self._identifier_characters:
            p2 = self.parse_once(self.parse_lexeme_character_or_digit_or_underscore)
            if p2 is None: return out
            out.token_data += p2.token_data

        return out

    def parse_lexeme_upper_identifier(self) -> Optional[Asts.TokenAst]:
        self.parse_nothing()
        out = Asts.TokenAst(self.current_pos(), SppTokenType.LxString, "")

        p0 = self.parse_optional(self.parse_token_dollar)
        if p0:
            out.token_data += p0.token_data

        p1 = self.parse_once(self.parse_lexeme_character)
        if p1 is None or not p1.token_data.isupper():
            self.store_error(self.current_pos(), "Invalid upper identifier")
            return None
        out.token_data += p1.token_data

        while self._token_types[self._pos] in self._upper_identifier_characters:
            p2 = self.parse_once(self.parse_lexeme_character_or_digit)
            if p2 is None: return out
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

    def parse_characters(self, value: str) -> Optional[Asts.TokenAst]:
        self.parse_nothing()
        p1 = Asts.TokenAst(self.current_pos(), SppTokenType.LxString, value)

        for c in value:
            p2 = self.parse_character(c)
            if p2 is None: return None

        return p1

    def parse_character(self, value: str) -> Optional[Asts.TokenAst]:
        p1 = self.parse_once(self.parse_lexeme_character_or_digit)
        if p1 is None or p1.token_data != value:
            self.store_error(self.current_pos(), f"Expected '{value}'")
            return None
        return p1

    @inline
    def parse_keyword_raw(self, keyword: RawKeywordType, mapped_keyword: SppTokenType, requires_following_space: bool) -> Optional[Asts.TokenAst]:
        self.parse_nothing()

        p1 = Asts.TokenAst(self.current_pos(), mapped_keyword, keyword.value)
        p2 = self.parse_characters(keyword.value)
        if p2 is None: return None
        if requires_following_space:
            p3 = self.parse_token_raw(RawTokenType.TkWhitespace, SppTokenType.NoToken)
            if p3 is None: return None
        return p1

    def parse_token_raw(self, token: RawTokenType, mapped_token: SppTokenType) -> Optional[Asts.TokenAst]:
        if self._pos > self._tokens_len:
            self.store_error(self._pos, "Unexpected end of input")
            return None

        if token != RawTokenType.TkNewLine and token != RawTokenType.TkWhitespace:
            while self._token_types[self._pos] in self._nl_ws_characters:
                self._pos += 1

        elif token == RawTokenType.TkNewLine:
            while self._token_types[self._pos] is self._ws_characters:
                self._pos += 1

        elif token == RawTokenType.TkWhitespace:
            while self._token_types[self._pos] is self._nl_characters:
                self._pos += 1

        if token == RawTokenType.NoToken:
            return 1

        if self._token_types[self._pos] != token:
            if self._error.pos == self._pos:
                self._error.add_expected_token(mapped_token.value)
                return None

            if self.store_error(self._pos, f"Expected £, got '{self._tokens[self._pos].token_data}'"):
                self._error.add_expected_token(mapped_token.value)
            return None

        token_ast = Asts.TokenAst(self.current_pos(), mapped_token, self._tokens[self._pos].token_data if mapped_token in self._stringable_characters else mapped_token.value)
        self._pos += 1
        return token_ast


__all__ = ["SppParser"]
