from unittest import TestCase

from tests._Utils import *


class TestPatternVariantDestructureArrayAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.VariableDestructureContainsMultipleMultiSkipsError)
    def test_invalid_pattern_variant_destructure_array_multiple_multi_skip(self):
        """
        fun f(p: std::array::Arr[std::number::bigint::BigInt, 2_uz]) -> std::void::Void {
            case p is [.., ..] { }
        }
        """

    @should_fail_compilation(SemanticErrors.VariableArrayDestructureArraySizeMismatchError)
    def test_invalid_pattern_variant_destructure_array_missing_value(self):
        """
        fun f(p: std::array::Arr[std::number::bigint::BigInt, 2_uz]) -> std::void::Void {
            case p is [x] { }
        }
        """

    @should_fail_compilation(SemanticErrors.VariableArrayDestructureArraySizeMismatchError)
    def test_invalid_pattern_variant_destructure_array_extra_value(self):
        """
        fun f(p: std::array::Arr[std::number::bigint::BigInt, 2_uz]) -> std::void::Void {
            case p is [x, y, z] { }
        }
        """

    @should_pass_compilation()
    def test_valid_pattern_variant_destructure_array(self):
        """
        fun f(p: std::array::Arr[std::number::bigint::BigInt, 2_uz]) -> std::void::Void {
            case p is [x, y] { }
        }
        """

    @should_pass_compilation()
    def test_valid_pattern_variant_destructure_array_skip_1(self):
        """
        fun f(p: std::array::Arr[std::number::bigint::BigInt, 2_uz]) -> std::void::Void {
            case p is [x, _] { }
        }
        """

    @should_pass_compilation()
    def test_valid_pattern_variant_destructure_array_skip_n(self):
        """
        fun f(p: std::array::Arr[std::number::bigint::BigInt, 2_uz]) -> std::void::Void {
            case p is [x, ..] { }
        }
        """

    @should_pass_compilation()
    def test_valid_pattern_variant_destructure_array_bound_multi_skip(self):
        """
        fun f(p: std::array::Arr[std::number::bigint::BigInt, 2_uz]) -> std::void::Void {
            case p is [..x] { }
        }
        """

    @should_pass_compilation()
    def test_valid_pattern_variant_destructure_array_multiple_patterns(self):
        """
        fun f(p: std::array::Arr[std::number::bigint::BigInt, 2_uz]) -> std::void::Void {
            case p of
                is [x, y] { }
                is [x, ..] { }
        }
        """
