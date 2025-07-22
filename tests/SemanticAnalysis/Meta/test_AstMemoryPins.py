from tests._Utils import *


class TestAstMemoryPins(CustomTestCase):
    @should_fail_compilation(SemanticErrors.MemoryMovedWhilstPinnedError)
    def test_invalid_moving_pinned_borrow_let(self):
        # Can't move a pinned borrow (let statement).
        """
        cor g(a: &std::string::Str) -> std::generator::Gen[std::string::Str, std::boolean::Bool] { }

        fun f() -> std::void::Void {
            let x = "hello world"
            let coroutine = g(&x)
            let y = x
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryMovedWhilstPinnedError)
    def test_invalid_moving_pinned_borrow_assign_variable(self):
        # Can't move a pinned borrow (assignment).
        """
        cor g(a: &std::string::Str) -> std::generator::Gen[std::string::Str, std::boolean::Bool] { }

        fun f() -> std::void::Void {
            let y: std::string::Str
            let x = "hello world"
            let coroutine = g(&x)
            y = x
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryMovedWhilstPinnedError)
    def test_invalid_moving_pinned_borrow_assign_attribute(self):
        # Can't move a pinned borrow (assignment).
        """
        cor g(a: &std::string::Str) -> std::generator::Gen[std::string::Str, std::boolean::Bool] { }

        cls A {
            a: std::string::Str
        }

        fun f(mut a: A) -> std::void::Void {
            let y: std::string::Str
            let x = "hello world"
            let coroutine = g(&x)
            a.a = x
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryMovedWhilstPinnedError)
    def test_invalid_moving_pinned_borrow_func_call(self):
        # Can't move a pinned borrow (function call argument).
        """
        cor g(a: &std::string::Str) -> std::generator::Gen[std::string::Str, std::boolean::Bool] { }

        fun f(x: std::string::Str) -> std::void::Void { }

        fun h() -> std::void::Void {
            let x = "hello world"
            let coroutine = g(&x)
            f(x)
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryMovedWhilstPinnedError)
    def test_invalid_moving_pinned_borrow_object_init(self):
        # Can't move a pinned borrow (object initialization argument).
        """
        cor g(a: &std::string::Str) -> std::generator::Gen[std::string::Str, std::boolean::Bool] { }

        cls A {
            a: std::string::Str
        }

        fun h() -> std::void::Void {
            let x = "hello world"
            let coroutine = g(&x)
            let a = A(a=x)
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryMovedWhilstPinnedError)
    def test_invalid_moving_pinned_borrow_inner_scope_return(self):
        # Can't move a pinned borrow (final statement in a scope).
        """
        cor g(a: &std::string::Str) -> std::generator::Gen[std::string::Str, std::boolean::Bool] { }

        fun h() -> std::void::Void {
            let y = {
                let x = "hello world"
                let coroutine = g(&x)
                x
            }
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryMovedWhilstPinnedError)
    def test_invalid_moving_pinned_borrow_loop_escape(self):
        # Can't move a pinned borrow (escape a loop with exit).
        """
        cor g(a: &std::string::Str) -> std::generator::Gen[std::string::Str, std::boolean::Bool] { }

        fun h() -> std::void::Void {
            loop true {
                let x = "hello world"
                let coroutine = g(&x)
                exit x
            }
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryMovedWhilstPinnedError)
    def test_invalid_moving_pinned_borrow_gen(self):
        # Can't move a pinned borrow (yield out of coroutine). Todo: add "gen with" test once it's implemented.
        """
        cor g(a: &std::string::Str) -> std::generator::Gen[std::string::Str, std::boolean::Bool] { }

        cor h() -> std::generator::Gen[std::string::Str, std::boolean::Bool] {
            let x = "hello world"
            let coroutine = g(&x)
            gen x
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryMovedWhilstLinkPinnedError)
    def test_invalid_moving_pinned_borrow_ret(self):
        # Can't move a pinned borrow (yield out of coroutine).
        """
        cor g(a: &std::string::Str) -> std::generator::Gen[std::string::Str, std::boolean::Bool] { }

        fun h() -> std::generator::Gen[std::string::Str, std::boolean::Bool] {
            let x = "hello world"
            let coroutine = g(&x)
            ret coroutine
        }
        """

    # @should_pass_compilation()
    # def test_valid_moving_coroutine_with_pins_let(self):
    #     # Can move a pinned coroutine in the same scope.
    #     """
    #     cor g(a: &std::string::Str) -> std::generator::Gen[std::string::Str, std::boolean::Bool] { }
    #
    #     fun f() -> std::void::Void {
    #         let x = "hello world"
    #         let coroutine = g(&x)
    #         let c = coroutine
    #     }
    #     """
    #
    # @should_pass_compilation()
    # def test_valid_moving_coroutine_with_pins_assign_variable(self):
    #     # Can move a pinned coroutine in the same scope.
    #     """
    #     cor g(a: &std::string::Str) -> std::generator::Gen[std::string::Str, std::boolean::Bool] { }
    #
    #     fun f() -> std::void::Void {
    #         let c: std::generator::Gen[std::string::Str, std::boolean::Bool]
    #         let x = "hello world"
    #         let coroutine = g(&x)
    #         c = coroutine
    #     }
    #     """
    #
    # @should_pass_compilation()
    # def test_valid_moving_coroutine_with_pins_assign_attribute(self):
    #     # Can move a pinned coroutine in the same scope.
    #     """
    #     cls A {
    #         a: std::generator::Gen[std::string::Str, std::boolean::Bool]
    #     }
    #
    #     cor g(a: &std::string::Str) -> std::generator::Gen[std::string::Str, std::boolean::Bool] { }
    #
    #     fun f() -> std::void::Void {
    #         let mut a = A()
    #         let x = "hello world"
    #         let coroutine = g(&x)
    #         a.a = coroutine
    #     }
    #     """
    #
    # @should_pass_compilation()
    # def test_valid_moving_coroutine_with_pins_func_call(self):
    #     # Can move a pinned coroutine in the same scope.
    #     """
    #     cor g(a: &std::string::Str) -> std::generator::Gen[std::string::Str, std::boolean::Bool] { }
    #
    #     fun f(x: std::generator::Gen[std::string::Str, std::boolean::Bool]) -> std::void::Void { }
    #
    #     fun h() -> std::void::Void {
    #         let x = "hello world"
    #         let coroutine = g(&x)
    #         f(coroutine)
    #     }
    #     """
    #
    # @should_pass_compilation()
    # def test_valid_moving_coroutine_with_pins_object_init(self):
    #     # Can move a pinned coroutine in the same scope.
    #     """
    #     cor g(a: &std::string::Str) -> std::generator::Gen[std::string::Str, std::boolean::Bool] { }
    #
    #     cls A {
    #         a: std::generator::Gen[std::string::Str, std::boolean::Bool]
    #     }
    #
    #     fun h() -> std::void::Void {
    #         let x = "hello world"
    #         let coroutine = g(&x)
    #         let a = A(a=coroutine)
    #     }
    #     """
    #
    # @should_fail_compilation(SemanticErrors.MemoryMovedWhilstLinkPinnedError)
    # def test_invalid_moving_coroutine_with_pins_object_init_then_ret(self):
    #     # Can move a pinned coroutine in the same scope.
    #     """
    #     cor g(a: &std::string::Str) -> std::generator::Gen[std::string::Str, std::boolean::Bool] { }
    #
    #     cls A {
    #         a: std::generator::Gen[std::string::Str, std::boolean::Bool]
    #     }
    #
    #     fun h() -> A {
    #         let x = "hello world"
    #         let coroutine = g(&x)
    #         let a = A(a=coroutine)
    #         ret a
    #     }
    #     """
    #
    # @should_pass_compilation()
    # def test_valid_moving_coroutine_with_pins_inner_scope_return(self):
    #     # Can move a pinned coroutine in the same scope.
    #     """
    #     cor g(a: &std::string::Str) -> std::generator::Gen[std::string::Str, std::boolean::Bool] { }
    #
    #     fun h() -> std::void::Void {
    #         let x = "hello world"
    #         let y = {
    #             let coroutine = g(&x)
    #             coroutine
    #         }
    #     }
    #     """
    #
    # @should_pass_compilation()
    # def test_valid_moving_coroutine_with_pins_loop_escape(self):
    #     # Can move a pinned coroutine in the same scope.
    #     """
    #     cor g(a: &std::string::Str) -> std::generator::Gen[std::string::Str, std::boolean::Bool] { }
    #
    #     fun h() -> std::void::Void {
    #         let x = "hello world"
    #         loop true {
    #             let coroutine = g(&x)
    #             exit coroutine
    #         }
    #     }
    #     """
    #
    # @should_pass_compilation()
    # def test_valid_moving_coroutine_with_pins_gen(self):
    #     # Can move a pinned coroutine in the same scope.
    #     """
    #     cmp x: std::string::Str = "hello world"
    #
    #     cor g(a: &std::string::Str) -> std::generator::Gen[std::string::Str, std::boolean::Bool] { }
    #
    #     cor h() -> std::generator::Gen[std::generator::Gen[std::string::Str, std::boolean::Bool], std::boolean::Bool] {
    #         let coroutine = g(&x)
    #         gen coroutine
    #     }
    #     """
    #
    # @should_pass_compilation()
    # def test_valid_moving_coroutine_with_pins_return(self):
    #     # Can move a pinned coroutine in the same scope.
    #     """
    #     cor g(a: &std::string::Str) -> std::generator::Gen[std::string::Str, std::boolean::Bool] { }
    #
    #     fun h(x: &std::string::Str) -> std::void::Void {
    #         let coroutine = g(x)
    #         ret coroutine
    #     }
    #     """

    @should_fail_compilation(SemanticErrors.MemoryMovedWhilstLinkPinnedError)
    def test_invalid_moving_coroutine_with_pins_assign_attribute(self):
        # Can't extend the lifetime of pin by moving a coroutine into a mutably borrowed type.
        """
        cls A {
            a: std::generator::Gen[std::string::Str, std::boolean::Bool]
        }

        cor g(a: &std::string::Str) -> std::generator::Gen[std::string::Str, std::boolean::Bool] { }

        fun f(a: &mut A) -> std::void::Void {
            let x = "hello world"
            let coroutine = g(&x)
            a.a = coroutine
        }
        """
