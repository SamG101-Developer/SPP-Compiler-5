from unittest import TestCase

from tst._Utils import *


class TestGenericArgumentGroupAst(TestCase):
    @should_fail_compilation(SemanticErrors.IdentifierDuplicationError)
    def test_invalid_generic_argument_group_duplicate_named_argument(self):
        """
        fun f[T, U]() -> std::Void { }

        fun g() -> std::Void {
            f[T=std::Bool, T=std::Bool]()
        }
        """

    @should_fail_compilation(SemanticErrors.OrderInvalidError)
    def test_invalid_generic_argument_group_invalid_argument_order(self):
        """
        fun f[T, U]() -> std::Void { }

        fun g() -> std::Void {
            f[T=std::Bool, std::Bool]()
        }
        """
