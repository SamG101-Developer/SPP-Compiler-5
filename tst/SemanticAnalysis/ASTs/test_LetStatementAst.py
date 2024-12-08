from unittest import TestCase

from tst._Utils import *


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
