from unittest import TestCase

from tests._Utils import *


class TestPostfixExpressionOperatorFunctionCallAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.FunctionCallOnNoncallableTypeError)
    def test_invalid_postfix_func_call_on_non_callable(self):
        """
        fun f() -> std::Void {
            5()
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionCallNoValidSignaturesError)
    def test_invalid_postfix_func_call_abstract_function(self):
        """
        cls TestClass { }
        sup TestClass {
            @abstract_method
            fun f(&self) -> std::Void { }
        }

        fun g() -> std::Void {
            TestClass().f()
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionCallNoValidSignaturesError)
    def test_invalid_postfix_func_call_too_many_args(self):
        """
        fun f() -> std::Void {
            f(5)
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionCallNoValidSignaturesError)
    def test_invalid_postfix_func_call_arg_name(self):
        """
        fun f(a: std::BigInt) -> std::Void {
            f(a=1, b=2)
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionCallNoValidSignaturesError)
    def test_invalid_postfix_func_call_name_missing(self):
        """
        fun f(a: std::BigInt, b: std::BigInt) -> std::Void {
            f(1)
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionCallNoValidSignaturesError)
    def test_invalid_postfix_func_call_arg_type_mismatch(self):
        """
        fun f(a: std::BigInt) -> std::Void {
            f("a")
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionCallNoValidSignaturesError)
    def test_invalid_postfix_func_call_missing_explicit_generic(self):
        """
        fun f[T](a: std::BigInt) -> std::Void {
            f(1)
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionCallNoValidSignaturesError)
    def test_invalid_postfix_func_call_generic_conflict(self):
        """
        fun f[T](a: T, b: T) -> std::Void {
            f(1, "1")
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionCallNoValidSignaturesError)
    def test_invalid_postfix_func_call_unnecessary_explicit_generic(self):
        """
        fun f[T](a: T) -> std::Void {
            f[std::BigInt](1)
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionCallNoValidSignaturesError)
    def test_invalid_postfix_func_call_extra_generic(self):
        """
        fun f[T](a: T) -> std::Void {
            f[std::Bool, std::Bool](1)
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionCallNoValidSignaturesError)
    def test_invalid_postfix_func_call_generic_named(self):
        """
        fun f[T](a: T) -> std::Void {
            f[T=std::Bool, U=std::Bool](1)
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionCallNoValidSignaturesError)
    def test_invalid_postfix_func_call_generic_explicit_and_inferred(self):
        """
        fun f[T, U](a: T) -> std::Void {
            f[std::Bool](123)
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionCallAmbiguousSignaturesError)
    def test_invalid_postfix_func_call_ambiguous_1(self):
        """
        fun f(a: std::BigInt) -> std::Void { }
        fun f[T](a: T) -> std::Void { }

        fun g() -> std::Void {
            f(1)
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionCallAmbiguousSignaturesError)
    def test_invalid_postfix_func_call_ambiguous_2(self):
        """
        fun f[T](a: T, b: std::BigInt) -> std::Void { }
        fun f[T](a: std::BigInt, b: T) -> std::Void { }

        fun g() -> std::Void {
            f(1, 2)
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryUsageOfUnpinnedBorrowError)
    def test_invalid_postfix_func_call_coroutine_missing_pins(self):
        """
        cor c(a: &std::BigInt) -> std::GenMov[std::BigInt] { }

        fun f() -> std::Void {
            let x = 123
            c(&x)
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryUsageOfUnpinnedBorrowError)
    def test_invalid_postfix_func_call_async_missing_pins(self):
        """
        fun a(b: &std::BigInt) -> std::Void { }

        fun f() -> std::Void {
            let x = 123
            async a(&x)
        }
        """

    @should_pass_compilation()
    def test_valid_postfix_func_call_no_params(self):
        """
        fun f() -> std::Void {
            f()
        }
        """

    @should_pass_compilation()
    def test_valid_postfix_func_call_single_param(self):
        """
        fun f(a: std::BigInt) -> std::Void {
            f(1)
        }
        """

    @should_pass_compilation()
    def test_valid_postfix_func_call_multiple_params(self):
        """
        fun f(a: std::BigInt, b: std::BigInt) -> std::Void {
            f(1, 2)
        }
        """

    @should_pass_compilation()
    def test_valid_postfix_func_call_generic(self):
        """
        fun f[T](a: T) -> std::Void {
            f(1)
        }
        """

    @should_pass_compilation()
    def test_valid_postfix_func_call_generic_multiple(self):
        """
        fun f[T, U](a: T, b: U) -> std::Void {
            f(1, "1")
        }
        """

    @should_pass_compilation()
    def test_valid_postfix_func_call_generic_multiple_same_type(self):
        """
        fun f[T](a: T, b: T) -> std::Void {
            f(1, 2)
        }
        """

    @should_pass_compilation()
    def test_valid_postfix_func_call_generic_explicit(self):
        """
        fun f[T, U]() -> std::Void {
            f[std::BigInt, std::Str]()
        }
        """

    @should_pass_compilation()
    def test_valid_postfix_func_call_generic_explicit_and_inferred(self):
        """
        fun f[T, U](a: T) -> std::Void {
            f[U=std::Bool](123)
        }
        """

    @should_pass_compilation()
    def test_valid_postfix_func_call_coroutine_correct_pins(self):
        """
        cor c(a: &std::BigInt) -> std::GenMov[std::BigInt] { }

        fun f() -> std::Void {
            let x = 123
            pin x
            c(&x)
        }
        """

    @should_pass_compilation()
    def test_valid_postfix_func_call_async_correct_pins(self):
        """
        fun a(b: &std::BigInt) -> std::Void { }

        fun f() -> std::Void {
            let x = 123
            pin x
            async a(&x)
        }
        """

    @should_pass_compilation()
    def test_valid_postfix_function_call_with_member_access(self):
        """
        cls TestClass { }
        cls NewClass {
            t: TestClass
            u: TestClass
        }

        sup TestClass {
            fun f(self) -> std::Void { }
        }

        fun g(n: NewClass) -> std::Void {
            n.t.f()
        }
        """

    @should_pass_compilation()
    def test_valid_postfix_function_call_with_member_access_2(self):
        """
        cls TestClass { }
        cls NewClass {
            t: TestClass
            u: TestClass
        }

        sup TestClass {
            fun f(self, t: TestClass) -> std::Void { }
        }

        fun g(n: NewClass) -> std::Void {
            n.t.f(n.u)
        }
        """

    @should_pass_compilation()
    def test_valid_postfix_function_call_with_member_access_3(self):
        """
        cls TestClass { }
        cls NewClass {
            t: TestClass
            u: TestClass
            v: TestClass
        }

        sup TestClass {
            @no_impl
            fun f(self, t: TestClass) -> TestClass { }
        }

        fun g(n: NewClass) -> std::Void {
            n.t.f(n.u).f(n.v)
        }
        """

    @should_pass_compilation()
    def test_valid_postfix_function_call_with_superimposition(self):
        """
        cls TestClass { }
        sup TestClass {
            @virtual_method
            fun f(self) -> std::Void { }
        }

        cls TestClass2 { }
        sup TestClass2 ext TestClass {
            fun f(self) -> std::Void { }
        }

        fun g() -> std::Void {
            TestClass2().f()
        }
        """

    @should_pass_compilation()
    def test_valid_postfix_function_folding_1(self):
        """
        fun f(a: std::BigInt) -> std::Str { }
        fun g() -> std::Void {
            let x = (1, 2, 3, 4)
            let mut y = f(x)..
            y = ("a", "b", "c", "d")
        }
        """

    @should_pass_compilation()
    def test_valid_postfix_function_folding_2(self):
        """
        fun f(a: std::BigInt, b: std::BigInt) -> std::Void { }
        fun g() -> std::Void {
            let x = (1, 2, 3, 4)
            let y = (1, 2, 3, 4)
            let mut z = f(x, y)..
            z = ("a", "b", "c", "d")
        }
        """

    @should_pass_compilation()
    def test_valid_remove_parameter_for_void_substitution(self):
        """
        cls TestClass[T] { }

        sup [T] TestClass[T] {
            fun f(self, a: T) -> std::Void { }
        }

        fun g() -> std::Void {
            let x = TestClass[std::Void]()
            x.f()
        }
        """

    @should_fail_compilation(SemanticErrors.VariableTupleDestructureTupleSizeMismatchError)
    def test_invalid_postfix_function_folding_1(self):
        """
        fun f(a: std::BigInt, b: std::BigInt) -> std::Void { }
        fun g() -> std::Void {
            let x = (1, 2, 3, 4)
            let y = (1, 2)
            f(x, y)..
        }
        """

    @should_pass_compilation()
    def test_valid_postfix_function_generic_substitution_void(self):
        """
        cls Type[T] { }
        sup [T] Type[T] {
            fun f(self, a: T) -> std::Void { }
        }

        fun f() -> std::Void {
            let x = Type[std::Void]()
            x.f()
        }
        """
