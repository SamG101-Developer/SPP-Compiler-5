from unittest import TestCase

from tst._Utils import *


class TestGenericArgumentAst(CustomTestCase):
    @should_pass_compilation()
    def test_valid_generic_comp_argument_unnamed_expression(self):
        """
        fun f[cmp n: std::Bool]() -> std::Void { }

        fun g() -> std::Void {
            f[n=true]()
        }
        """

    @should_pass_compilation()
    def test_valid_generic_comp_argument_named_expression(self):
        """
        fun f[cmp n: std::Bool]() -> std::Void { }

        fun g() -> std::Void {
            f[true]()
        }
        """

    @should_pass_compilation()
    def test_valid_generic_type_argument_named_expression(self):
        """
        fun f[T]() -> std::Void { }

        fun g() -> std::Void {
            f[T=std::Bool]()
        }
        """

    @should_pass_compilation()
    def test_valid_generic_type_argument_unnamed_expression(self):
        """
        fun f[T]() -> std::Void { }

        fun g() -> std::Void {
            f[std::Bool]()
        }
        """
