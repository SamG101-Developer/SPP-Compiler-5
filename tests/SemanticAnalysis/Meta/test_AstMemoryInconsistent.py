from tests._Utils import *


class TestAstMemoryInconsistent(CustomTestCase):
    @should_fail_compilation(SemanticErrors.MemoryInconsistentlyInitializedError)
    def test_invalid_memory_inconsistently_initialized_moved(self):
        # Move an initialized value in one branch and not in the other.
        """
        cls Point {
            x: std::number::bigint::BigInt
            y: std::number::bigint::BigInt
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
            x: std::number::bigint::BigInt
            y: std::number::bigint::BigInt
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
            x: std::number::bigint::BigInt
            y: std::number::bigint::BigInt
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
            x: std::number::bigint::BigInt
            y: std::number::bigint::BigInt
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
            x: std::number::bigint::BigInt
            y: std::number::bigint::BigInt
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
            x: std::number::bigint::BigInt
            y: std::number::bigint::BigInt
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
            x: std::number::bigint::BigInt
            y: std::number::bigint::BigInt
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
            x: std::number::bigint::BigInt
            y: std::number::bigint::BigInt
        }

        cor c(x: &std::number::bigint::BigInt) -> std::generator::Gen[std::boolean::Bool] { }

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
            x: std::number::bigint::BigInt
            y: std::number::bigint::BigInt
        }

        cor c(x: &std::number::bigint::BigInt) -> std::generator::Gen[std::boolean::Bool] { }

        fun f() -> std::void::Void {
            let p = Point(x=5, y=5)
            case 1 of
                == 1 { c(&p.x) }
                == 2 { c(&p.y) }

            let r = p
        }
        """
