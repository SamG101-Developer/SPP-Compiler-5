from unittest import TestCase

from tst._Utils import *


class TestGenericTypeParameterInlineConstraintsAst(TestCase):
    @should_fail_compilation(SemanticErrors.IdentifierDuplicationError)
    def test_invalid_generic_type_parameter_inline_constraints_duplicate(self):
        """
        fun f[T: std::Bool, std::Bool]() -> std::Void { }
        """

    @should_pass_compilation()
    def test_valid_generic_type_parameter_inline_constraints(self):
        """
        fun f[T: std::Bool]() -> std::Void { }
        """
