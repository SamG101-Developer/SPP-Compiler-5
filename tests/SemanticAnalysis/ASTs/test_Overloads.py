from tests._Utils import *


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

    @should_pass_compilation()
    def test_valid_overrides_with_generics(self):
        """
        cls A[T] { }
        cls B[T] { }

        sup [T] A[T] {
            @virtual_method fun f(&self) -> std::Void { }
            @virtual_method
            @no_impl fun f(&self, a: T) -> T { }
            @virtual_method fun f(&self, a: std::Bool, b: std::BigInt) -> std::Void { }
        }

        sup [T] B[T] ext A[T] {
            fun f(&self) -> std::Void { }
        }

        fun test() -> std::Void {
            let b = B[std::BigInt]()
            b.f()
            let mut x = b.f(1)
            x = 123
            b.f(true, 1)
        }
        """

    @should_pass_compilation()
    def test_valid_overrides_with_generics_complex(self):
        """
        cls A[T] { }
        cls B[T] { }

        sup [T] A[T] {
            @virtual_method fun f(&self) -> std::Void { }
            @virtual_method
            @no_impl fun f(&self, a: T) -> std::Vec[T] { }
            @virtual_method fun f(&self, a: std::Bool, b: std::BigInt) -> std::Void { }
        }

        sup [T] B[T] ext A[T] {
            fun f(&self) -> std::Void { }
        }

        fun test() -> std::Void {
            let b = B[std::BigInt]()
            b.f()
            let mut x = b.f(1)
            x = std::Vec[std::BigInt]()
            b.f(true, 1)
        }
        """

    @should_pass_compilation()
    def test_valid_coroutine_overrides_with_generics(self):
        """
        cls A[T] { }
        cls B[T] { }

        sup [T] A[T] {
            @virtual_method cor c(&self) -> std::GenRef[T] { }
            @virtual_method cor c(&self, a: T) -> std::GenRef[T] { }
            @virtual_method cor c(&self, a: std::Bool, b: std::BigInt) -> std::GenRef[T] { }
        }

        sup [T] B[T] ext A[T] {
            cor c(&self) -> std::GenRef[T] { }
        }

        fun test() -> std::Void {
            let b = B[std::BigInt]()
            let coroutine = b.c(123)
            coroutine.res()
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
