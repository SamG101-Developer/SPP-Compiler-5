from tests._Utils import *


class TestUseStatementAst(CustomTestCase):
    @should_pass_compilation()
    def test_valid_use_statement_reduction(self):
        """
        use std::bignum::bigint::BigInt
        use std::string::Str
        use std::option::Opt
        """

    @should_pass_compilation()
    def test_valid_use_statement_reduction_use_generic_1(self):
        """
        use std::vector::Vec

        fun f[T](a: Vec[T]) -> std::void::Void { }
        """

    @should_pass_compilation()
    def test_valid_use_statement_reduction_use_generic_2(self):
        """
        use std::array::Arr
        use std::void::Void
        use std::number::USize

        fun f[T, cmp n: USize](a: Arr[T, n]) -> Void { }
        """
