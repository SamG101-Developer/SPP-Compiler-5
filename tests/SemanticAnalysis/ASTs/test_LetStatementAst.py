from unittest import TestCase

from tests._Utils import *


class TestLetStatementAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.ExpressionTypeInvalidError)
    def test_invalid_expression_type(self):
        """
        fun f() -> std::Void {
            let x = std::Bool
        }
        """

    @should_fail_compilation(SemanticErrors.TypeVoidInvalidUsageError)
    def test_invalid_type_void(self):
        """
        fun f() -> std::Void {
            let x: std::Void
        }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_tye_convention(self):
        """
        fun f(b: &std::Bool) -> std::Void {
            let mut x: &mut std::Bool
            x = b
        }
        """

    @should_pass_compilation()
    def test_valid_let_statement_uninitialized(self):
        """
        fun f() -> std::Void {
            let x = false
        }
        """

    @should_pass_compilation()
    def test_valid_let_statement(self):
        """
        fun f() -> std::Void {
            let x: std::BigInt
        }
        """

    @should_pass_compilation()
    def test_valid_convention(self):
        """
        fun f(b: &std::Bool) -> std::Void {
            let mut x: & std::Bool
            x = b
        }
        """
