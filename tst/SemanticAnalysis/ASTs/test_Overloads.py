from tst._Utils import *


class TestOverloads(CustomTestCase):
    @should_pass_compilation()
    def test_valid_overrides(self):
        """
        cls A { }
        cls B { }

        sup A {
            @virtual_method fun f(&self) -> std::Void { }
            @virtual_method fun f(&self, a: A) -> std::Void { }
            @virtual_method fun f(&self, a: std::Bool, b: std::BigInt) -> std::Void { }
        }

        sup B ext A {
            fun f(&self) -> std::Void { }
        }

        fun test() -> std::Void {
            let b = B()
            b.f()
            b.f(A())
            b.f(true, 1)
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionCallNoValidSignaturesError)
    def test_invalid_override_call(self):
        """
        cls A { }
        cls B { }

        sup A {
            @virtual_method fun f(&self) -> std::Void { }
            @virtual_method fun f(&self, a: A) -> std::Void { }
            @virtual_method fun f(&self, a: std::Bool, b: std::BigInt) -> std::Void { }
        }

        sup B ext A {
            fun f(&self) -> std::Void { }
        }

        fun test() -> std::Void {
            let b = B()
            b.f("a")
        }
        """
