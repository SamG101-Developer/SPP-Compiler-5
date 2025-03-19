from unittest import TestCase

from tests._Utils import *


class TestPostfixExpressionMemberAccessAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.MemberAccessStaticOperatorExpectedError)
    def test_invalid_postfix_member_access_static_operator_expected_on_type(self):
        """
        cls Point {
            x: std::number::BigInt
            y: std::number::BigInt
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
            x: std::number::BigInt
            y: std::number::BigInt
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
            x: std::number::BigInt
            y: std::number::BigInt
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
            x: std::number::BigInt
            y: std::number::BigInt
        }

        fun f(p: Point) -> std::void::Void {
            p.0
        }
        """

    @should_fail_compilation(SemanticErrors.MemberAccessIndexOutOfBoundsError)
    def test_invalid_postfix_member_access_index_out_of_bounds_tuple(self):
        """
        fun f(p: (std::number::BigInt, std::number::BigInt)) -> std::void::Void {
            p.3
        }
        """

    @should_pass_compilation()
    def test_valid_postfix_member_access_tuple(self):
        """
        fun f(p: (std::number::BigInt, std::number::BigInt)) -> std::void::Void {
            p.0
        }
        """

    @should_fail_compilation(SemanticErrors.MemberAccessIndexOutOfBoundsError)
    def test_invalid_postfix_member_access_index_out_of_bounds_array(self):
        """
        fun f(p: std::array::Arr[std::number::BigInt, 2]) -> std::void::Void {
            p.3
        }
        """

    @should_pass_compilation()
    def test_valid_postfix_member_access_array(self):
        """
        fun f(p: std::array::Arr[std::number::BigInt, 2]) -> std::void::Void {
            p.0
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
            std::console::print("hello")
        }
        """

    @should_fail_compilation(SemanticErrors.IdentifierUnknownError)
    def test_invalid_postfix_member_access_unknown_field_on_variable(self):
        """
        fun f(p: std::number::BigInt) -> std::void::Void {
            p.x
        }
        """

    @should_pass_compilation()
    def test_valid_postfix_member_on_variable(self):
        """
        cls Point {
            x: std::number::BigInt
            y: std::number::BigInt
        }

        fun f(p: Point) -> std::void::Void {
            p.x
        }
        """

    @should_fail_compilation(SemanticErrors.MemberAccessRuntimeOperatorExpectedError)
    def test_invalid_postfix_member_access_runtime_operator_expected_on_variable(self):
        """
        cls Point {
            x: std::number::BigInt
            y: std::number::BigInt
        }

        fun f(p: Point) -> std::void::Void {
            let x = p::x
        }
        """

    @should_pass_compilation()
    def test_valid_postfix_member_access_runtime_operator_on_variable(self):
        """
        cls Point {
            x: std::number::BigInt
            y: std::number::BigInt
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
            let x = std::console::print("hello")
        }
        """
