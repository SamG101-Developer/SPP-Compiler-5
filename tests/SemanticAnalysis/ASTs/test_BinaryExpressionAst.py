from tests._Utils import *


# Todo: invalid and valid testing of binary "is" operation


class TestBinaryExpressionAst(CustomTestCase):
    @should_pass_compilation()
    def test_valid_binary_operation(self):
        """
        fun f() -> std::void::Void {
            let a = 1 + 2
        }
        """

    @should_pass_compilation()
    def test_valid_binary_operation_lhs_folding(self):
        """
        fun f(b: (std::number::bigint::BigInt, std::number::bigint::BigInt, std::number::bigint::BigInt, std::number::bigint::BigInt)) -> std::void::Void {
            let a = .. + b
        }
        """

    @should_pass_compilation()
    def test_valid_binary_operation_rhs_folding(self):
        """
        fun f(a: (std::number::bigint::BigInt, std::number::bigint::BigInt, std::number::bigint::BigInt, std::number::bigint::BigInt)) -> std::void::Void {
            let b = a + ..
        }
        """

    @should_fail_compilation(SemanticErrors.ExpressionTypeInvalidError)
    def test_invalid_binary_operation_lhs_value(self):
        """
        fun f() -> std::void::Void {
            let a = std::number::bigint::BigInt + 2
        }
        """

    @should_fail_compilation(SemanticErrors.ExpressionTypeInvalidError)
    def test_invalid_binary_operation_rhs_value(self):
        """
        fun f() -> std::void::Void {
            let a = 1 + std::number::bigint::BigInt
        }
        """

    @should_fail_compilation(SemanticErrors.MemberAccessNonIndexableError)
    def test_invalid_binary_operation_lhs_folding(self):
        """
        fun f(b: std::number::bigint::BigInt) -> std::void::Void {
            let a = .. + b
        }
        """

    @should_fail_compilation(SemanticErrors.MemberAccessNonIndexableError)
    def test_invalid_binary_operation_rhs_folding(self):
        """
        fun f(a: std::number::bigint::BigInt) -> std::void::Void {
            let b = a + ..
        }
        """
