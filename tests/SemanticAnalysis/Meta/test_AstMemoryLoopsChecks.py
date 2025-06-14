from tests._Utils import *


class TestAstMemoryLoopChecks(CustomTestCase):
    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_invalid_loop_with_memory_move(self):
        """
        fun f() -> std::void::Void {
            let x = "hello world"
            loop true {
                let y = x
            }
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryPartiallyInitializedUsageError)
    def test_invalid_loop_with_memory_move_nested(self):
        """
        fun f() -> std::void::Void {
            let x = "hello world"
            loop true {
                let d = x.data
            }
        }
        """

    @should_pass_compilation()
    def test_valid_loop_with_memory_copy(self):
        """
        fun f() -> std::void::Void {
            let x = 123_u32
            loop true {
                let y = x
            }
        }
        """
