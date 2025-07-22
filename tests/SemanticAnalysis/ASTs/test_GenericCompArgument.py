from tests._Utils import *


class TestGenericCompArgument(CustomTestCase):
    @should_fail_compilation(SemanticErrors.FunctionCallNoValidSignaturesError)
    def test_invalid_generic_comp_parameter_value_type_func_call(self):
        """
        fun g[cmp n: std::boolean::Bool]() -> std::void::Void { }
        fun f() -> std::void::Void {
            g[123]()
        }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_generic_comp_parameter_value_type_obj_init(self):
        """
        cls G[cmp n: std::boolean::Bool] {}
        fun f() -> std::void::Void {
            let g = G[123]()
        }
        """

    @should_pass_compilation()
    def test_valid_generic_comp_parameter_value_type_func_call(self):
        """
        fun g[cmp n: std::boolean::Bool]() -> std::void::Void { }
        fun f() -> std::void::Void {
            g[true]()
        }
        """

    @should_pass_compilation()
    def test_valid_generic_comp_parameter_value_type_obj_init(self):
        """
        cls G[cmp n: std::boolean::Bool] {}
        fun f() -> std::void::Void {
            let g = G[true]()
        }
        """
