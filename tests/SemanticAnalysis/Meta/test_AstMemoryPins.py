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

    @should_fail_compilation(SemanticErrors.MemoryOverlapUsageError)
    def test_invalid_mut_borrow_to_a_pin(self):
        # Can't mutate a borrowed value that is pinned.
        """
        cor g(a: &std::string::Str) -> std::generator::Gen[std::string::Str, std::boolean::Bool] { }

        fun h(a: &mut std::string::Str) -> std::void::Void { }

        fun f() -> std::void::Void {
            let mut x = "hello world"
            let coroutine = g(&x)
            h(&mut x)
        }
        """

    @should_pass_compilation()
    def test_valid_ref_borrow_to_a_pin(self):
        # Can't mutate a borrowed value that is pinned.
        """
        cor g(a: &std::string::Str) -> std::generator::Gen[std::string::Str, std::boolean::Bool] { }

        fun h(a: &std::string::Str) -> std::void::Void { }

        fun f() -> std::void::Void {
            let x = "hello world"
            let coroutine = g(&x)
            h(&x)
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryMovedWhilstPinnedError)
    def test_invalid_assign_to_pin(self):
        # Can't move a pinned coroutine (assigning it).
        """
        cor g(a: &std::string::Str) -> std::generator::Gen[std::string::Str, std::boolean::Bool] { }

        fun f() -> std::void::Void {
            let c = std::generator::Gen[std::string::Str, std::boolean::Bool]()
            let x = "hello world"
            let mut coroutine = g(&x)
            coroutine = c
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryOverlapUsageError)
    def test_invalid_extended_borrow_mut_ref_conflict(self):
        # When yielding a second borrow, the first one should be invalidated.
        """
        cls MyType { }
        sup MyType {
            cor custom_iter_ref(&self) -> std::generator::Gen[&std::string::Str, std::void::Void] { }
            cor custom_iter_mut(&mut self) -> std::generator::Gen[&mut std::string::Str, std::void::Void] { }
        }

        fun test() -> std::void::Void {
            let mut object = MyType()
            let generator_mut = object.custom_iter_mut()  # borrow held onto here
            let generator_ref = object.custom_iter_ref()
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryOverlapUsageError)
    def test_invalid_extended_borrow_mut_ref_conflict_with_scoping(self):
        # When yielding a second borrow, the first one should be invalidated.
        """
        cls MyType { }
        sup MyType {
            cor custom_iter_ref(&self) -> std::generator::Gen[&std::string::Str, std::void::Void] { }
            cor custom_iter_mut(&mut self) -> std::generator::Gen[&mut std::string::Str, std::void::Void] { }
        }

        fun test() -> std::void::Void {
            let mut object = MyType()
            let generator_mut: std::generator::Gen[&mut std::string::Str, std::void::Void]
            {
                generator_mut = object.custom_iter_mut()  # borrow held onto here
            }
            let generator_ref = object.custom_iter_ref()
        }
        """

    @should_pass_compilation()
    def test_valid_extended_borrow_mut_ref_with_scope_bound(self):
        # When yielding a second borrow, the first one should be invalidated.
        """
        cls MyType { }
        sup MyType {
            cor custom_iter_ref(&self) -> std::generator::Gen[&std::string::Str, std::void::Void] { }
            cor custom_iter_mut(&mut self) -> std::generator::Gen[&mut std::string::Str, std::void::Void] { }
        }

        fun test() -> std::void::Void {
            let mut object = MyType()
            loop true {
                let generator_mut = object.custom_iter_mut()  # borrow held onto here
            }
            let generator_ref = object.custom_iter_ref()
        }
        """
