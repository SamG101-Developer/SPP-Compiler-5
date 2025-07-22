from tests._Utils import *


class TestPostfixExpressionOperatorMemberAccessAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.MemberAccessStaticOperatorExpectedError)
    def test_invalid_postfix_member_access_static_operator_expected_on_type(self):
        """
        cls Point {
            x: std::bignum::bigint::BigInt
            y: std::bignum::bigint::BigInt
        }

        sup Point {
            fun f() -> std::void::Void { }
        }

        fun f() -> std::void::Void {
            Point.f()
        }
        """

    @should_pass_compilation()
    def test_valid_postfix_member_access_static_operator_on_type(self):
        """
        cls Point {
            x: std::bignum::bigint::BigInt
            y: std::bignum::bigint::BigInt
        }

        sup Point {
            fun f() -> std::void::Void { }
        }

        fun f() -> std::void::Void {
            Point::f()
        }
        """

    @should_fail_compilation(SemanticErrors.IdentifierUnknownError)
    def test_invalid_postfix_member_access_unknown_field_on_type(self):
        """
        cls Point {
            x: std::bignum::bigint::BigInt
            y: std::bignum::bigint::BigInt
        }

        fun f(p: Point) -> std::void::Void {
            Point::f()
        }
        """

    @should_fail_compilation(SemanticErrors.GenericTypeInvalidUsageError)
    def test_invalid_postfix_member_access_indexing_generic_type(self):
        """
        fun f[T](p: T) -> std::void::Void {
            p.0
        }
        """

    @should_fail_compilation(SemanticErrors.MemberAccessNonIndexableError)
    def test_invalid_postfix_member_access_non_indexable_type(self):
        """
        cls Point {
            x: std::bignum::bigint::BigInt
            y: std::bignum::bigint::BigInt
        }

        fun f(p: Point) -> std::void::Void {
            p.0
        }
        """

    @should_fail_compilation(SemanticErrors.MemberAccessIndexOutOfBoundsError)
    def test_invalid_postfix_member_access_index_out_of_bounds_tuple(self):
        """
        fun f(p: (std::bignum::bigint::BigInt, std::bignum::bigint::BigInt)) -> std::void::Void {
            p.2
        }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_postfix_member_access_invalid_type_check(self):
        """
        fun f(p: (std::bignum::bigint::BigInt, std::string::Str)) -> std::void::Void {
            let mut x = p.0
            x = false
        }
        """

    @should_fail_compilation(SemanticErrors.MemberAccessIndexOutOfBoundsError)
    def test_invalid_postfix_member_access_index_out_of_bounds_array(self):
        """
        fun f(p: [std::boolean::Bool, 2]) -> std::void::Void {
            p.2
        }
        """

    @should_pass_compilation()
    def test_valid_postfix_member_access_array(self):
        """
        fun f(p: [std::string::Str, 2]) -> std::void::Void {
            let mut x = p.0
            x = "hello world"
        }
        """

    @should_pass_compilation()
    def test_valid_postfix_member_access_tuple(self):
        """
        fun f(p: (std::bignum::bigint::BigInt, std::bignum::bigint::BigInt)) -> std::void::Void {
            p.0
        }
        """

    @should_pass_compilation()
    def test_valid_postfix_member_access_tuple_type_check(self):
        """
        fun f(p: (std::bignum::bigint::BigInt, std::string::Str)) -> std::void::Void {
            let mut x = p.0
            x = 123
        }
        """

    @should_pass_compilation()
    def test_valid_postfix_member_access_array(self):
        """
        fun f(p: [std::string::Str, 2]) -> std::void::Void {
            p.0
        }
        """

    @should_pass_compilation()
    def test_valid_postfix_member_access_array_type_check(self):
        """
        fun f(p: [std::string::Str, 2]) -> std::void::Void {
            let mut x = p.0
            x = "hello world"
        }
        """

    @should_fail_compilation(SemanticErrors.GenericTypeInvalidUsageError)
    def test_invalid_postfix_member_access_generic_type(self):
        """
        fun f[T](p: T) -> std::void::Void {
            p.x
        }
        """

    @should_fail_compilation(SemanticErrors.MemberAccessStaticOperatorExpectedError)
    def test_invalid_postfix_member_access_static_operator_expected_on_namespace(self):
        """
        fun f() -> std::void::Void {
            std.print()
        }
        """

    @should_pass_compilation()
    def test_valid_postfix_member_access_static_operator_on_namespace(self):
        """
        fun f() -> std::void::Void {
            std::io::print(&"hello")
        }
        """

    @should_fail_compilation(SemanticErrors.IdentifierUnknownError)
    def test_invalid_postfix_member_access_unknown_field_on_variable(self):
        """
        fun f(p: std::bignum::bigint::BigInt) -> std::void::Void {
            p.x
        }
        """

    @should_pass_compilation()
    def test_valid_postfix_member_on_variable(self):
        """
        cls Point {
            x: std::bignum::bigint::BigInt
            y: std::bignum::bigint::BigInt
        }

        fun f(p: Point) -> std::void::Void {
            p.x
        }
        """

    @should_fail_compilation(SemanticErrors.MemberAccessRuntimeOperatorExpectedError)
    def test_invalid_postfix_member_access_runtime_operator_expected_on_variable(self):
        """
        cls Point {
            x: std::bignum::bigint::BigInt
            y: std::bignum::bigint::BigInt
        }

        fun f(p: Point) -> std::void::Void {
            let x = p::x
        }
        """

    @should_pass_compilation()
    def test_valid_postfix_member_access_runtime_operator_on_variable(self):
        """
        cls Point {
            x: std::bignum::bigint::BigInt
            y: std::bignum::bigint::BigInt
        }

        fun f(p: Point) -> std::void::Void {
            let x = p.x
        }
        """

    @should_fail_compilation(SemanticErrors.IdentifierUnknownError)
    def test_invalid_postfix_member_access_unknown_field_on_namespace(self):
        """
        fun f() -> std::void::Void {
            let x = std::non_existent()
        }
        """

    @should_pass_compilation()
    def test_valid_postfix_member_access_on_namespace(self):
        """
        fun f() -> std::void::Void {
            let x = std::io::print(&"hello")
        }
        """
