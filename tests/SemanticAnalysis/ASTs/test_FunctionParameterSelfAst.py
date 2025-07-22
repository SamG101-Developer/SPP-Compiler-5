from tests._Utils import *


class TestFunctionParameterSelfAst(CustomTestCase):
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
