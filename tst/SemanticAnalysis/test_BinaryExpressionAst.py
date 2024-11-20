from unittest import TestCase

from tst._Utils import *


class TestAnnotationAst(TestCase):
    @should_pass_compilation()
    def test_valid_binary_operation(self):
        """
        fun f() -> std::Void {
            let a = 1 + 2
        }
        """

    @should_pass_compilation()
    def test_valid_binary_operation_lhs_folding(self):
        """
        fun f(b: (std::BigInt, std::BigInt, std::BigInt, std::BigInt)) -> std::Void {
            let a = .. + b
        }
        """

    @should_pass_compilation()
    def test_valid_binary_operation_rhs_folding(self):
        """
        fun f(a: (std::BigInt, std::BigInt, std::BigInt, std::BigInt)) -> std::Void {
            let b = a + ..
        }
        """

    @should_fail_compilation(SemanticErrors.ExpressionTypeInvalidError)
    def test_invalid_binary_operation_lhs_value(self):
        """
        fun f() -> std::Void {
            let a = std::BigInt + 2
        }
        """

    @should_fail_compilation(SemanticErrors.ExpressionTypeInvalidError)
    def test_invalid_binary_operation_rhs_value(self):
        """
        fun f() -> std::Void {
            let a = 1 + std::BigInt
        }
        """

    @should_fail_compilation(SemanticErrors.MemberAccessNonIndexableError)
    def test_invalid_binary_operation_lhs_folding(self):
        """
        fun f(b: std::BigInt) -> std::Void {
            let a = .. + b
        }
        """

    @should_fail_compilation(SemanticErrors.MemberAccessNonIndexableError)
    def test_invalid_binary_operation_rhs_folding(self):
        """
        fun f(a: std::BigInt) -> std::Void {
            let b = a + ..
        }
        """
