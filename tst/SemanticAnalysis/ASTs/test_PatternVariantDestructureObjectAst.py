from unittest import TestCase

from tst._Utils import *


# Todo: flush out the test cases

class TestPatternVariantDestructureObjectAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.VariableDestructureContainsMultipleMultiSkipsError)
    def test_invalid_pattern_variant_destructure_object_multiple_multi_skip(self):
        """
        cls Point {
            x: std::BigInt
            y: std::BigInt
        }

        fun f(p: Point) -> std::Void {
            case p is Point(.., ..) { }
        }
        """

    @should_fail_compilation(SemanticErrors.VariableObjectDestructureWithBoundMultiSkipError)
    def test_invalid_pattern_variant_destructure_object_bound_multi_skip(self):
        """
        cls Point {
            x: std::BigInt
            y: std::BigInt
        }

        fun f(p: Point) -> std::Void {
            case p is Point(..x) { }
        }
        """

    @should_fail_compilation(SemanticErrors.ArgumentRequiredNameMissingError)
    def test_invalid_pattern_variant_destructure_object_missing_attribute(self):
        """
        cls Point {
            x: std::BigInt
            y: std::BigInt
        }

        fun f(p: Point) -> std::Void {
            case p is Point(x) { }
        }
        """

    @should_fail_compilation(SemanticErrors.IdentifierUnknownError)
    def test_invalid_pattern_variant_destructure_object_invalid_attribute(self):
        """
        cls Point {
            x: std::BigInt
            y: std::BigInt
        }

        fun f(p: Point) -> std::Void {
            case p is Point(x, y, z) { }
        }
        """

    @should_fail_compilation(SemanticErrors.IdentifierUnknownError)
    def test_invalid_pattern_variant_destructure_object_aliasing_attributes(self):
        """
        cls Point1 {
            x: std::BigInt
            y: std::BigInt
        }

        fun f(p: Point1) -> std::Void {
            case p is Point1(x as x_value, ..) { let xxx = x }
        }
        """

    @should_pass_compilation()
    def test_valid_pattern_variant_destructure_object(self):
        """
        cls Point {
            x: std::BigInt
            y: std::BigInt
        }

        fun f(p: Point) -> std::Void {
            case p is Point(x, y) { }
        }
        """

    @should_pass_compilation()
    def test_valid_pattern_variant_destructure_object_skip_1(self):
        """
        cls Point {
            x: std::BigInt
            y: std::BigInt
        }

        fun f(p: Point) -> std::Void {
            case p is Point(x, ..) { }
        }
        """

    @should_pass_compilation()
    def test_valid_pattern_variant_destructure_object_variant_type(self):
        """
        cls Point1 {
            x: std::BigInt
            y: std::BigInt
        }

        cls Point2 {
            x: std::BigInt
            y: std::BigInt
        }

        fun f(p: Point1 | Point2) -> std::Void {
            case p of
                is Point1(x, y) { }
                is Point2(x, y) { }
        }
        """

    @should_pass_compilation()
    def test_valid_pattern_variant_destructure_object_aliasing_attributes(self):
        """
        cls Point1 {
            x: std::BigInt
            y: std::BigInt
        }

        fun f(p: Point1) -> std::Void {
            case p of
                is Point1(x as x_value, ..) { let xxx = x_value }
                is Point1(y as y_value, ..) { let yyy = y_value }
        }
        """
