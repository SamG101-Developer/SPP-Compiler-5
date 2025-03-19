from tests._Utils import *


class TestFunctionParameterSelfAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.InvalidSelfTypeError)
    def test_function_parameter_self_ast_invalid_arbitrary_type(self):
        """
        cls TestType { }
        sup TestType {
            fun f(self: std::string::Str) -> std::void::Void { }
        }
        """

    @should_fail_compilation(ParserErrors.SyntaxError)
    def test_function_parameter_self_ast_invalid_arbitrary_type_convention(self):
        """
        cls TestType { }
        sup TestType {
            fun f(&self: &Single[Self]) -> std::void::Void { }
        }
        """

    @should_pass_compilation()
    def test_function_parameter_self_ast_strict_type_mov(self):
        """
        cls TestType { }
        sup TestType {
            fun f(self) -> std::void::Void { }
        }
        """

    @should_pass_compilation()
    def test_function_parameter_self_ast_strict_type_mut(self):
        """
        cls TestType { }
        sup TestType {
            fun f(&mut self) -> std::void::Void { }
        }
        """

    @should_pass_compilation()
    def test_function_parameter_self_ast_strict_type_ref(self):
        """
        cls TestType { }
        sup TestType {
            fun f(&self) -> std::void::Void { }
        }
        """

    @should_pass_compilation()
    def test_function_parameter_self_ast_valid_arbitrary_type(self):
        """
        cls TestType { }
        sup TestType {
            fun f(self: &std::single::Single[Self]) -> std::void::Void { }
        }
        """
