from unittest import TestCase

from tst._Utils import *


class TestAnnotationAst(TestCase):
    @should_fail_compilation(SemanticErrors.TypeVoidInvalidUsageError)
    def test_invalid_class_attribute_void_type(self):
        """
        cls A {
            a: std::Void
        }
        """

    @should_pass_compilation()
    def test_valid_class_attribute(self):
        """
        cls A {
            a: std::Str
            b: std::Str
        }
        """
