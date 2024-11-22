from unittest import TestCase

from tst._Utils import *


class DummyException(BaseException):
    pass


class TestLocalVariableDestructureObjectAst(TestCase):
    @should_fail_compilation(SemanticErrors.VariableDestructureContainsMultipleMultiSkipsError)
    def test_invalid_local_variable_destructure_object_multiple_multi_skip(self):
        """
        cls Point {
            x: std::BigInt
            y: std::BigInt
        }

        fun f(p: Point) -> std::Void {
            let Point(.., ..) = p
        }
        """

    @should_fail_compilation(SemanticErrors.VariableObjectDestructureWithBoundMultiSkipError)
    def test_invalid_local_variable_destructure_object_bound_multi_skip(self):
        """
        cls Point {
            x: std::BigInt
            y: std::BigInt
        }

        fun f(p: Point) -> std::Void {
            let Point(..x) = p
        }
        """

    @should_fail_compilation(SemanticErrors.ArgumentRequiredNameMissingError)
    def test_invalid_local_variable_destructure_object_missing_attribute(self):
        """
        cls Point {
            x: std::BigInt
            y: std::BigInt
        }

        fun f(p: Point) -> std::Void {
            let Point(x) = p
        }
        """

    @should_fail_compilation(SemanticErrors.IdentifierUnknownError)
    def test_invalid_local_variable_destructure_object_invalid_attribute(self):
        """
        cls Point {
            x: std::BigInt
            y: std::BigInt
        }

        fun f(p: Point) -> std::Void {
            let Point(x, y, z) = p
        }
        """

    @should_pass_compilation()
    def test_valid_local_variable_destructure_object(self):
        """
        cls Point {
            x: std::BigInt
            y: std::BigInt
        }

        fun f(p: Point) -> std::Void {
            let Point(x, y) = p
        }
        """

    @should_pass_compilation()
    def test_valid_local_variable_destructure_object_skip_1(self):
        """
        cls Point {
            x: std::BigInt
            y: std::BigInt
        }

        fun f(p: Point) -> std::Void {
            let Point(x, ..) = p
        }
        """

    @should_pass_compilation()
    def test_valid_local_variable_destructure_object_skip_2(self):
        """
        cls Point {
            x: std::BigInt
            y: std::BigInt
        }

        fun f(p: Point) -> std::Void {
            let Point(.., y) = p
        }
        """

    @should_pass_compilation()
    def test_valid_local_variable_destructure_object_skip_3(self):
        """
        cls Point {
            x: std::BigInt
            y: std::BigInt
        }

        fun f(p: Point) -> std::Void {
            let Point(..) = p
        }
        """

    @should_pass_compilation()
    def test_valid_local_variable_destructure_object_nested_object(self):
        """
        cls Point {
            x: std::BigInt
            y: std::BigInt
        }

        cls Line {
            start: Point
            end: Point
        }

        fun f(l: Line) -> std::Void {
            let Line(start=Point(x, y), ..) = l
        }
        """

    @should_fail_compilation(SemanticErrors.IdentifierUnknownError)
    def test_invalid_local_variable_destructure_object_check_symbols_introduced(self):
        """
        cls Point {
            x: std::BigInt
            y: std::BigInt
        }

        cls Line {
            start: Point
            end: Point
        }

        fun f(l: Line) -> std::Void {
            let Line(start=Point(x, y), ..) = l
            let t = start
        }
        """

    @should_pass_compilation()
    def test_valid_local_variable_destructure_check_symbols_introduced(self):
        """
        cls Point {
            x: std::BigInt
            y: std::BigInt
        }

        cls Line {
            start: Point
            end: Point
        }

        fun f(l: Line) -> std::Void {
            let Line(start=Point(x, y), ..) = l
            let mut t = 100
            t = y
        }
        """

    @should_pass_compilation()
    def test_valid_local_variable_destructure_object_nested_tuple(self):
        """
        cls TestType {
            a: (std::Bool, std::BigInt)
        }

        fun f(t: TestType) -> std::Void {
            let TestType(a=(b, mut other_variable)) = t
            other_variable = 2
        }
        """
