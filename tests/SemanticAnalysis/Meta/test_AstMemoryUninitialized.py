from tests._Utils import *


class TestAstMemoryUninitialized(CustomTestCase):
    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_invalid_using_uninitialized_symbol(self):
        # Use a non-initialized value (never given a value / use-after-free).
        """
        cls Point {
            x: std::bignum::bigint::BigInt
            y: std::bignum::bigint::BigInt
        }

        fun f() -> std::void::Void {
            let p: Point
            let q = p
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_invalid_using_moved_symbol(self):
        # Use a non-initialized value (value has been moved already / double-free).
        """
        cls Point {
            x: std::bignum::bigint::BigInt
            y: std::bignum::bigint::BigInt
        }

        fun f() -> std::void::Void {
            let p = Point(x=5, y=5)
            let q = p
            let r = p
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_invalid_partially_using_uninitialized_symbol(self):
        # Use part of a non-initialized value (never given a value / use-after-free).
        """
        cls Point {
            x: std::bignum::bigint::BigInt
            y: std::bignum::bigint::BigInt
        }

        fun f() -> std::void::Void {
            let p: Point
            let x = p.x
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_invalid_partially_using_moved_symbol(self):
        # Use part of a non-initialized value (value has been moved already / double-free).
        """
        cls Point {
            x: std::bignum::bigint::BigInt
            y: std::bignum::bigint::BigInt
        }

        fun f() -> std::void::Void {
            let p = Point(x=5, y=5)
            let q = p
            let x = p.x
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_invalid_partially_using_partially_moved_symbol_same_part(self):
        # Use part of a partially-initialized value (value has been moved already / double-free).
        """
        cls Point {
            x: std::bignum::bigint::BigInt
            y: std::bignum::bigint::BigInt
        }

        fun f() -> std::void::Void {
            let p = Point(x=5, y=5)
            let x1 = p.x
            let x2 = p.x
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryPartiallyInitializedUsageError)
    def test_invalid_using_partially_moved_symbol(self):
        # Use a value that has been partially moved.
        """
        cls Point {
            x: std::bignum::bigint::BigInt
            y: std::bignum::bigint::BigInt
        }

        fun f() -> std::void::Void {
            let p = Point(x=5, y=5)
            let x = p.x
            let q = p
        }
        """

    @should_pass_compilation()
    def test_valid_multiple_partial_moves_different_parts(self):
        # Move different parts of a value over multiple expressions.
        """
        cls Point {
            x: std::bignum::bigint::BigInt
            y: std::bignum::bigint::BigInt
        }

        fun f() -> std::void::Void {
            let p = Point(x=5, y=5)
            let x = p.x
            let y = p.y
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_array(self):
        """
        fun f() -> std::void::Void {
            let elem: std::string::Str
            let a = [elem]
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_assignment(self):
        """
        cls Point {
            x: std::bignum::bigint::BigInt
            y: std::bignum::bigint::BigInt
        }

        fun f() -> std::void::Void {
            let mut point: Point
            point.x = 5
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_binary_expression_lhs(self):
        """
        fun f() -> std::void::Void {
            let elem: std::bignum::bigint::BigInt
            let a = elem + 123
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_binary_expression_rhs(self):
        """
        fun f() -> std::void::Void {
            let elem: std::bignum::bigint::BigInt
            let a = 123 + elem
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_case_expression_condition(self):
        """
        fun f() -> std::void::Void {
            let elem: std::bignum::bigint::BigInt
            case elem of
                == 1 { }
                == 2 { }
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_case_expression_branch(self):
        """
        fun f() -> std::void::Void {
            let elem: std::bignum::bigint::BigInt
            case 1 of
                == elem { }
                else { }
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_function_call_argument_unnamed(self):
        """
        fun g(a: std::string::Str) -> std::void::Void { }
        fun f() -> std::void::Void {
            let elem: std::string::Str
            let a = g(elem)
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_function_call_argument_named(self):
        """
        fun g(a: std::string::Str) -> std::void::Void { }
        fun f() -> std::void::Void {
            let elem: std::string::Str
            let a = g(a=elem)
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_gen_mov_expression(self):
        """
        cor f() -> std::generator::Gen[std::string::Str] {
            let elem: std::string::Str
            gen elem
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_gen_mut_expression(self):
        """
        cor f() -> std::generator::Gen[&mut std::string::Str] {
            let elem: std::string::Str
            gen &mut elem
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_gen_ref_expression(self):
        """
        cor f() -> std::generator::Gen[&std::string::Str] {
            let elem: std::string::Str
            gen &elem
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_generic_comp_argument_unnamed(self):
        """
        fun g[cmp n: std::string::Str]() -> std::void::Void { }

        fun f() -> std::void::Void {
            let elem: std::string::Str
            let a = g[elem]()
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_generic_comp_argument_named(self):
        """
        fun g[cmp n: std::string::Str]() -> std::void::Void { }

        fun f() -> std::void::Void {
            let elem: std::string::Str
            let a = g[n=elem]()
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_is_expression(self):
        """
        cls Point {
            x: std::bignum::bigint::BigInt
            y: std::bignum::bigint::BigInt
        }

        fun f() -> std::void::Void {
            let elem: Point
            case elem of
                is Point(x=0, y) { }
                is Point(x, y=0) { }
                else { }
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_lambda_capture_mov(self):
        """
        fun f() -> std::void::Void {
            let elem: std::string::Str
            let a = |caps elem| { }
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_lambda_capture_mut(self):
        """
        fun f() -> std::void::Void {
            let mut elem: std::string::Str
            let a = |caps &mut elem| { }
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_lambda_capture_ref(self):
        """
        fun f() -> std::void::Void {
            let elem: std::string::Str
            let a = |caps &elem| { }
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_let_statement(self):
        """
        fun f() -> std::void::Void {
            let elem: std::string::Str
            let a = elem
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_parenthesis(self):
        """
        fun f() -> std::void::Void {
            let elem: std::string::Str
            let a = (elem)
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_loop_condition_boolean(self):
        """
        fun f() -> std::void::Void {
            let elem: std::boolean::Bool
            loop elem { }
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_loop_condition_iterable(self):
        """
        fun f() -> std::void::Void {
            let iterator: std::generator::Gen[std::string::Str]
            loop elem in iterator { }
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_object_initializer_argument_unnamed(self):
        """
        fun f() -> std::void::Void {
            let data: std::vector::Vec[std::number::U8]
            let a = std::string::Str(data)
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_object_initializer_argument_named(self):
        """
        fun f() -> std::void::Void {
            let data_vec: std::vector::Vec[std::number::U8]
            let a = std::string::Str(data=data_vec)
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_pattern_guard(self):
        """
        fun f() -> std::void::Void {
            let elem: std::boolean::Bool
            case true of
                == false and elem { }
                else { }
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_postfix_expression_operator_member_access_attribute(self):
        """
        fun f() -> std::void::Void {
            let elem: std::string::Str
            elem.data
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_postfix_expression_operator_member_access_index(self):
        """
        fun f() -> std::void::Void {
            let elem: (std::string::Str, std::string::Str)
            elem.0
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_postfix_expression_operator_not_keyword(self):
        """
        fun f() -> std::void::Void {
            let elem: std::boolean::Bool
            elem.not
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_postfix_expression_operator_res_keyword(self):
        """
        fun f() -> std::void::Void {
            let elem: std::generator::Gen[std::string::Str, std::boolean::Bool]
            elem.res(false)
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_ret_statement(self):
        """
        fun f() -> std::string::Str {
            let elem: std::string::Str
            ret elem
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_unary_expression_operator_async(self):
        """
        fun f() -> std::void::Void {
            let elem: std::function::FunRef[(std::string::Str,), std::void::Void]
            let a = async elem("hello world")
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_postfix_expression_operator_function_call(self):
        """
        fun f() -> std::void::Void {
            let elem: std::function::FunRef[(std::string::Str,), std::void::Void]
            let a = elem("hello world")
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_tuple(self):
        """
        fun f() -> std::void::Void {
            let elem: std::string::Str
            let a = (elem,)
        }
        """
