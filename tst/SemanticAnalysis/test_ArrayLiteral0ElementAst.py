from unittest import TestCase

from tst._Utils import *


class TestAnnotationAst(TestCase):
    @should_pass_compilation()
    def test_valid_array_empty_array_literal(self):
        """
        fun f() -> std::Void {
            let a = [std::Bool, 1]
        }
        """
