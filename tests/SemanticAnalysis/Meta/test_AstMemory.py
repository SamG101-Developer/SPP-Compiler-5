from unittest import TestCase

from tests._Utils import *


class TestAstMemory(CustomTestCase):
    @should_fail_compilation(SemanticErrors.MemoryInconsistentlyInitializedError)
    def test_invalid_memory_inconsistently_initialized_moved(self):
        """
        cls Point {
            x: std::BigInt
            y: std::BigInt
        }

        fun f() -> std::Void {
            let p = Point(x=5, y=5)

            case 1 of
                == 1 { let r = p }
                == 2 { }

            let r = p
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryInconsistentlyInitializedError)
    def test_invalid_memory_inconsistently_initialized_initialized(self):
        """
        cls Point {
            x: std::BigInt
            y: std::BigInt
        }

        fun f() -> std::Void {
            let p: Point
            case 1 of
                == 1 { p = Point(x=5, y=6) }
                == 2 { }

            let r = p
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryInconsistentlyInitializedError)
    def test_invalid_memory_inconsistently_initialized_partially_initialized_1(self):
        """
        cls Point {
            x: std::BigInt
            y: std::BigInt
        }

        fun f() -> std::Void {
            let p = Point(x=5, y=6)
            case 1 of
                == 1 { let x = p.x }
                == 2 { }

            let r = p
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryInconsistentlyInitializedError)
    def test_invalid_memory_inconsistently_initialized_partially_initialized_2(self):
        """
        cls Point {
            x: std::BigInt
            y: std::BigInt
        }

        fun f() -> std::Void {
            let p = Point(x=5, y=6)
            case 1 of
                == 1 { let x = p.x }
                == 2 { let y = p.y }

            let r = p
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryInconsistentlyInitializedError)
    def test_invalid_memory_inconsistently_initialized_partially_initialized_3(self):
        """
        cls Point {
            x: std::BigInt
            y: std::BigInt
        }

        fun f() -> std::Void {
            let mut p = Point(x=5, y=6)
            let x = p.x

            case 1 of
                == 1 { p.x = 123 }
                == 2 { }

            let r = p
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryInconsistentlyPinnedError)
    def test_invalid_memory_inconsistently_pinned_1(self):
        """
        cls Point {
            x: std::BigInt
            y: std::BigInt
        }

        fun f() -> std::Void {
            let p = Point(x=5, y=5)
            case 1 of
                == 1 { pin p }
                == 2 { }

            let r = p
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryInconsistentlyPinnedError)
    def test_invalid_memory_inconsistently_pinned_2(self):
        """
        cls Point {
            x: std::BigInt
            y: std::BigInt
        }

        fun f() -> std::Void {
            let p = Point(x=5, y=5)
            case 1 of
                == 1 { pin p.x }
                == 2 { }

            let r = p
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryInconsistentlyPinnedError)
    def test_invalid_memory_inconsistently_pinned_3(self):
        """
        cls Point {
            x: std::BigInt
            y: std::BigInt
        }

        fun f() -> std::Void {
            let p = Point(x=5, y=5)
            case 1 of
                == 1 { pin p.x }
                == 2 { pin p.y }

            let r = p
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryInconsistentlyPinnedError)
    def test_invalid_memory_inconsistently_pinned_4(self):
        """
        cls Point {
            x: std::BigInt
            y: std::BigInt
        }

        fun f() -> std::Void {
            let p = Point(x=5, y=5)
            pin p
            case 1 of
                == 1 { rel p }
                == 2 { }

            let r = p
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryInconsistentlyPinnedError)
    def test_invalid_memory_inconsistently_pinned_5(self):
        """
        cls Point {
            x: std::BigInt
            y: std::BigInt
        }

        fun f() -> std::Void {
            let p = Point(x=5, y=5)
            pin p.x, p.y
            case 1 of
                == 1 { rel p.x }
                == 2 { }

            let r = p
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryInconsistentlyPinnedError)
    def test_invalid_memory_inconsistently_pinned_1(self):
        """
        cls Point {
            x: std::BigInt
            y: std::BigInt
        }

        fun f() -> std::Void {
            let p = Point(x=5, y=5)
            pin p.x, p.y
            case 1 of
                == 1 { rel p.x }
                == 2 { rel p.y }

            let r = p
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_invalid_memory_not_initialized_usage_1(self):
        """
        cls Point {
            x: std::BigInt
            y: std::BigInt
        }

        fun f() -> std::Void {
            let p: Point
            let q = p
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_invalid_memory_not_initialized_usage_2(self):
        """
        cls Point {
            x: std::BigInt
            y: std::BigInt
        }

        fun f() -> std::Void {
            let p = Point(x=5, y=5)
            let q = p
            let r = p
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_invalid_memory_not_initialized_usage_3(self):
        """
        cls Point {
            x: std::BigInt
            y: std::BigInt
        }

        fun f() -> std::Void {
            let p = Point(x=5, y=5)
            let q = p
            let x = p.x
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_invalid_memory_partially_initialized_usage_1(self):
        """
        cls Point {
            x: std::BigInt
            y: std::BigInt
        }

        fun f() -> std::Void {
            let p = Point(x=5, y=5)
            let x1 = p.x
            let x2 = p.x
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryPartiallyInitializedUsageError)
    def test_invalid_memory_partially_initialized_usage_2(self):
        """
        cls Point {
            x: std::BigInt
            y: std::BigInt
        }

        fun f() -> std::Void {
            let p = Point(x=5, y=5)
            let x = p.x
            let q = p
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryMovedFromBorrowedContextError)
    def test_invalid_memory_moved_from_borrowed_context_1(self):
        """
        cls T { }

        cls Point {
            x: T
            y: T
        }

        fun f(p: &Point) -> std::Void {
            let x = p.x
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryMovedFromBorrowedContextError)
    def test_invalid_memory_moved_from_borrowed_context_2(self):
        """
        cls T { }

        cls Point {
            x: T
            y: T
        }

        fun f(p: &mut Point) -> std::Void {
            let x = p.x
        }
        """

    @should_pass_compilation()
    def test_valid_memory_multiple_partial_moves(self):
        """
        cls Point {
            x: std::BigInt
            y: std::BigInt
        }

        fun f() -> std::Void {
            let p = Point(x=5, y=5)
            let x = p.x
            let y = p.y
        }
        """

    @should_pass_compilation()
    def test_valid_memory_copy(self):
        """
        fun f() -> std::Void {
            let x = 123
            let a = x
            let b = x
        }
        """

    @should_pass_compilation()
    def test_valid_memory_copy_custom(self):
        """
        cls Point {
            x: std::BigInt
            y: std::BigInt
        }

        sup Point ext std::Copy { }

        fun f() -> std::Void {
            let p = Point(x=5, y=5)
            let a = p
            let b = p
        }
        """

    @should_pass_compilation()
    def test_valid_memory_copy_custom_generic(self):
        """
        cls Point[T] {
            x: T
            y: T
        }

        sup [T] Point[T] ext std::Copy { }

        fun f() -> std::Void {
            let p = Point(x=5, y=5)
            let a = p
            let b = p
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryUsageOfUnpinnedBorrowError)
    def test_invalid_unpinned_values_for_coroutine(self):
        """
        cor foo(x: &std::BigInt) -> std::GenRef[std::BigInt] {
            gen &1
        }

        fun test() -> std::Void {
            let x = 123
            foo(&x)
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryUsageOfUnpinnedBorrowError)
    def test_invalid_unpinned_values_for_async(self):
        """
        fun foo(x: &std::BigInt) -> std::Void {
        }

        fun test() -> std::Void {
            let x = 123
            async foo(&x)
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_invalid_coroutine_yielded_value_use(self):
        """
        cor foo() -> std::GenRef[std::BigInt] {
            gen &1
        }

        fun test() -> std::Void {
            let coro = foo()
            let x = coro.step
            let y = coro.step
            let z = x + y
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_invalid_use_of_moving_coro_during_pin_from_pinned_borrow(self):
        """
        cor foo(x: &std::BigInt) -> std::GenRef[std::BigInt] {
            gen &1
        }

        fun test() -> std::Void {
            let x = 1
            pin x
            let coro = foo(&x)
            let y = coro
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_invalid_use_of_coroutine_post_invalidation(self):
        """
        cor foo(x: &std::BigInt) -> std::GenRef[std::BigInt] {
            gen &1
        }

        fun test() -> std::Void {
            let x = 1
            pin x
            let coro = foo(&x)
            rel x
            let y = coro.step
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_invalid_use_of_future_post_invalidation(self):
        """
        fun foo(x: &std::BigInt) -> std::Void {
        }

        fun test() -> std::Void {
            let x = 1
            pin x
            let fut = async foo(&x)
            rel x
            let y = fut
        }
        """

    @should_pass_compilation()
    def test_valid_pinned_values_for_coroutine(self):
        """
        cor foo(x: &std::BigInt) -> std::GenRef[std::BigInt] {
            gen &1
        }

        fun test() -> std::Void {
            let x = 123
            pin x
            foo(&x)
        }
        """

    @should_pass_compilation()
    def test_valid_pinned_values_for_async(self):
        """
        fun foo(x: &std::BigInt) -> std::Void {
        }

        fun test() -> std::Void {
            let x = 123
            pin x
            async foo(&x)
        }
        """
