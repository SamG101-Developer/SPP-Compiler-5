from tests._Utils import *


class TestGenericArgumentGroupAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.IdentifierDuplicationError)
    def test_invalid_generic_argument_group_duplicate_named_argument(self):
        """
        fun f[T, U]() -> std::void::Void { }

        fun g() -> std::void::Void {
            f[T=std::boolean::Bool, T=std::boolean::Bool]()
        }
        """

    @should_fail_compilation(SemanticErrors.OrderInvalidError)
    def test_invalid_generic_argument_group_invalid_argument_order(self):
        """
        fun f[T, U]() -> std::void::Void { }

        fun g() -> std::void::Void {
            f[T=std::boolean::Bool, std::boolean::Bool]()
        }
        """

    @should_pass_compilation()
    def test_valid_generic_argument_group_different_names_from_sup_1(self):
        """
        cls A[T] { a: T }

        sup [T] A[T] {
            fun f(&self) -> std::void::Void { }
        }

        fun g() -> std::void::Void {
            let a = A(a=5)
            a.f()
        }
        """

    @should_pass_compilation()
    def test_valid_generic_argument_group_different_names_from_sup_2(self):
        """
        cls A[T] { a: T }
        sup [T] A[T] {
            fun new(&self) -> A[T] { ret A[T]() }
        }

        sup [T] A[T] {
            fun f(&self) -> T { ret self.new().a }
        }

        fun g() -> std::void::Void {
            let a = A(a=5)
            let mut b = a.f()
            b = a.a
        }
        """
