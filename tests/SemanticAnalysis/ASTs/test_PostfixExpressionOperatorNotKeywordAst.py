from tests._Utils import *


class TestPostfixExpressionOperatorNotKeywordAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.ExpressionNotBooleanError)
    def test_invalid_postfix_expression_not_keyword_type_mismatch(self):
        """
        fun f() -> std::void::Void {
            123.not
        }
        """

    @should_pass_compilation()
    def test_valid_postfix_expression_not_keyword(self):
        """
        fun f() -> std::void::Void {
            true.not
        }
        """
