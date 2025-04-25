from tests._Utils import *


class TestCmpStatementAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_comptime_global_constant_type_mismatch(self):
        """
        cmp x: std::number::bigint::BigInt = false
        """

    @should_fail_compilation(SemanticErrors.InvalidConventionLocationError)
    def test_invalid_comptime_global_constant_type_convention_mut(self):
        """
        cmp x: &mut std::number::bigint::BigInt = 1
        """

    @should_fail_compilation(SemanticErrors.InvalidConventionLocationError)
    def test_invalid_comptime_global_constant_type_convention_ref(self):
        """
        cmp x: &std::number::bigint::BigInt = 1
        """

    @should_pass_compilation()
    def test_valid_comptime_global_constant(self):
        """
        cmp x: std::number::bigint::BigInt = 1
        """
