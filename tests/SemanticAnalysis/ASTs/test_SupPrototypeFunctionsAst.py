from tests._Utils import *


class TestSupPrototypeFunctionsAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.SuperimpositionUnconstrainedGenericParameterError)
    def test_invalid_sup_prototype_functions_unconstrained_generic_parameter_1(self):
        """
        cls Point {
            x: std::BigInt
            y: std::BigInt
        }

        sup [T] Point { }
        """

    @should_fail_compilation(SemanticErrors.SuperimpositionUnconstrainedGenericParameterError)
    def test_invalid_sup_prototype_functions_unconstrained_generic_parameter_2(self):
        """
        cls Point[T] {
            x: T
            y: T
        }

        sup [T, U] Point[T] { }
        """

    @should_fail_compilation(SemanticErrors.SuperimpositionOptionalGenericParameterError)
    def test_invalid_sup_prototype_functions_optional_generic_parameter(self):
        """
        cls Point[T] {
            x: T
            y: T
        }

        sup [T=std::Bool] Point[T] { }
        """

    @should_fail_compilation(SemanticErrors.GenericTypeInvalidUsageError)
    def test_invalid_sup_prototype_functions_onto_generic_type(self):
        """
        sup [T] T {
            fun f(&self) -> std::Void { }
        }
        """

    @should_fail_compilation(SemanticErrors.InvalidConventionLocationError)
    def test_invalid_superimposition_extension_type_convention_mut(self):
        """
        cls A { }
        sup &mut A { }
        """

    @should_fail_compilation(SemanticErrors.InvalidConventionLocationError)
    def test_invalid_superimposition_extension_type_convention_ref(self):
        """
        cls A { }
        sup &A { }
        """

    @should_pass_compilation()
    def test_valid_sup_prototype_functions(self):
        """
        cls A { }
        sup A {
            fun f(&self) -> std::Void { }
        }
        """

    @should_pass_compilation()
    def test_valid_sup_prototype_functions_generic_fallthrough_explicit(self):
        """
        cls BaseClass[T] { }

        sup [T] BaseClass[T] {
            @no_impl
            fun f(&self) -> T { }
        }

        fun f() -> std::Void {
            let x = BaseClass[std::Bool] ()
            let mut y = x.f()
            y = false
        }
        """

    @should_pass_compilation()
    def test_valid_sup_prototype_functions_generic_fallthrough_implicit(self):
        """
        cls BaseClass[T] { a: T }

        sup [T] BaseClass[T] {
            @no_impl
            fun f(&self) -> T { }
        }

        fun f() -> std::Void {
            let x = BaseClass(a=false)
            let mut y = x.f()
            y = false
        }
        """
