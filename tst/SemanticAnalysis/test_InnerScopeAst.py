from unittest import TestCase

from tst._Utils import *


class TestInnerScopeAst(TestCase):
    @should_fail_compilation(SemanticErrors.UnreachableCodeError)
    def test_invalid_unreachable_code_in_function(self):
        """
        fun f() -> std::BigInt {
            ret 100
            f()
        }
        """

    @should_fail_compilation(SemanticErrors.UnreachableCodeError)
    def test_invalid_unreachable_code_in_inner_scope(self):
        """
        fun f() -> std::BigInt {
            {
                ret 100
                f()
            }
        }
        """

    @should_pass_compilation()
    def test_valid_inner_scope(self):
        """
        fun f() -> std::BigInt {
            {
                ret 100
            }
            ret 200
        }
        """
