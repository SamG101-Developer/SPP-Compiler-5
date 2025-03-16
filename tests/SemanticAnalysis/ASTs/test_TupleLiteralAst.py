from unittest import TestCase

from tests._Utils import *


class TestTupleLiteralNElementAst(CustomTestCase):
    @should_pass_compilation()
    def test_valid_tuple_filled_tuple_literal_size_0(self):
        """
        fun f() -> std::void::Void {
            let a = ()
        }
        """

    @should_pass_compilation()
    def test_valid_tuple_filled_tuple_literal_size_1(self):
        """
        fun f() -> std::void::Void {
            let a = (1,)
        }
        """

    @should_pass_compilation()
    def test_valid_tuple_filled_tuple_literal_size_n(self):
        """
        fun f() -> std::void::Void {
            let a = (1, 2, 3)
        }
        """

    @should_fail_compilation(SemanticErrors.ExpressionTypeInvalidError)
    def test_invalid_tuple_filled_tuple_literal_invalid_element(self):
        """
        fun f() -> std::void::Void {
            let a = (std::boolean::Bool, std::boolean::Bool)
        }
        """

    @should_fail_compilation(SemanticErrors.TupleElementBorrowedError)
    def test_invalid_tuple_filled_tuple_borrowed_elements(self):
        """
        fun f(a: &std::number::BigInt) -> std::void::Void {
            let a = (a, 2, 3)
        }
        """