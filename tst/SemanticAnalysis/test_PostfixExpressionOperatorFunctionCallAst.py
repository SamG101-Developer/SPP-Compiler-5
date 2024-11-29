from unittest import TestCase

from tst._Utils import *


class TestPostfixExpressionOperatorFunctionCallAst(TestCase):
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
        fun f(a: T) -> std::Void { }

        fun g() -> std::Void {
            f(1)
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionCallAmbiguousSignaturesError)
    def test_invalid_postfix_func_call_ambiguous_2(self):
        """
        fun f(a: T, b: std::BigInt) -> std::Void { }
        fun f(a: std::BigInt, b: T) -> std::Void { }

        fun g() -> std::Void {
            f(1, 2)
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
