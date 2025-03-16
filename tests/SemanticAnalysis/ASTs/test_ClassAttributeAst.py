from tests._Utils import *


class TestClassAttributeAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.TypeVoidInvalidUsageError)
    def test_invalid_class_attribute_void_type(self):
        """
        cls A {
            a: std::void::Void
        }
        """

    @should_fail_compilation(SemanticErrors.IdentifierDuplicationError)
    def test_invalid_class_attribute_duplicate(self):
        """
        cls A {
            a: std::string::Str
            a: std::string::Str
        }
        """

    @should_fail_compilation(SemanticErrors.IdentifierDuplicationError)
    def test_invalid_class_attribute_duplicate_with_super_class_1(self):
        """
        cls A {
            a: std::string::Str
        }

        cls B {
            a: std::string::Str
        }

        cls C { }
        sup C ext A {}
        sup C ext B {}
        """

    @should_fail_compilation(SemanticErrors.IdentifierDuplicationError)
    def test_invalid_class_attribute_duplicate_with_super_class_2(self):
        """
        cls A {
            a: std::string::Str
        }

        cls B {
            a: std::string::Str
        }

        sup B ext A {}
        """

    @should_fail_compilation(SemanticErrors.InvalidConventionLocationError)
    def test_invalid_class_attribute_convention_mut(self):
        """
        cls A {
            a: &mut std::string::Str
        }
        """

    @should_fail_compilation(SemanticErrors.InvalidConventionLocationError)
    def test_invalid_class_attribute_convention_ref(self):
        """
        cls A {
            a: &std::string::Str
        }
        """

    @should_pass_compilation()
    def test_valid_class_attribute(self):
        """
        cls A {
            a: std::string::Str
            b: std::string::Str
        }

        cls B {
            a: std::string::Str
            b: std::string::Str
        }
        """

    @should_pass_compilation()
    def test_valid_class_attribute_with_super_class(self):
        """
        cls A {
            a: std::string::Str
        }

        cls B {
            b: std::string::Str
        }

        cls C { }
        sup C ext A {}
        sup C ext B {}
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_class_attribute_default_value(self):
        """
        cls A {
            a: std::string::Str = 1
        }
        """

    @should_pass_compilation()
    def test_valid_class_attribute_default_value(self):
        """
        cls A {
            a: std::string::Str = "Hello"
        }
        """
