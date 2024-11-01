from unittest import TestCase

from tst._Utils import *


class TestFunctionParameterGroupAst(TestCase):
    @should_pass_compilation
    def test_self_parameter(self):
        """
        fun f(self) -> Void {}
        """

    @should_pass_compilation
    def test_required_parameters(self):
        """
        fun f(a: Str, b: Str) -> Void {}
        """

    @should_pass_compilation
    def test_optional_parameters(self):
        """
        fun f(a: Str = "default 1", b: Str = "default 2") -> Void {}
        """

    @should_pass_compilation
    def test_variadic_parameter(self):
        """
        fun f(..a: Str) -> Void {}
        """

    @should_pass_compilation
    def test_ordering(self):
        """
        fun f(self, a: Str, b: Str = "default", ..c: Str) -> Void {}
        """

    @should_fail_compilation
    def test_more_than_1_self_parameter(self):
        """
        fun f(self, self) -> Void {}
        """

    @should_fail_compilation
    def test_more_than_1_variadic_parameter(self):
        """
        fun f(..a: Str, ..b: Str) -> Void {}
        """

    @should_fail_compilation
    def test_duplicate_parameter_names(self):
        """
        fun f(a: Str, a: Bool) -> Void {}
        """

    @should_fail_compilation
    def test_invalid_ordering_1(self):
        """
        fun f(a: Str, self) -> Void {}
        """

    @should_fail_compilation
    def test_invalid_ordering_2(self):
        """
        fun f(a: Str = "default", b: Str) -> Void {}
        """

    @should_fail_compilation
    def test_invalid_ordering_3(self):
        """
        fun f(..a: Str, b: Str = "default") -> Void {}
        """