from unittest import TestCase

from tests._Utils import *


class TestArrayLiteral0ElementAst(CustomTestCase):
    @should_pass_compilation()
    def test_valid_array_empty_array_literal(self):
        """
        fun f() -> std::void::Void {
            let a = [std::boolean::Bool, 1]
        }
        """
