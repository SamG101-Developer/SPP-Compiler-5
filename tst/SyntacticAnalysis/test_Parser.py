from unittest import TestCase

from SPPCompiler.SyntacticAnalysis.Parser import Parser
from tst._Utils import should_fail_parsing, should_pass_parsing


class TestParser(TestCase):
    @should_pass_parsing(Parser.parse_class_prototype)
    def test_parse_class_prototype(self):
        """
        cls TestClass[T, U] {
            test_attribute_1: TestType1
            test_attribute_2: TestType2
        }
        """

    @should_pass_parsing(Parser.parse_sup_prototype_functions)
    def test_parse_sup_prototype_functions(self):
        """
        sup [T, U] TestClass[T, U] {
            fun test_func_1() -> TestType1 { }
            fun test_func_2() -> TestType1 { }
        }
        """

    @should_pass_parsing(Parser.parse_sup_prototype_inheritance)
    def test_parse_sup_prototype_inheritance(self):
        """
        sup [T, U] TestNewClass[T, U] ext TestClass {
            fun test_func_1() -> TestType1 { }
            fun test_func_2() -> TestType1 { }
        }
        """

    @should_pass_parsing(Parser.parse_function_prototype)
    def test_parse_function_prototype(self):
        """
        fun test_func_1[T](a: T, b: Str = "hello", ..c: Bool) -> TestType1 { }
        """

    @should_pass_parsing(Parser.parse_parenthesized_expression)
    def test_parse_parenthesized_expression(self):
        """
        (1 + 2)
        """

    @should_pass_parsing(Parser.parse_case_expression)
    def test_parse_case_expression(self):
        """
        case condition then
            == 1 { }
        """

    @should_pass_parsing(Parser.parse_loop_expression)
    def test_parse_loop_expression_condition_boolean(self):
        """
        loop true { }
        """

    @should_pass_parsing(Parser.parse_loop_expression)
    def test_parse_loop_expression_condition_iterable(self):
        """
        loop x in y { }
        """

    @should_pass_parsing(Parser.parse_gen_expression)
    def test_parse_gen_expression_normal_no_expression(self):
        """
        gen
        """

    @should_pass_parsing(Parser.parse_gen_expression)
    def test_parse_gen_expression_normal_with_expression(self):
        """
        gen &mut 123
        """

    @should_pass_parsing(Parser.parse_gen_expression)
    def test_parse_gen_expression_unroll(self):
        """
        gen with other_generator
        """

    @should_pass_parsing(Parser.parse_with_expression)
    def test_parse_with_expression(self):
        """
        with let x = context { }
        """

    @should_pass_parsing(Parser.parse_ret_statement)
    def test_parse_return_statement(self):
        """
        ret expression
        """

    @should_pass_parsing(Parser.parse_pin_statement)
    def test_parse_pin_statement(self):
        """
        pin a, a.b, c
        """

    @should_pass_parsing(Parser.parse_rel_statement)
    def test_parse_rel_statement(self):
        """
        rel a, a.b, c
        """

    @should_pass_parsing(Parser.parse_inner_scope)
    def test_parse_inner_scope(self):
        """
        {}
        """

    @should_pass_parsing(Parser.parse_use_statement)
    def test_parse_use_statement_namespace_reduction_types_multiple(self):
        """
        use std::{Str, inner::{A, B}, C}
        """

    @should_pass_parsing(Parser.parse_use_statement)
    def test_parse_use_statement_namespace_reduction_types_single(self):
        """
        use std::BigInt
        """

    @should_pass_parsing
    def test_parse_use_statement_type_alias(self):
        """
        use Vec[T] as MyVector[T]
        """

    @should_pass_parsing(Parser.parse_global_constant)
    def test_parse_global_constant(self):
        """
        cmp constant = 123
        """

    @should_pass_parsing(Parser.parse_let_statement)
    def test_parse_local_variable_single_identifier(self):
        """
        let x = 1
        """

    @should_pass_parsing(Parser.parse_let_statement)
    def test_parse_local_variable_object_destructure(self):
        """
        let Vec(pos=Point(x, y, z), direction) = v
        """

    @should_pass_parsing(Parser.parse_let_statement)
    def test_parse_local_variable_tuple_destructure(self):
        """
        let ((a, b), (c, (d, e))) = t
        """

    @should_pass_parsing(Parser.parse_assignment_statement)
    def test_parse_assignment_statement(self):
        """
        x, y = 1, 2
        """

    @should_pass_parsing(Parser.parse_case_expression)
    def test_parse_pattern_variant_object_destructure(self):
        """
        case expression then
            is Class(attr, attr2=123, ..) { }
            is Class(attr, attr3=456, ..) { }
        """

    @should_pass_parsing(Parser.parse_case_expression)
    def test_parse_pattern_variant_tuple_destructure(self):
        """
        case expression then
            is (1, a, (3, b)) { }
            is (2, a, (c, d)) { }
        """

    @should_pass_parsing(Parser.parse_case_expression)
    def test_parse_pattern_variant_else(self):
        """
        case expression then
            == 1 { }
            == 2 { }
            else { }
        """

    @should_pass_parsing(Parser.parse_case_expression)
    def test_parse_pattern_variant_else_case(self):
        """
        case x then == 1 {
            let a = 1
        }
        else case y then == true {
            let b = 2
        }
        else case z then == true {
            let c = 3
        }
        else {
            let d = 4
        }
        """

    @should_pass_parsing(Parser.parse_case_expression)
    def test_parse_pattern_guard(self):
        """
        case expression then
            is (1, a) && a < 100 { }
            is (a, 1) && a > 100 { }
        """

    @should_pass_parsing(Parser.parse_unary_expression)
    def test_parse_unary_op_async_call(self):
        """
        async function_call()
        """

    @should_pass_parsing(Parser.parse_postfix_expression)
    def test_parse_postfix_op_function_call(self):
        """
        function_call()
        """

    @should_pass_parsing(Parser.parse_postfix_expression)
    def test_parse_postfix_op_member_access_runtime(self):
        """
        class.attribute_tuple.0.attribute
        """

    @should_pass_parsing(Parser.parse_postfix_expression)
    def test_parse_postfix_op_member_access_static(self):
        """
        Class::static_method()
        """

    @should_pass_parsing(Parser.parse_postfix_expression)
    def test_parse_postfix_op_early_return(self):
        """
        x?
        """

    @should_pass_parsing(Parser.parse_postfix_expression)
    def test_parse_postfix_op_not_keyword(self):
        """
        x.not
        """

    @should_pass_parsing(Parser.parse_postfix_expression)
    def test_parse_object_initialization(self):
        """
        Object(a, b, c=1, d=2, e, sup=(a, b), else=other)
        """

    @should_pass_parsing(Parser.parse_literal_string)
    def test_parse_literal_string(self):
        """
        "test"
        """

    @should_pass_parsing(Parser.parse_literal_regex)
    def test_parse_literal_regex(self):
        """
        r"test"
        """

    @should_pass_parsing(Parser.parse_literal_boolean)
    def test_parse_literal_boolean(self):
        """
        true
        """

    @should_pass_parsing(Parser.parse_literal_float)
    def test_parse_literal_float_b10(self):
        """
        -100.0_f32
        """

    @should_pass_parsing(Parser.parse_literal_integer)
    def test_parse_literal_integer_b10(self):
        """
        -100_u64
        """

    @should_pass_parsing(Parser.parse_literal_integer)
    def test_parse_literal_integer_b02(self):
        """
        0b10_u32
        """

    @should_pass_parsing(Parser.parse_literal_integer)
    def test_parse_literal_integer_b16(self):
        """
        0xff_u32
        """

    @should_pass_parsing(Parser.parse_literal_tuple)
    def test_parse_literal_tuple_0_items(self):
        """
        ()
        """

    @should_pass_parsing(Parser.parse_literal_tuple)
    def test_parse_literal_tuple_1_items(self):
        """
        (a,)
        """

    @should_pass_parsing(Parser.parse_literal_tuple)
    def test_parse_literal_tuple_n_items(self):
        """
        (a, b, c)
        """

    @should_pass_parsing(Parser.parse_literal_array)
    def test_parse_literal_array_0_items(self):
        """
        [U32, 5]
        """

    @should_pass_parsing(Parser.parse_literal_array)
    def test_parse_literal_array_n_items(self):
        """
        [0, 1, 2, 3, 4]
        """
