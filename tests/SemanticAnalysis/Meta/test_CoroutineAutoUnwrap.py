from tests._Utils import *


class TestCoroutineAutoUnwrap(CustomTestCase):
    @should_pass_compilation()
    def test_auto_unwrap_vector(self):
        """
        use std::string::Str
        use std::vector::Vec
        use std::void::Void

        fun f() -> Void {
            let mut vec = Vec[Str]()
            vec.push("hello")
            vec.push("world")

            let mut elem1 = vec.index_ref(0_uz)
            let mut elem2 = vec.index_ref(1_uz)
            let mut value = elem1 + elem2.clone()
            value = "hello world !!!"
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionCallNoValidSignaturesError)
    def test_auto_unwrap_vector_wrong_gen_type(self):
        """
        use std::string::Str
        use std::vector::Vec
        use std::void::Void

        fun f() -> Void {
            let mut vec = Vec[Str]()
            vec.push("hello")
            vec.push("world")

            let mut elem1 = vec.index_ref(0_uz)
            let mut elem2 = vec.index_ref(1_uz)
            let mut value = elem1 + elem2
            value = "hello world !!!"
        }
        """
