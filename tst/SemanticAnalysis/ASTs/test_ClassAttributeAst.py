from unittest import TestCase

from tst._Utils import *


class TestClassAttributeAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.TypeVoidInvalidUsageError)
    def test_invalid_class_attribute_void_type(self):
        """
        cls A {
            a: std::Void
        }
        """

    @should_fail_compilation(SemanticErrors.IdentifierDuplicationError)
    def test_invalid_class_attribute_duplicate(self):
        """
        cls A {
            a: std::Str
            a: std::Str
        }
        """

    @should_fail_compilation(SemanticErrors.IdentifierDuplicationError)
    def test_invalid_class_attribute_duplicate_with_super_class_1(self):
        """
        cls A {
            a: std::Str
        }

        cls B {
            a: std::Str
        }

        cls C { }
        sup C ext A {}
        sup C ext B {}
        """

    @should_fail_compilation(SemanticErrors.IdentifierDuplicationError)
    def test_invalid_class_attribute_duplicate_with_super_class_2(self):
        """
        cls A {
            a: std::Str
        }

        cls B {
            a: std::Str
        }

        sup B ext A {}
        """

    @should_pass_compilation()
    def test_valid_class_attribute(self):
        """
        cls A {
            a: std::Str
            b: std::Str
        }

        cls B {
            a: std::Str
            b: std::Str
        }
        """

    @should_pass_compilation()
    def test_valid_class_attribute_with_super_class(self):
        """
        cls A {
            a: std::Str
        }

        cls B {
            b: std::Str
        }

        cls C { }
        sup C ext A {}
        sup C ext B {}
        """
