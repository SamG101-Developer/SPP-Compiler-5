from tests._Utils import *


class TestAstMemory(CustomTestCase):
    @should_fail_compilation(SemanticErrors.MemoryInconsistentlyInitializedError)
    def test_invalid_memory_inconsistently_initialized_moved(self):
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
    def test_invalid_memory_inconsistently_initialized_partially_initialized_1(self):
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
    def test_invalid_memory_inconsistently_initialized_partially_initialized_2(self):
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
    def test_invalid_memory_inconsistently_initialized_partially_initialized_3(self):
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

    @should_fail_compilation(SemanticErrors.MemoryInconsistentlyPinnedError)
    def test_invalid_memory_inconsistently_pinned_1(self):
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
    def test_invalid_memory_moved_from_borrowed_context_1(self):
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

    @should_fail_compilation(SemanticErrors.MemoryMovedFromBorrowedContextError)
    def test_invalid_memory_moved_from_borrowed_context_2(self):
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

    @should_pass_compilation()
    def test_valid_memory_multiple_partial_moves(self):
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
        """
        fun f() -> std::void::Void {
            let x = 123
            let a = x
            let b = x
        }
        """

    @should_pass_compilation()
    def test_valid_memory_copy_custom(self):
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
    def test_invalid_coroutine_yielded_borrowed_value_use(self):
        """
        cls MyType[T] { }
        sup [T] MyType[T] {
            cor custom_iter_mut(&mut self) -> std::generator::Gen[&mut T, std::boolean::Bool] { }
        }

        fun test() -> std::void::Void {
            let mut g = MyType[std::number::BigInt]()
            let iter = g.custom_iter_mut()
            let x = iter.res(false)
            let y = iter.res(false)
            let z = x + y
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_invalid_coroutine_yielded_borrowed_value_use_2(self):
        """
        cls MyType[T] { }
        sup [T] MyType[T] {
            cor custom_iter_mut(&mut self) -> std::generator::Gen[&mut T, std::boolean::Bool] { }
        }

        fun test() -> std::void::Void {
            let mut g = MyType[std::number::BigInt]()
            let x = g.custom_iter_mut().res(false)
            let y = g.custom_iter_mut().res(false)
            let a = x
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_invalid_mut_borrow_usage_invalidated(self):
        """
        cls MyType {
            x: std::number::BigInt
        }

        sup MyType {
            cor custom_iter_mut(&mut self) -> std::generator::Gen[&mut std::number::BigInt, std::boolean::Bool] { }
        }

        fun f() -> std::void::Void {
            let mut my_type = MyType(x=123)
            let generator1 = my_type.custom_iter_mut()
            let generator2 = my_type.custom_iter_mut()
            let a = generator1.res(false)
        }
        """

    @should_pass_compilation()
    def test_valid_mut_borrow_usage_invalidated(self):
        """
        cls MyType {
            x: std::number::BigInt
        }

        sup MyType {
            cor custom_iter_mut(&mut self) -> std::generator::Gen[&mut std::number::BigInt, std::boolean::Bool] { }
        }

        fun f() -> std::void::Void {
            let mut my_type = MyType(x=123)
            let generator1 = my_type.custom_iter_mut()
            let generator2 = my_type.custom_iter_mut()
            let a = generator2.res(false)
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
            let a = generator2.res(false)
        }
        """
