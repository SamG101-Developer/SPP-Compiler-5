from unittest import TestCase

from tst._Utils import *


class TestGlobalConstantAst(TestCase):
    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_global_constant_type_mismatch(self):
        """
        cmp x: std::BigInt = false
        """

    @should_pass_compilation()
    def test_valid_global_constant(self):
        """
        cmp x: std::BigInt = 1
        """
