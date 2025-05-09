from tests._Utils import *


class AstMemoryMoveFromMutBorrowedCtx(CustomTestCase):
    @should_fail_compilation(SemanticErrors.MemoryMovedFromBorrowedContextError)
    def test_invalid_moved_from_borrowed_context(self):
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
    def test_invalid_moved_from_borrowed_context_with_symbol_alias(self):
        # Create a partial move on a mutable borrow.
        """
        cls T { }

        cls Point {
            x: T
            y: T
        }

        fun f(p: &mut Point) -> std::void::Void {
            let q = p
            let x = q.x
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryMovedFromBorrowedContextError)
    def test_invalid_moved_from_borrowed_context_nested(self):
        # Create a partial move on a mutable borrow.
        """
        cls U { }
        cls T { u: U }

        cls Point {
            x: T
            y: T
        }

        fun f(p: &mut Point) -> std::void::Void {
            let q = p
            let x = q.x.u
        }
        """


class AstMemoryMoveFromRefBorrowedCtx(CustomTestCase):
    @should_fail_compilation(SemanticErrors.MemoryMovedFromBorrowedContextError)
    def test_invalid_moved_from_borrowed_context(self):
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

    @should_fail_compilation(SemanticErrors.MemoryMovedFromBorrowedContextError)
    def test_invalid_moved_from_borrowed_context_with_symbol_alias(self):
        # Create a partial move in an immutable borrow.
        """
        cls T { }

        cls Point {
            x: T
            y: T
        }

        fun f(p: &Point) -> std::void::Void {
            let q = p
            let x = q.x
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryMovedFromBorrowedContextError)
    def test_invalid_moved_from_borrowed_context_nested(self):
        # Create a partial move in an immutable borrow.
        """
        cls U { }
        cls T { u: U }

        cls Point {
            x: T
            y: T
        }

        fun f(p: &Point) -> std::void::Void {
            let q = p
            let x = q.x.u
        }
        """
