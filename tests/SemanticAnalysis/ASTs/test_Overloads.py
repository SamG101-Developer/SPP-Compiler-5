from tests._Utils import *


class TestOverloads(CustomTestCase):
    @should_pass_compilation()
    def test_valid_overrides(self):
        """
        cls A { }
        cls B { }

        sup A {
            @virtual_method fun f(&self) -> std::void::Void { }
            @virtual_method fun f(&self, a: A) -> std::void::Void { }
            @virtual_method fun f(&self, a: std::boolean::Bool, b: std::number::BigInt) -> std::void::Void { }
        }

        sup B ext A {
            fun f(&self) -> std::void::Void { }
        }

        fun test() -> std::void::Void {
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
            @virtual_method fun f(&self) -> std::void::Void { }
            @virtual_method
            @no_impl fun f(&self, a: T) -> T { }
            @virtual_method fun f(&self, a: std::boolean::Bool, b: std::number::BigInt) -> std::void::Void { }
        }

        sup [T] B[T] ext A[T] {
            fun f(&self) -> std::void::Void { }
        }

        fun test() -> std::void::Void {
            let b = B[std::number::BigInt]()
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
            @virtual_method fun f(&self) -> std::void::Void { }
            @virtual_method
            @no_impl fun f(&self, a: T) -> std::vector::Vec[T] { }
            @virtual_method fun f(&self, a: std::boolean::Bool, b: std::number::BigInt) -> std::void::Void { }
        }

        sup [T] B[T] ext A[T] {
            fun f(&self) -> std::void::Void { }
        }

        fun test() -> std::void::Void {
            let b = B[std::number::BigInt]()
            b.f()
            let mut x = b.f(1)
            x = std::vector::Vec[std::number::BigInt]()
            b.f(true, 1)
        }
        """

    @should_pass_compilation()
    def test_valid_coroutine_overrides_with_generics(self):
        """
        cls A[T] { }
        cls B[T] { }

        sup [T] A[T] {
            @virtual_method cor c(&self) -> std::generator::Gen[&T, std::boolean::Bool] { }
            @virtual_method cor c(&self, a: T) -> std::generator::Gen[&T, std::boolean::Bool] { }
            @virtual_method cor c(&self, a: std::boolean::Bool, b: std::number::BigInt) -> std::generator::Gen[&T, std::boolean::Bool] { }
        }

        sup [T] B[T] ext A[T] {
            cor c(&self) -> std::generator::Gen[&T, std::boolean::Bool] { }
        }

        fun test() -> std::void::Void {
            let b = B[std::number::BigInt]()
            let coroutine = b.c(123)
            coroutine.res(false)
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionCallNoValidSignaturesError)
    def test_invalid_override_call(self):
        """
        cls A { }
        cls B { }

        sup A {
            @virtual_method fun f(&self) -> std::void::Void { }
            @virtual_method fun f(&self, a: A) -> std::void::Void { }
            @virtual_method fun f(&self, a: std::boolean::Bool, b: std::number::BigInt) -> std::void::Void { }
        }

        sup B ext A {
            fun f(&self) -> std::void::Void { }
        }

        fun test() -> std::void::Void {
            let b = B()
            b.f("a")
        }
        """
