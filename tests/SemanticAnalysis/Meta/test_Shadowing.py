from tests._Utils import *


class TestShadowing(CustomTestCase):
    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_shadow_create_inner_doesnt_use_outer(self):
        """
        use std::void::Void
        use std::boolean::Bool

        fun f() -> Void {
            let x: Bool
            loop true {
                let x = false
            }
            let y = x
        }
        """

    @should_pass_compilation()
    def test_shadow_use_inner_uses_outer(self):
        """
        use std::void::Void
        use std::boolean::Bool

        fun f() -> Void {
            let x: Bool
            loop true {
                x = false
            }
            let y = x
        }
        """
