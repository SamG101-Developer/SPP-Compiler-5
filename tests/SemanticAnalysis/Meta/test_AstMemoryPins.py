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

    @should_fail_compilation(SemanticErrors.MemoryOverlapUsageError)
    def test_invalid_use_ref_borrow_after_mut_borrow_created(self):
        # Can't mutate a borrowed value that is pinned.
        """
        cor g(a: &mut std::string::Str) -> std::generator::Gen[std::string::Str] { }

        fun h(a: &std::string::Str) -> std::void::Void { }

        fun f() -> std::void::Void {
            let mut x = "hello world"
            let coroutine = g(&mut x)
            h(&x)
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryOverlapUsageError)
    def test_invalid_use_mut_borrow_after_mut_borrow_created(self):
        # Can't mutate a borrowed value that is pinned.
        """
        cor g(a: &mut std::string::Str) -> std::generator::Gen[std::string::Str] { }

        fun h(a: &mut std::string::Str) -> std::void::Void { }

        fun f() -> std::void::Void {
            let mut x = "hello world"
            let coroutine = g(&mut x)
            h(&mut x)
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryOverlapUsageError)
    def test_invalid_use_mut_borrow_after_ref_borrow_created(self):
        # Can't mutate a borrowed value that is pinned.
        """
        cor g(a: &std::string::Str) -> std::generator::Gen[std::string::Str] { }

        fun h(a: &mut std::string::Str) -> std::void::Void { }

        fun f() -> std::void::Void {
            let mut x = "hello world"
            let coroutine = g(&x)
            h(&mut x)
        }
        """

    @should_pass_compilation()
    def test_valid_use_ref_borrow_after_ref_borrow_created(self):
        # Can't mutate a borrowed value that is pinned.
        """
        cor g(a: &std::string::Str) -> std::generator::Gen[std::string::Str] { }

        fun h(a: &std::string::Str) -> std::void::Void { }

        fun f() -> std::void::Void {
            let x = "hello world"
            let coroutine = g(&x)
            h(&x)
            coroutine.res()
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryOverlapUsageError)
    def test_invalid_use_mut_borrow_after_ref_borrow_created_complex(self):
        # When yielding a second borrow, the first one should be invalidated.
        """
        cls MyType { }
        sup MyType {
            cor custom_iter_ref(&self) -> std::generator::Gen[&std::string::Str] { }
            cor custom_iter_mut(&mut self) -> std::generator::Gen[&mut std::string::Str] { }
        }

        fun test() -> std::void::Void {
            let mut object = MyType()
            let generator_mut = object.custom_iter_mut()
            let generator_ref = object.custom_iter_ref()
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryOverlapUsageError)
    def test_invalid_use_ref_borrow_after_mut_borrow_created_complex(self):
        # When yielding a second borrow, the first one should be invalidated.
        """
        cls MyType { }
        sup MyType {
            cor custom_iter_ref(&self) -> std::generator::Gen[&std::string::Str] { }
            cor custom_iter_mut(&mut self) -> std::generator::Gen[&mut std::string::Str] { }
        }

        fun test() -> std::void::Void {
            let mut object = MyType()
            let generator_ref = object.custom_iter_ref()
            let generator_mut = object.custom_iter_mut()
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryOverlapUsageError)
    def test_invalid_use_mut_borrow_after_mut_borrow_created_complex(self):
        # When yielding a second borrow, the first one should be invalidated.
        """
        cls MyType { }
        sup MyType {
            cor custom_iter_ref(&self) -> std::generator::Gen[&std::string::Str] { }
            cor custom_iter_mut(&mut self) -> std::generator::Gen[&mut std::string::Str] { }
        }

        fun test() -> std::void::Void {
            let mut object = MyType()
            let generator_mut_1 = object.custom_iter_mut()
            let generator_mut_2 = object.custom_iter_mut()
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryOverlapUsageError)
    def test_invalid_use_borrow_conflict_with_assign_from_inner_scope(self):
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
            loop true {
                generator_mut = object.custom_iter_mut()
            }
            let generator_ref = object.custom_iter_ref()
            generator_mut.res()
        }
        """

    @should_pass_compilation()
    def test_valid_use_borrow_conflict_with_value_discarded_in_inner_scope(self):
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
                let generator_mut = object.custom_iter_mut()
            }
            let generator_ref = object.custom_iter_ref()
            generator_ref.res()
        }
        """
