from tests._Utils import *


class TestFunctionCallArgumentAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.ExpressionTypeInvalidError)
    def test_invalid_function_argument_unnamed_expression(self):
        """
        fun f(a: std::boolean::Bool) -> std::void::Void { }

        fun g() -> std::void::Void {
            f(std::boolean::Bool)
        }
        """

    @should_fail_compilation(SemanticErrors.ExpressionTypeInvalidError)
    def test_invalid_function_argument_named_type(self):
        """
        fun f(a: std::boolean::Bool) -> std::void::Void { }

        fun g() -> std::void::Void {
            f(a=std::boolean::Bool)
        }
        """

    @should_pass_compilation()
    def test_valid_function_argument_unnamed_expression(self):
        """
        fun f(a: std::boolean::Bool) -> std::void::Void { }

        fun g() -> std::void::Void {
            f(true)
        }
        """

    @should_pass_compilation()
    def test_valid_function_argument_named_expression(self):
        """
        fun f(a: std::boolean::Bool) -> std::void::Void { }

        fun g() -> std::void::Void {
            f(a=true)
        }
        """
