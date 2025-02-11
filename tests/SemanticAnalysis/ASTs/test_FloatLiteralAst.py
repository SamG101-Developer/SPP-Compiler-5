from unittest import TestCase

from tests._Utils import *


class TestFloatLiteralAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.NumberOutOfBoundsError)
    def test_invalid_float_under_minimum_f8(self):
        """
        cmp a: std::F8 = -9.0_f8
        """

    @should_fail_compilation(SemanticErrors.NumberOutOfBoundsError)
    def test_invalid_float_over_maximum_f8(self):
        """
        cmp a: std::F8 = 9.0_f8
        """

    @should_fail_compilation(SemanticErrors.NumberOutOfBoundsError)
    def test_invalid_float_under_minimum_f16(self):
        """
        cmp a: std::F16 = -65505.0_f16
        """

    @should_fail_compilation(SemanticErrors.NumberOutOfBoundsError)
    def test_invalid_float_over_maximum_f16(self):
        """
        cmp a: std::F16 = 65505.0_f16
        """

    @should_pass_compilation()
    def test_valid_float_f8(self):
        """
        cmp a: std::F8 = 0.0_f8
        """

    @should_pass_compilation()
    def test_valid_float_f16(self):
        """
        cmp a: std::F16 = 0.0_f16
        """
