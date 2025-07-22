from tests._Utils import *


class TestParser(CustomTestCase):
    @should_pass_compilation()
    def test_valid_class_attribute(self):
        """
        cls A {
            a: std::bignum::bigint::BigInt
            b: std::string::Str
        }
        """

    @should_pass_compilation()
    def test_valid_class_attribute_default_value(self):
        """
        cls A {
            a: std::bignum::bigint::BigInt = 1
            b: std::string::Str = "hello"
        }
        """
