from unittest import TestCase

from SPPCompiler.Compiler.Compiler import Compiler
from tst._Utils import *


class TestAnnotationAst(TestCase):
    @should_pass
    def test_valid_annotation_virtual_method(self) -> None:
        """
        @virtual_method
        fun test_func() -> Void { }
        """

    @should_fail
    def test_invalid_annotation_virtual_method(self) -> None:
        """
        @virtual_method
        cls TestClass { }
        """
