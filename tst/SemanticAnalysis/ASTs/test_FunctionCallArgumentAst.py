from unittest import TestCase

from tst._Utils import *


class TestFunctionCallArgumentAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.ExpressionTypeInvalidError)
    def test_invalid_function_argument_unnamed_expression(self):
        """
        fun f(a: std::Bool) -> std::Void { }

        fun g() -> std::Void {
            f(std::Bool)
        }
        """

    @should_fail_compilation(SemanticErrors.ExpressionTypeInvalidError)
    def test_invalid_function_argument_named_type(self):
        """
        fun f(a: std::Bool) -> std::Void { }

        fun g() -> std::Void {
            f(a=std::Bool)
        }
        """

    @should_pass_compilation()
    def test_valid_function_argument_unnamed_expression(self):
        """
        fun f(a: std::Bool) -> std::Void { }

        fun g() -> std::Void {
            f(true)
        }
        """

    @should_pass_compilation()
    def test_valid_function_argument_named_expression(self):
        """
        fun f(a: std::Bool) -> std::Void { }

        fun g() -> std::Void {
            f(a=true)
        }
        """
