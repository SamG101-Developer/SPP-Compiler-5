from unittest import TestCase

from tst._Utils import *


class TestAnnotationAst(TestCase):
    @should_pass
    def test_valid_annotation_virtual_method(self) -> None:
        """
        @virtual_method
        fun test_func() -> Void { }
        """

    @should_pass
    def test_valid_annotation_abstract_method(self) -> None:
        """
        @abstract_method
        fun test_func() -> Void { }
        """

    @should_pass
    def test_valid_annotation_public(self) -> None:
        """
        @public
        cls TestClass { }
        """

    @should_pass
    def test_valid_annotation_protected(self) -> None:
        """
        @protected
        cls TestClass { }
        """

    @should_pass
    def test_valid_annotation_private(self) -> None:
        """
        @private
        cls TestClass { }
        """

    @should_fail
    def test_invalid_annotation_virtual_method(self) -> None:
        """
        @virtual_method
        cls TestClass { }
        """

    @should_fail
    def test_invalid_annotation_abstract_method(self) -> None:
        """
        @abstract_method
        cls TestClass { }
        """
