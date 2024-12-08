from unittest import TestCase

from tst._Utils import *


class TestAstMemory(TestCase):
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
        cls Point {
            x: std::BigInt
            y: std::BigInt
        }

        fun f(p: &Point) -> std::Void {
            let x = p.x
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryMovedFromBorrowedContextError)
    def test_invalid_memory_moved_from_borrowed_context_2(self):
        """
        cls Point {
            x: std::BigInt
            y: std::BigInt
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
