from unittest import TestCase

from tst._Utils import *


class TestArrayLiteralNElementAst(CustomTestCase):
    @should_pass_compilation()
    def test_valid_array_filled_array_literal(self):
        """
        fun f() -> std::Void {
            let a = [1, 2, 3]
        }
        """

    @should_fail_compilation(SemanticErrors.ExpressionTypeInvalidError)
    def test_invalid_array_filled_array_literal_invalid_element(self):
        """
        fun f() -> std::Void {
            let a = [std::Bool, std::Bool]
        }
        """

    @should_fail_compilation(SemanticErrors.ArrayElementsDifferentTypesError)
    def test_invalid_array_filled_array_different_types(self):
        """
        fun f() -> std::Void {
            let a = [1, false, 3]
        }
        """

    @should_fail_compilation(SemanticErrors.ArrayElementBorrowedError)
    def test_invalid_array_filled_array_borrowed_elements(self):
        """
        fun f(a: &std::BigInt) -> std::Void {
            let a = [a, 2, 3]
        }
        """