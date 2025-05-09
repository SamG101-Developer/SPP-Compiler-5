from tests._Utils import *


class TestLocalVariableSingleAst:
    @should_fail_compilation(SemanticErrors.MemoryMovedFromBorrowedContextError)
    def test_invalid_local_variable_set_from_ref_borrowed_then_moved_from(self):
        """
        fun f(a: &std::string::Str) -> std::void::Void {
            let b = a
            let data = b.data
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryMovedFromBorrowedContextError)
    def test_invalid_local_variable_set_from_mut_borrowed_then_moved_from(self):
        """
        fun f(a: &mut std::string::Str) -> std::void::Void {
            let b = a
            let data = b.data
        }
        """
