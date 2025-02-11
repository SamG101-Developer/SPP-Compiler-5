from unittest import TestCase

from tst._Utils import *


class TestGenericArgumentGroupAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.IdentifierDuplicationError)
    def test_invalid_generic_argument_group_duplicate_named_argument(self):
        """
        fun f[T, U]() -> std::Void { }

        fun g() -> std::Void {
            f[T=std::Bool, T=std::Bool]()
        }
        """

    @should_fail_compilation(SemanticErrors.OrderInvalidError)
    def test_invalid_generic_argument_group_invalid_argument_order(self):
        """
        fun f[T, U]() -> std::Void { }

        fun g() -> std::Void {
            f[T=std::Bool, std::Bool]()
        }
        """

    @should_pass_compilation()
    def test_valid_generic_argument_group_different_names_from_sup_1(self):
        """
        cls A[T] { a: T }

        sup [T] A[T] {
            fun f(&self) -> std::Void { }
        }

        fun g() -> std::Void {
            let a = A(a=5)
            a.f()
        }
        """

    @should_pass_compilation()
    def test_valid_generic_argument_group_different_names_from_sup_2(self):
        """
        cls A[T] { a: T }

        sup [T] A[T] {
            fun f(&self) -> T { ret self.a }
        }

        fun g() -> std::Void {
            let a = A(a=5)
            let mut b = a.f()
            b = a.a
        }
        """
