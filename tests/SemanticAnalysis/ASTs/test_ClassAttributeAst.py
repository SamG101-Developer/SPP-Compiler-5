from tests._Utils import *


class TestClassAttributeAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.IdentifierDuplicationError)
    def test_invalid_class_attribute_duplicate(self):
        """
        cls A {
            a: std::string::Str
            a: std::string::Str
        }
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

    @should_fail_compilation(SemanticErrors.InvalidConventionLocationError)
    def test_invalid_class_attribute_convention_mut_from_generic_substitution(self):
        """
        cls A[T] {
            a: T
        }

        fun f() -> std::void::Void {
            let a = A[&mut std::string::Str]()
        }
        """

    @should_fail_compilation(SemanticErrors.InvalidConventionLocationError)
    def test_invalid_class_attribute_convention_ref_from_generic_substitution(self):
        """
        cls A[T] {
            a: T
        }

        fun f() -> std::void::Void {
            let a = A[&std::string::Str]()
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
