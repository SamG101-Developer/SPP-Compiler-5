from tests._Utils import *


class TestClassPrototypeAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.RecursiveTypeDefinitionError)
    def test_invalid_recursive_class_prototype(self):
        """
        cls A {
            a: A
        }
        """

    @should_fail_compilation(SemanticErrors.RecursiveTypeDefinitionError)
    def test_invalid_recursive_class_prototype_complex(self):
        """
        cls A {
            a: B
        }

        cls B {
            a: A
        }
        """

    @should_pass_compilation()
    def test_valid_class_prototype_definition(self):
        """
        cls A {
            a: B
        }

        cls B {
            a: std::string::Str
        }
        """
