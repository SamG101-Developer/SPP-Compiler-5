from tests._Utils import *


class TestTupleSuperimpositions(CustomTestCase):
    @should_pass_compilation()
    def test_tuple_superimposition_any_3_tuple(self):
        """
        use std::number::u16::U16
        use std::number::u32::U32
        use std::number::u64::U64
        use std::void::Void

        sup [T, U, V] std::tuple::Tup[T, U, V] {
            fun f(&self) -> Void { }
        }

        fun f() -> Void {
            let t = (1_u64, 2_u32, 3_u16)
            t.f()
        }
        """

    @should_fail_compilation(SemanticErrors.IdentifierUnknownError)
    def test_tuple_superimposition_wrong_number_elems_1(self):
        """
        use std::number::u32::U32
        use std::number::u64::U64
        use std::void::Void

        sup [T, U, V] std::tuple::Tup[T, U, V] {
            fun f(&self) -> Void { }
        }

        fun f() -> Void {
            let t = (1_u64, 2_u32)
            t.f()
        }
        """

    @should_fail_compilation(SemanticErrors.IdentifierUnknownError)
    def test_tuple_superimposition_wrong_number_elems_2(self):
        """
        use std::number::u16::U16
        use std::number::u32::U32
        use std::number::u64::U64
        use std::void::Void

        sup [T, U] std::tuple::Tup[T, U] {
            fun f(&self) -> Void { }
        }

        fun f() -> Void {
            let t = (1_u64, 2_u32, 3_u16)
            t.f()
        }
        """

    @should_fail_compilation(SemanticErrors.IdentifierUnknownError)
    def test_tuple_superimposition_specific_3_tuple_mismatch_types(self):
        """
        use std::number::u16::U16
        use std::number::u32::U32
        use std::number::u64::U64
        use std::void::Void

        sup std::tuple::Tup[U64, U32, U16] {
            fun f(&self) -> Void { }
        }

        fun f() -> Void {
            let t = (1_u64, 2_u64, 3_u64)
            t.f()
        }
        """

    @should_pass_compilation()
    def test_tuple_superimposition_specific_3_tuple_correct_types(self):
        """
        use std::number::u16::U16
        use std::number::u32::U32
        use std::number::u64::U64
        use std::void::Void

        sup std::tuple::Tup[U64, U32, U16] {
            fun f(&self) -> Void { }
        }

        fun f() -> Void {
            let t = (1_u64, 2_u32, 3_u16)
            t.f()
        }
        """

    @should_pass_compilation()
    def test_tuple_superimposition_specific_and_generic_3_tuple_correct_types(self):
        """
        use std::number::u16::U16
        use std::number::u32::U32
        use std::number::u64::U64
        use std::void::Void

        sup [P, Q] std::tuple::Tup[U64, P, Q] {
            fun f(&self) -> Void { }
        }

        fun f() -> Void {
            let t = (1_u64, "hello", false)
            t.f()
        }
        """
