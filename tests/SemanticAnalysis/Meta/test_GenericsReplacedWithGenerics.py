from tests._Utils import *


class TestGenericsReplacedWithGenerics(CustomTestCase):
    @should_pass_compilation()
    def test_generic_replaced_with_generic(self):
        """
        use std::string::Str
        use std::vector::Vec

        fun g[U]() -> Vec[U] {
            ret Vec[U]()
        }

        fun f() -> std::void::Void {
            let mut x = g[Str]()
            x.push(element="hello")
        }
        """

    @should_pass_compilation()
    def test_generic_replaced_with_generic_stateful(self):
        """
        use std::option::Opt
        use std::option::Some
        use std::string::Str

        fun g[U]() -> Opt[U] {
            ret Some[U]()
        }

        fun f() -> std::void::Void {
            let mut x = g[Str]()
            x = Some(val="hello")
        }
        """
