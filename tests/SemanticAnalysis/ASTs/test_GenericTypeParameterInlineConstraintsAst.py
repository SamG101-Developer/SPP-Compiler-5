from tests._Utils import *


class TestGenericTypeParameterInlineConstraintsAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.IdentifierDuplicationError)
    def test_invalid_generic_type_parameter_inline_constraints_duplicate(self):
        """
        fun f[T: std::boolean::Bool & std::boolean::Bool]() -> std::void::Void { }
        """

    @should_pass_compilation()
    def test_valid_generic_type_parameter_inline_constraints(self):
        """
        fun f[T: std::boolean::Bool]() -> std::void::Void { }
        """
