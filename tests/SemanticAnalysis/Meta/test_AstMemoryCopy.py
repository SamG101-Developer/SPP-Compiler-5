from tests._Utils import *


class TestAstMemoryCopy(CustomTestCase):
    @should_pass_compilation()
    def test_valid_memory_copy(self):
        # Perform a "double move" when the compiler superimposes Copy over the type.
        """
        fun f() -> std::void::Void {
            let x = 123_uz
            let a = x
            let b = x
        }
        """

    @should_pass_compilation()
    def test_valid_memory_copy_custom_type(self):
        # Perform a "double move" when the use superimposes Copy over the type.
        """
        cls Point {
            x: std::bignum::bigint::BigInt
            y: std::bignum::bigint::BigInt
        }

        sup Point ext std::copy::Copy { }

        fun f() -> std::void::Void {
            let p = Point(x=5, y=5)
            let a = p
            let b = p
        }
        """

    @should_pass_compilation()
    def test_valid_memory_copy_custom_generic_type(self):
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
