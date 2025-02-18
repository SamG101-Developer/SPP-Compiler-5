from unittest import TestCase

from tests._Utils import *


class TestLocalVariableDestructureTupleAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_local_variable_destructure_tuple_non_tuple(self):
        """
        fun f() -> std::Void {
            let (a, b) = 1
        }
        """

    @should_fail_compilation(SemanticErrors.VariableDestructureContainsMultipleMultiSkipsError)
    def test_invalid_local_variable_destructure_tuple_multiple_multi_skip(self):
        """
        fun f() -> std::Void {
            let (a, .., .., b) = (1, 2, 3, 4)
        }
        """

    @should_fail_compilation(SemanticErrors.VariableTupleDestructureTupleSizeMismatchError)
    def test_invalid_local_variable_destructure_tuple_missing_element(self):
        """
        fun f() -> std::Void {
            let (a, b) = (1, 2, 3)
        }
        """

    @should_fail_compilation(SemanticErrors.VariableTupleDestructureTupleSizeMismatchError)
    def test_invalid_local_variable_destructure_tuple_invalid_element(self):
        """
        fun f() -> std::Void {
            let (a, b, c) = (1, 2)
        }
        """

    @should_pass_compilation()
    def test_valid_local_variable_destructure_tuple(self):
        """
        fun f() -> std::Void {
            let (a, b, c) = (1, 2, 3)
        }
        """

    @should_pass_compilation()
    def test_valid_local_variable_destructure_tuple_with_single_skip(self):
        """
        fun f() -> std::Void {
            let (mut a, .., mut d) = (1, "2", "3", 4)
            a = 5
            d = 6
        }
        """

    @should_pass_compilation()
    def test_valid_local_variable_destructure_tuple_with_multi_skip(self):
        """
        fun f() -> std::Void {
            let (a, .., c) = (1, 2, 3, 4, 5)
        }
        """

    @should_pass_compilation()
    def test_valid_local_variable_destructure_tuple_with_bound_multi_skip_1(self):
        """
        fun f() -> std::Void {
            let (a, ..mut b, c) = (1, false, "3", 4)
            b = (true, "5")
        }
        """

    @should_pass_compilation()
    def test_valid_local_variable_destructure_tuple_with_bound_multi_skip_2(self):
        """
        fun f() -> std::Void {
            let (..mut a, b) = (1, 2, 3, 4)
            a = (5, 6, 7)
        }
        """

    @should_pass_compilation()  # todo: if (1, 2, 3, 4) is a variable, then there is a memory error
    def test_valid_local_variable_destructure_tuple_with_bound_multi_skip_3(self):
        """
        fun f() -> std::Void {
            let (a, b, ..mut c) = (1, 2, 3, 4)
            c = (5, 6)
        }
        """

    @should_pass_compilation()
    def test_valid_local_variable_destructure_tuple_nested_tuple(self):
        """
        fun f() -> std::Void {
            let t = (1, "2")
            let ((a, mut b), c) = (t, 3)
            b = "4"
        }
        """

    @should_pass_compilation()
    def test_valid_local_variable_destructure_tuple_nested_array(self):
        """
        fun f() -> std::Void {
            let t = [1, 2]
            let ([a, mut b], c) = (t, 3)
            b = 4
        }
        """

    @should_pass_compilation()
    def test_valid_local_variable_destructure_tuple_nested_object(self):
        """
        cls Point {
            x: std::BigInt
            y: std::BigInt
        }

        fun f() -> std::Void {
            let points = (Point(x=1, y=2), Point(x=3, y=4))
            let (Point(x, mut y), ..) = points
            y = 5
        }
        """
