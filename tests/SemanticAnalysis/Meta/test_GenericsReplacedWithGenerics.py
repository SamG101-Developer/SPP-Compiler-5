from tests._Utils import *


class TestGenericsReplacedWithGenerics(CustomTestCase):
    @should_pass_compilation()
    def test_generic_replaced_with_generic(self):
        """
        use std::vector::Vec
        fun g[U]() -> Vec[U] {
            ret Vec[U]()
        }
        """

    @should_pass_compilation()
    def test_generic_replaced_with_generic_stateful(self):
        """
        use std::option::Opt
        use std::option::Some

        fun g[U]() -> Opt[U] {
            ret Some[U]()
        }
        """
