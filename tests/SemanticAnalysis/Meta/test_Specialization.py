from tests._Utils import *


class TestSpecialization(CustomTestCase):
    @should_pass_compilation()
    def test_specialization_vector_string(self) -> None:
        """
        sup std::vector::Vec[std::string::Str] {
            fun test_func(&self) -> std::number::bigint::BigInt {
                ret 1
            }
        }

        use std::vector::Vec
        use std::string::Str

        sup std::number::bigint::BigInt {
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
    def test_specialization_vector_bool_for_vector_string(self) -> None:
        """
        sup std::vector::Vec[std::string::Str] {
            fun test_func(&self) -> std::number::bigint::BigInt {
                ret 1
            }
        }

        use std::vector::Vec
        use std::boolean::Bool

        fun f() -> std::void::Void {
            let v = Vec[Bool]()
            let mut x = v.test_func()
            x = 1234
        }
        """

    # @should_pass_compilation()
    # def test_blanket_specialization(self) -> None:
    #     """
    #     sup [T] T {
    #         fun test_func(&self) -> std::number::bigint::BigInt {
    #             ret 1
    #         }
    #     }
    #
    #     fun f() -> std::void::Void {
    #         let x = 1.test_func()
    #     }
    #     """
