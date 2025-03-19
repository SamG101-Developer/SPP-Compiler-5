from tests._Utils import *


class TestFunctionParameterOptionalAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.ExpressionTypeInvalidError)
    def test_invalid_function_parameter_optional_invalid_default(self):
        """
        fun f(a: std::boolean::Bool = std::boolean::Bool) -> std::void::Void { }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_function_parameter_optional_invalid_type(self):
        """
        fun f(a: std::boolean::Bool = 1) -> std::void::Void { }
        """

    @should_pass_compilation()
    def test_valid_function_parameter_optional(self):
        """
        fun f(a: std::boolean::Bool = true) -> std::void::Void { }
        """
