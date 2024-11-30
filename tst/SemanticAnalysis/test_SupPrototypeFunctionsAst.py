from unittest import TestCase

from tst._Utils import *


class TestSupPrototypeFunctionsAst(TestCase):
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
