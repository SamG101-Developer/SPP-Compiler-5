from unittest import TestCase

from tst._Utils import *


class TestArrayLiteral0ElementAst(CustomTestCase):
    @should_pass_compilation()
    def test_valid_array_empty_array_literal(self):
        """
        fun f() -> std::Void {
            let a = [std::Bool, 1]
        }
        """
