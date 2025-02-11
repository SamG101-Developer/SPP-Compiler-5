from unittest import TestCase

from tests._Utils import *


class TestFunctionParameterOptionalAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.ExpressionTypeInvalidError)
    def test_invalid_function_parameter_optional_invalid_default(self):
        """
        fun f(a: std::Bool = std::Bool) -> std::Void { }
        """

    @should_fail_compilation(SemanticErrors.ParameterOptionalNonBorrowTypeError)
    def test_invalid_function_parameter_optional_invalid_convention(self):
        """
        fun f(a: &std::Bool = true) -> std::Void { }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_function_parameter_optional_invalid_type(self):
        """
        fun f(a: std::Bool = 1) -> std::Void { }
        """

    @should_pass_compilation()
    def test_valid_function_parameter_optional(self):
        """
        fun f(a: std::Bool = true) -> std::Void { }
        """
