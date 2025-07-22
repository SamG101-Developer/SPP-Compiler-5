from tests._Utils import *


class TestFirstClassFunctions(CustomTestCase):
    @should_pass_compilation()
    def test_subroutine_lambda_as_value(self):
        """
        use std::string::Str
        use std::function::FunRef

        fun g(x: FunRef[(), Str]) -> std::void::Void {
            let mut y = x()
            y = "Goodbye, World!"
        }

        fun f() -> std::void::Void {
            let p = || "string"
            g(p)
        }
        """

    @should_pass_compilation()
    def test_subroutine_function_as_value(self):
        """
        use std::string::Str
        use std::function::FunRef

        fun h() -> std::string::Str {
            ret "Hello, World!"
        }

        fun g(x: FunRef[(), Str]) -> std::void::Void {
            let mut y = x()
            y = "Goodbye, World!"
        }

        fun f() -> std::void::Void {
            let p = h
            g(p)
        }
        """
