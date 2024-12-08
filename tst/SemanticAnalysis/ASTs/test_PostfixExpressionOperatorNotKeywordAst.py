from unittest import TestCase

from tst._Utils import *


class TestPostfixExpressionNotKeywordAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.ExpressionNotBooleanError)
    def test_invalid_postfix_expression_not_keyword_type_mismatch(self):
        """
        fun f() -> std::Void {
            123.not
        }
        """

    @should_pass_compilation()
    def test_valid_postfix_expression_not_keyword(self):
        """
        fun f() -> std::Void {
            true.not
        }
        """
