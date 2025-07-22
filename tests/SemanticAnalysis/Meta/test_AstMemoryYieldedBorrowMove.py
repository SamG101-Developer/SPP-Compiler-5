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
            let mut generator = g()
            let a = generator.res()
            let b = iter a of
                value { value.a }
                !! { "nothing" }
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
            let mut generator = g()
            let b = iter generator.res() of
                value { value.a }
                !! { "nothing" }
        }
        """
