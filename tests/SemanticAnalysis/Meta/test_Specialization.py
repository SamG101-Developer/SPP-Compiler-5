from tests._Utils import *


class TestSpecialization(CustomTestCase):
    @should_pass_compilation()
    def test_specialization_vector_string(self) -> None:
        """
        sup std::vector::Vec[std::string::Str] {
            fun test_func(&self) -> std::bignum::bigint::BigInt {
                ret 1
            }
        }

        use std::vector::Vec
        use std::string::Str

        sup std::bignum::bigint::BigInt {
            fun to_string(&self) -> std::string::Str {
                ret ""
            }
        }

        fun f() -> std::void::Void {
            let mut v = Vec[Str]()
            let mut x = v.test_func()
            x = 1234
            v.push(x.to_string())
        }
        """

    @should_fail_compilation(SemanticErrors.IdentifierUnknownError)
    def test_specialization_failure_different_generic(self) -> None:
        """
        sup std::vector::Vec[std::string::Str] {
            fun test_func(&self) -> std::bignum::bigint::BigInt {
                ret 1
            }
        }

        use std::vector::Vec
        use std::boolean::Bool

        fun f() -> std::void::Void {
            let v = Vec[Bool]()
            let x = v.test_func()
        }
        """

    @should_pass_compilation()
    def test_methods_on_different_generic_names(self) -> None:
        """
        cls MyType[T] {
            a: T
        }

        sup [T] MyType[T] {
            fun test_func_0(self) -> T {
                ret self.a
            }
        }

        sup [U] MyType[U] {
            fun test_func_1(self) -> U {
                ret self.a
            }
        }

        sup std::bignum::bigint::BigInt {
            fun to_string(&self) -> std::string::Str {
                ret ""
            }
        }

        fun f() -> std::void::Void {
            let t = MyType[std::bignum::bigint::BigInt]()
            let a = t.test_func_0()

            let u = MyType[std::string::Str]()
            let mut b = u.test_func_1()

            b = a.to_string()
        }
        """

    # @should_pass_compilation()
    # def test_blanket_specialization(self) -> None:
    #     """
    #     sup [T] T {
    #         fun test_func(&self) -> std::bignum::bigint::BigInt {
    #             ret 1
    #         }
    #     }
    #
    #     fun f() -> std::void::Void {
    #         let x = 1.test_func()
    #     }
    #     """
