from unittest import TestCase

from tst._Utils import *


class TestAnnotationAst(TestCase):
    @should_pass_compilation
    def test_valid_annotation_virtual_method(self) -> None:
        """
        """
