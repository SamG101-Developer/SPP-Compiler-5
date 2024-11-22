from unittest import TestCase

from tst._Utils import *


class TestIdentifierAst(TestCase):
    @should_fail_compilation(SemanticErrors.IdentifierUnknownError)
    def test_invalid_identifier(self):
        """
        fun f() -> std::Void {
            let mut x = y
            x = z
        }
        """

    @should_pass_compilation()
    def test_valid_identifier(self):
        """
        fun f() -> std::Void {
            let mut x = 1
            let y = 2
            x = y
        }
        """
