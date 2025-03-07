from unittest import TestCase

from tests._Utils import *


class TestLocalVariableDestructureObjectAst(CustomTestCase):
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
            let Point(..mut x) = p
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

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_local_variable_destructure_object_variant_type_1(self):
        """
        fun f(o: std::Opt[std::Str]) -> std::Void {
            let std::Pass(val) = o
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

    @should_pass_compilation()
    def test_valid_local_variable_destructure_object_nested_array(self):
        """
        cls TestType {
            a: std::Arr[std::Bool, 2]
        }

        fun f(t: TestType) -> std::Void {
            let TestType(a=[b, mut other_variable]) = t
            other_variable = true
        }
        """

    @should_pass_compilation()
    def test_valid_local_variable_destructure_object_variant_type_1(self):
        """
        fun f(o: std::Opt[std::Str]) -> std::Void {
            let std::Some(mut val) = o
            val = "hello world"
        }
        """

    @should_pass_compilation()  # todo: this should be invalid (what if its Point2?)
    def test_valid_local_variable_destructure_object_variant_type_2(self):
        """
        cls Point1 {
            x: std::BigInt
            y: std::BigInt
        }

        cls Point2 {
            x: std::BigInt
            y: std::BigInt
        }

        fun f(p: Point1 or Point2) -> std::Void {
            let Point1(x, y) = p
        }
        """
