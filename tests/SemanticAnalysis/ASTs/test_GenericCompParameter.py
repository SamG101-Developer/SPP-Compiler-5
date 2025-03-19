from tests._Utils import *


class TestGenericCompParameter(CustomTestCase):
    @should_fail_compilation(SemanticErrors.InvalidConventionLocationError)
    def test_invalid_generic_comp_parameter_required_convention_mut(self):
        """
        fun f[cmp n: &mut std::boolean::Bool]() -> std::void::Void { }
        """

    @should_fail_compilation(SemanticErrors.InvalidConventionLocationError)
    def test_invalid_generic_comp_parameter_required_convention_ref(self):
        """
        fun f[cmp n: &std::boolean::Bool]() -> std::void::Void { }
        """

    @should_fail_compilation(SemanticErrors.InvalidConventionLocationError)
    def test_invalid_generic_comp_parameter_optional_convention_mut(self):
        """
        fun f[cmp n: &mut std::boolean::Bool = false]() -> std::void::Void { }
        """

    @should_fail_compilation(SemanticErrors.InvalidConventionLocationError)
    def test_invalid_generic_comp_parameter_optional_convention_ref(self):
        """
        fun f[cmp n: &std::boolean::Bool = false]() -> std::void::Void { }
        """

    @should_fail_compilation(SemanticErrors.InvalidConventionLocationError)
    def test_invalid_generic_comp_parameter_variadic_convention_mut(self):
        """
        fun f[cmp ..n: &std::boolean::Bool]() -> std::void::Void { }
        """

    @should_fail_compilation(SemanticErrors.InvalidConventionLocationError)
    def test_invalid_generic_comp_parameter_variadic_convention_ref(self):
        """
        fun f[cmp ..n: &mut std::boolean::Bool]() -> std::void::Void { }
        """
