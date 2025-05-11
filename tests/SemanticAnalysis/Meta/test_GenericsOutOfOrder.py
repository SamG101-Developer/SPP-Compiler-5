from tests._Utils import *


class Test_GenericsOutOfOrder(CustomTestCase):
    @should_pass_compilation()
    def test_type_match_same_type_same_generic_order(self):
        """
        cls Type[T, U] { }

        fun f() -> std::void::Void {
            let mut type1 = Type[std::boolean::Bool, std::string::Str]()
            type1 = Type[T=std::boolean::Bool, U=std::string::Str]()
        }
        """

    @should_pass_compilation()
    def test_type_match_same_type_different_generic_order(self):
        """
        cls Type[T, U] { }

        fun f() -> std::void::Void {
            let mut type1 = Type[std::boolean::Bool, std::string::Str]()
            type1 = Type[U=std::string::Str, T=std::boolean::Bool]()
        }
        """
