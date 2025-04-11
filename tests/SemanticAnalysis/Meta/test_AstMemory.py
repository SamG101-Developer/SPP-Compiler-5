from tests._Utils import *


class TestAstMemory(CustomTestCase):
    @should_fail_compilation(SemanticErrors.MemoryInconsistentlyInitializedError)
    def test_invalid_memory_inconsistently_initialized_moved(self):
        # Move an initialized  value in one branch and not in the other.
        """
        cls Point {
            x: std::number::BigInt
            y: std::number::BigInt
        }

        fun f() -> std::void::Void {
            let p = Point(x=5, y=5)

            case 1 of
                == 1 { let r = p }
                == 2 { }

            let r = p
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryInconsistentlyInitializedError)
    def test_invalid_memory_inconsistently_initialized_initialized(self):
        # Initialize a non-initialized value in one branch and not in the other.
        """
        cls Point {
            x: std::number::BigInt
            y: std::number::BigInt
        }

        fun f() -> std::void::Void {
            let p: Point
            case 1 of
                == 1 { p = Point(x=5, y=6) }
                == 2 { }

            let r = p
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryInconsistentlyInitializedError)
    def test_invalid_memory_inconsistently_initialized_partially_moved_1(self):
        # Partially move an initialized value in one branch and not in the other.
        """
        cls Point {
            x: std::number::BigInt
            y: std::number::BigInt
        }

        fun f() -> std::void::Void {
            let p = Point(x=5, y=6)
            case 1 of
                == 1 { let x = p.x }
                == 2 { }

            let r = p
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryInconsistentlyInitializedError)
    def test_invalid_memory_inconsistently_initialized_partially_moved_2(self):
        # Partially move different parts of an initialized value in both branches.
        """
        cls Point {
            x: std::number::BigInt
            y: std::number::BigInt
        }

        fun f() -> std::void::Void {
            let p = Point(x=5, y=6)
            case 1 of
                == 1 { let x = p.x }
                == 2 { let y = p.y }

            let r = p
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryInconsistentlyInitializedError)
    def test_invalid_memory_inconsistently_initialized_partially_initialized_1(self):
        # Partially initialize different parts of a partially initialized value in one branch and not the other.
        """
        cls Point {
            x: std::number::BigInt
            y: std::number::BigInt
        }

        fun f() -> std::void::Void {
            let mut p = Point(x=5, y=6)
            let x = p.x

            case 1 of
                == 1 { p.x = 123 }
                == 2 { }

            let r = p
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryInconsistentlyInitializedError)
    def test_invalid_memory_inconsistently_initialized_partially_initialized_2(self):
        # Partially initialize different parts of a partially initialized value in both branches.
        """
        cls Point {
            x: std::number::BigInt
            y: std::number::BigInt
        }

        fun f() -> std::void::Void {
            let mut p = Point(x=5, y=6)
            let x = p.x
            let y = p.y

            case 1 of
                == 1 { p.x = 123 }
                == 2 { p.y = 456 }

            let r = p
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryInconsistentlyPinnedError)
    def test_invalid_memory_inconsistently_pinned_1(self):
        # Cause a value to be pinned in one branch and not in the other.
        """
        cls Point {
            x: std::number::BigInt
            y: std::number::BigInt
        }

        cor c(p: &Point) -> std::generator::Gen[std::boolean::Bool] { }

        fun f() -> std::void::Void {
            let p = Point(x=5, y=5)
            case 1 of
                == 1 { c(&p) }
                == 2 { }

            let r = p
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryInconsistentlyPinnedError)
    def test_invalid_memory_inconsistently_pinned_2(self):
        # Cause part of a value to be pinned in one branch and not in the other.
        """
        cls Point {
            x: std::number::BigInt
            y: std::number::BigInt
        }

        cor c(x: &std::number::BigInt) -> std::generator::Gen[std::boolean::Bool] { }

        fun f() -> std::void::Void {
            let p = Point(x=5, y=5)
            case 1 of
                == 1 { c(&p.x) }
                == 2 { }

            let r = p
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryInconsistentlyPinnedError)
    def test_invalid_memory_inconsistently_pinned_3(self):
        # Cause different parts of a value to be pinned in both branches.
        """
        cls Point {
            x: std::number::BigInt
            y: std::number::BigInt
        }

        cor c(x: &std::number::BigInt) -> std::generator::Gen[std::boolean::Bool] { }

        fun f() -> std::void::Void {
            let p = Point(x=5, y=5)
            case 1 of
                == 1 { c(&p.x) }
                == 2 { c(&p.y) }

            let r = p
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_invalid_memory_not_initialized_usage_1(self):
        # Use a non-initialized value (never given a value / use-after-free).
        """
        cls Point {
            x: std::number::BigInt
            y: std::number::BigInt
        }

        fun f() -> std::void::Void {
            let p: Point
            let q = p
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_invalid_memory_not_initialized_usage_2(self):
        # Use a non-initialized value (value has been moved already / double-free).
        """
        cls Point {
            x: std::number::BigInt
            y: std::number::BigInt
        }

        fun f() -> std::void::Void {
            let p = Point(x=5, y=5)
            let q = p
            let r = p
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_invalid_memory_not_initialized_usage_3(self):
        # Use part of a non-initialized value (never given a value / use-after-free).
        """
        cls Point {
            x: std::number::BigInt
            y: std::number::BigInt
        }

        fun f() -> std::void::Void {
            let p: Point
            let x = p.x
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_invalid_memory_not_initialized_usage_4(self):
        # Use part of a non-initialized value (value has been moved already / double-free).
        """
        cls Point {
            x: std::number::BigInt
            y: std::number::BigInt
        }

        fun f() -> std::void::Void {
            let p = Point(x=5, y=5)
            let q = p
            let x = p.x
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_invalid_memory_partially_initialized_usage_1(self):
        # Use part of a partially-initialized value (value has been moved already / double-free).
        """
        cls Point {
            x: std::number::BigInt
            y: std::number::BigInt
        }

        fun f() -> std::void::Void {
            let p = Point(x=5, y=5)
            let x1 = p.x
            let x2 = p.x
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryPartiallyInitializedUsageError)
    def test_invalid_memory_partially_initialized_usage_2(self):
        # Use a value that has been partially moved.
        """
        cls Point {
            x: std::number::BigInt
            y: std::number::BigInt
        }

        fun f() -> std::void::Void {
            let p = Point(x=5, y=5)
            let x = p.x
            let q = p
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryMovedFromBorrowedContextError)
    def test_invalid_memory_moved_from_borrowed_context_mut(self):
        # Create a partial move on a mutable borrow.
        """
        cls T { }

        cls Point {
            x: T
            y: T
        }

        fun f(p: &mut Point) -> std::void::Void {
            let x = p.x
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryMovedFromBorrowedContextError)
    def test_invalid_memory_moved_from_borrowed_context_ref(self):
        # Create a partial move in an immutable borrow.
        """
        cls T { }

        cls Point {
            x: T
            y: T
        }

        fun f(p: &Point) -> std::void::Void {
            let x = p.x
        }
        """

    @should_pass_compilation()
    def test_valid_memory_multiple_partial_moves(self):
        # Move different parts of a value over multiple expressions.
        """
        cls Point {
            x: std::number::BigInt
            y: std::number::BigInt
        }

        fun f() -> std::void::Void {
            let p = Point(x=5, y=5)
            let x = p.x
            let y = p.y
        }
        """

    @should_pass_compilation()
    def test_valid_memory_copy(self):
        # Perform a "double move" when the compiler superimposes Copy over the type.
        """
        fun f() -> std::void::Void {
            let x = 123
            let a = x
            let b = x
        }
        """

    @should_pass_compilation()
    def test_valid_memory_copy_custom(self):
        # Perform a "double move" when the use superimposes Copy over the type.
        """
        cls Point {
            x: std::number::BigInt
            y: std::number::BigInt
        }

        sup Point ext std::copy::Copy { }

        fun f() -> std::void::Void {
            let p = Point(x=5, y=5)
            let a = p
            let b = p
        }
        """

    @should_pass_compilation()
    def test_valid_memory_copy_custom_generic(self):
        # Perform a "double move" when the use superimposes Copy over the generic type.
        """
        cls Point[T] {
            x: T
            y: T
        }

        sup [T] Point[T] ext std::copy::Copy { }

        fun f() -> std::void::Void {
            let p = Point(x=5, y=5)
            let a = p
            let b = p
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_invalid_borrow_invalidated_by_next_borrow_1(self):
        # When yielding a second borrow, the first one should be invalidated.
        """
        cls MyType { }
        sup MyType {
            cor custom_iter_mut(&mut self) -> std::generator::Gen[&mut std::string::Str, std::boolean::Bool] { }
        }

        fun test() -> std::void::Void {
            let mut object = MyType()
            let generator = object.custom_iter_mut()
            let borrow1 = generator.resume(false)
            let borrow2 = generator.resume(false)
            let value = borrow1
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_invalid_borrow_invalidated_by_next_borrow_2(self):
        # When yielding a second borrow, the first one should be invalidated.
        """
        cls MyType { }
        sup MyType {
            cor custom_iter_ref(&self) -> std::generator::Gen[&std::string::Str, std::boolean::Bool] { }
            cor custom_iter_mut(&mut self) -> std::generator::Gen[&mut std::string::Str, std::boolean::Bool] { }
        }

        fun test() -> std::void::Void {
            let mut object = MyType()
            let generator_mut = object.custom_iter_mut()
            let borrow1 = generator_mut.resume(false)
            let generator_ref = object.custom_iter_ref()
            let borrow2 = generator_ref.resume(false)
            let value = borrow1
        }
        """

    @should_pass_compilation()
    def test_valid_ref_borrow_usage_invalidated(self):
        """
        cls MyType {
            x: std::number::BigInt
        }

        sup MyType {
            cor custom_iter_ref(&self) -> std::generator::Gen[&std::number::BigInt, std::boolean::Bool] { }
        }

        fun f() -> std::void::Void {
            let my_type = MyType(x=123)
            let generator1 = my_type.custom_iter_ref()
            let generator2 = my_type.custom_iter_ref()
            let a = generator2.resume(false)
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryMovedWhilstPinnedError)
    def test_invalid_moving_coroutine_with_pins_mov(self):
        """
        cor g(a: &std::string::Str) -> std::generator::Gen[std::string::Str, std::boolean::Bool] { }

        fun f() -> std::void::Void {
            let x = "hello world"
            let coroutine = g(&x)
            let c = coroutine
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryMovedWhilstPinnedError)
    def test_invalid_moving_coroutine_with_pins_ret(self):
        """
        cor g(a: &std::string::Str) -> std::generator::Gen[std::string::Str, std::boolean::Bool] { }

        fun f() -> std::generator::Gen[std::string::Str, std::boolean::Bool] {
            let x = "hello world"
            let coroutine = g(&x)
            ret coroutine
        }
        """
