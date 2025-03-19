from unittest import TestCase

from tests._Utils import *


class TestGenericArgumentAst(CustomTestCase):
    @should_pass_compilation()
    def test_valid_generic_comp_argument_unnamed_expression(self):
        """
        fun f[cmp n: std::boolean::Bool]() -> std::void::Void { }

        fun g() -> std::void::Void {
            f[n=true]()
        }
        """

    @should_pass_compilation()
    def test_valid_generic_comp_argument_named_expression(self):
        """
        fun f[cmp n: std::boolean::Bool]() -> std::void::Void { }

        fun g() -> std::void::Void {
            f[true]()
        }
        """

    @should_pass_compilation()
    def test_valid_generic_type_argument_named_expression(self):
        """
        fun f[T]() -> std::void::Void { }

        fun g() -> std::void::Void {
            f[T=std::boolean::Bool]()
        }
        """

    @should_pass_compilation()
    def test_valid_generic_type_argument_unnamed_expression(self):
        """
        fun f[T]() -> std::void::Void { }

        fun g() -> std::void::Void {
            f[std::boolean::Bool]()
        }
        """
