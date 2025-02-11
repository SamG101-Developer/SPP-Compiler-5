from unittest import TestCase

from tests._Utils import *


class TestPatternVariantDestructureTupleAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.VariableDestructureContainsMultipleMultiSkipsError)
    def test_invalid_pattern_variant_destructure_tuple_multiple_multi_skip(self):
        """
        fun f(p: (std::BigInt, std::BigInt)) -> std::Void {
            case p is (.., ..) { }
        }
        """

    @should_fail_compilation(SemanticErrors.VariableTupleDestructureTupleSizeMismatchError)
    def test_invalid_pattern_variant_destructure_object_missing_attribute(self):
        """
        fun f(p: (std::BigInt, std::BigInt)) -> std::Void {
            case p is (x) { }
        }
        """

    @should_fail_compilation(SemanticErrors.VariableTupleDestructureTupleSizeMismatchError)
    def test_invalid_pattern_variant_destructure_object_invalid_attribute(self):
        """
        fun f(p: (std::BigInt, std::BigInt)) -> std::Void {
            case p is (x, y, z) { }
        }
        """

    @should_pass_compilation()
    def test_valid_pattern_variant_destructure_object(self):
        """
        fun f(p: (std::BigInt, std::BigInt)) -> std::Void {
            case p is (x, y) { }
        }
        """

    @should_pass_compilation()
    def test_valid_pattern_variant_destructure_object_skip_1(self):
        """
        fun f(p: (std::BigInt, std::BigInt)) -> std::Void {
            case p is (x, ..) { }
        }
        """

    @should_pass_compilation()
    def test_valid_pattern_variant_destructure_object_bound_multi_skip(self):
        """
        fun f(p: (std::BigInt, std::BigInt)) -> std::Void {
            case p is (..mut x) { }
        }
        """
