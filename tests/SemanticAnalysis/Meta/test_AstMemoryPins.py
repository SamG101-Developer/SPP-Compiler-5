from tests._Utils import *


class TestAstMemoryPins(CustomTestCase):
    @should_fail_compilation(SemanticErrors.MemoryMovedWhilstPinnedError)
    def test_invalid_moving_coroutine_with_pins_let(self):
        # Can't move a pinned coroutine (assigning it).
        """
        cor g(a: &std::string::Str) -> std::generator::Gen[std::string::Str, std::boolean::Bool] { }

        fun f() -> std::void::Void {
            let x = "hello world"
            let coroutine = g(&x)
            let c = coroutine
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryMovedWhilstPinnedError)
    def test_invalid_moving_coroutine_with_pins_assign(self):
        # Can't move a pinned coroutine (assigning it).
        """
        cor g(a: &std::string::Str) -> std::generator::Gen[std::string::Str, std::boolean::Bool] { }

        fun f() -> std::void::Void {
            let c: std::generator::Gen[std::string::Str, std::boolean::Bool]
            let x = "hello world"
            let coroutine = g(&x)
            c = coroutine
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryMovedWhilstPinnedError)
    def test_invalid_moving_coroutine_with_pins_ret(self):
        # Can't move a pinned coroutine (returning it).
        """
        cor g(a: &std::string::Str) -> std::generator::Gen[std::string::Str, std::boolean::Bool] { }

        fun f() -> std::generator::Gen[std::string::Str, std::boolean::Bool] {
            let x = "hello world"
            let coroutine = g(&x)
            ret coroutine
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryMovedWhilstPinnedError)
    def test_invalid_assign_to_pin(self):
        # Can't move a pinned coroutine (assigning to it).
        """
        cor g(a: &std::string::Str) -> std::generator::Gen[std::string::Str, std::boolean::Bool] { }

        fun f() -> std::void::Void {
            let c = std::generator::Gen[std::string::Str, std::boolean::Bool]()
            let x = "hello world"
            let mut coroutine = g(&x)
            coroutine = c
        }
        """
