from tests._Utils import *


class TestParenthesizedExpressionAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.ExpressionTypeInvalidError)
    def test_invalid_parenthesized_expression_invalid_expression_type(self):
        """
        fun f() -> std::void::Void {
            let a = (std::boolean::Bool)
        }
        """

    @should_pass_compilation()
    def test_valid_parenthesized_expression_valid_expression_type(self):
        """
        fun f() -> std::void::Void {
            let mut a = (true)
            a = false
        }
        """
