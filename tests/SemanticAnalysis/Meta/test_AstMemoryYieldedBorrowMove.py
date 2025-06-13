from tests._Utils import *


class TestAstYieldedBorrowMove(CustomTestCase):
    @should_fail_compilation(SemanticErrors.MemoryMovedFromBorrowedContextError)
    def test_invalid_partial_move_from_yielded_borrow_via_variable(self):
        """
        cls A {
            a: std::string::Str
        }

        cor g() -> std::generator::Gen[&A] { }

        fun f() -> std::void::Void {
            let generator = g()
            let a = generator.res()
            let b = a.a
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryMovedFromBorrowedContextError)
    def test_invalid_partial_move_from_yielded_borrow_directly(self):
        """
        cls A {
            a: std::string::Str
        }

        cor g() -> std::generator::Gen[&A] { }

        fun f() -> std::void::Void {
            let generator = g()
            let a = generator.res().a
        }
        """
