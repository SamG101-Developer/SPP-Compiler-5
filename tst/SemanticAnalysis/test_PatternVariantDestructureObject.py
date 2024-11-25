from unittest import TestCase

from tst._Utils import *


# Todo: flush out the test cases

class TestPatternVariantDestructureObjectAst(TestCase):
    @should_fail_compilation(SemanticErrors.VariableDestructureContainsMultipleMultiSkipsError)
    def test_invalid_pattern_variant_destructure_object_multiple_multi_skip(self):
        """
        cls Point {
            x: std::BigInt
            y: std::BigInt
        }

        fun f(p: Point) -> std::Void {
            case p then is Point(.., ..) { }
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
            case p then is Point(..x) { }
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
            case p then is Point(x) { }
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
            case p then is Point(x, y, z) { }
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
            case p then is Point(x, y) { }
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
            case p then is Point(x, ..) { }
        }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
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
            case p then is
                Point1(x, y) { }
                Point2(x, y) { }
        }
        """
