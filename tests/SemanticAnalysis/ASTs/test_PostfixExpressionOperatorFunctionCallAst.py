from tests._Utils import *


class TestPostfixExpressionOperatorFunctionCallAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.FunctionCallNoValidSignaturesError)
    def test_invalid_postfix_func_call_on_non_callable(self):
        """
        fun f() -> std::void::Void {
            5()
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionCallNoValidSignaturesError)
    def test_invalid_postfix_func_call_abstract_function(self):
        """
        cls TestClass { }
        sup TestClass {
            @abstract_method
            fun f(&self) -> std::void::Void { }
        }

        fun g() -> std::void::Void {
            TestClass().f()
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionCallNoValidSignaturesError)
    def test_invalid_postfix_func_call_too_many_args(self):
        """
        fun f() -> std::void::Void {
            f(5)
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionCallNoValidSignaturesError)
    def test_invalid_postfix_func_call_arg_name(self):
        """
        fun f(a: std::number::bigint::BigInt) -> std::void::Void {
            f(a=1, b=2)
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionCallNoValidSignaturesError)
    def test_invalid_postfix_func_call_name_missing(self):
        """
        fun f(a: std::number::bigint::BigInt, b: std::number::bigint::BigInt) -> std::void::Void {
            f(1)
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionCallNoValidSignaturesError)
    def test_invalid_postfix_func_call_arg_type_mismatch(self):
        """
        fun f(a: std::number::bigint::BigInt) -> std::void::Void {
            f("a")
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionCallNoValidSignaturesError)
    def test_invalid_postfix_func_call_missing_explicit_generic(self):
        """
        fun f[T](a: std::number::bigint::BigInt) -> std::void::Void {
            f(1)
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionCallNoValidSignaturesError)
    def test_invalid_postfix_func_call_generic_conflict(self):
        """
        fun f[T](a: T, b: T) -> std::void::Void {
            f(1, "1")
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionCallNoValidSignaturesError)
    def test_invalid_postfix_func_call_unnecessary_explicit_generic(self):
        """
        fun f[T](a: T) -> std::void::Void {
            f[std::number::bigint::BigInt](1)
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionCallNoValidSignaturesError)
    def test_invalid_postfix_func_call_unnecessary_explicit_generic(self):
        """
        fun f[T](a: T) -> std::void::Void {
            f[std::string::Str](1)
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionCallNoValidSignaturesError)
    def test_invalid_postfix_func_call_extra_generic(self):
        """
        fun f[T](a: T) -> std::void::Void {
            f[std::boolean::Bool, std::boolean::Bool](1)
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionCallNoValidSignaturesError)
    def test_invalid_postfix_func_call_generic_named(self):
        """
        fun f[T](a: T) -> std::void::Void {
            f[T=std::boolean::Bool, U=std::boolean::Bool](1)
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionCallNoValidSignaturesError)
    def test_invalid_postfix_func_call_generic_explicit_and_inferred(self):
        """
        fun f[T, U](a: T) -> std::void::Void {
            f[std::boolean::Bool](123)
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionCallAmbiguousSignaturesError)
    def test_invalid_postfix_func_call_ambiguous_1(self):
        """
        fun f(a: std::number::bigint::BigInt) -> std::void::Void { }
        fun f[T](a: T) -> std::void::Void { }

        fun g() -> std::void::Void {
            f(1)
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionCallAmbiguousSignaturesError)
    def test_invalid_postfix_func_call_ambiguous_2(self):
        """
        fun f[T](a: T, b: std::number::bigint::BigInt) -> std::void::Void { }
        fun f[T](a: std::number::bigint::BigInt, b: T) -> std::void::Void { }

        fun g() -> std::void::Void {
            f(1, 2)
        }
        """

    @should_pass_compilation()
    def test_valid_postfix_func_call_no_params(self):
        """
        fun f() -> std::void::Void {
            f()
        }
        """

    @should_pass_compilation()
    def test_valid_postfix_func_call_single_param(self):
        """
        fun f(a: std::number::bigint::BigInt) -> std::void::Void {
            f(1)
        }
        """

    @should_pass_compilation()
    def test_valid_postfix_func_call_multiple_params(self):
        """
        fun f(a: std::number::bigint::BigInt, b: std::number::bigint::BigInt) -> std::void::Void {
            f(1, 2)
        }
        """

    @should_pass_compilation()
    def test_valid_postfix_func_call_generic(self):
        """
        fun f[T](a: T) -> std::void::Void {
            f(1)
        }
        """

    @should_pass_compilation()
    def test_valid_postfix_func_call_generic_multiple(self):
        """
        fun f[T, U](a: T, b: U) -> std::void::Void {
            f(1, "1")
        }
        """

    @should_pass_compilation()
    def test_valid_postfix_func_call_generic_multiple_same_type(self):
        """
        fun f[T](a: T, b: T) -> std::void::Void {
            f(1, 2)
        }
        """

    @should_pass_compilation()
    def test_valid_postfix_func_call_generic_explicit(self):
        """
        fun f[T, U]() -> std::void::Void {
            f[std::number::bigint::BigInt, std::string::Str]()
        }
        """

    @should_pass_compilation()
    def test_valid_postfix_func_call_generic_explicit_and_inferred(self):
        """
        fun f[T, U](a: T) -> std::void::Void {
            f[U=std::boolean::Bool](123)
        }
        """

    @should_pass_compilation()
    def test_valid_postfix_func_call_coroutine_correct_pins(self):
        """
        cor c(a: &std::number::bigint::BigInt) -> std::generator::Gen[std::number::bigint::BigInt] { }

        fun f() -> std::void::Void {
            let x = 123
            c(&x)
        }
        """

    @should_pass_compilation()
    def test_valid_postfix_func_call_async_correct_pins(self):
        """
        fun a(b: &std::number::bigint::BigInt) -> std::void::Void { }

        fun f() -> std::void::Void {
            let x = 123
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
            fun f(self) -> std::void::Void { }
        }

        fun g(n: NewClass) -> std::void::Void {
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
            fun f(self, t: TestClass) -> std::void::Void { }
        }

        fun g(n: NewClass) -> std::void::Void {
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

        fun g(n: NewClass) -> std::void::Void {
            n.t.f(n.u).f(n.v)
        }
        """

    @should_pass_compilation()
    def test_valid_postfix_function_call_with_superimposition(self):
        """
        cls TestClass { }
        sup TestClass {
            @virtual_method
            fun f(self) -> std::void::Void { }
        }

        cls TestClass2 { }
        sup TestClass2 ext TestClass {
            fun f(self) -> std::void::Void { }
        }

        fun g() -> std::void::Void {
            TestClass2().f()
        }
        """

    @should_pass_compilation()
    def test_valid_postfix_function_folding_1(self):
        """
        fun f(a: std::number::bigint::BigInt) -> std::string::Str {
            ret "hello world"
        }

        fun g() -> std::void::Void {
            let x = (1, 2, 3, 4)
            let mut y = f(x)..
        }
        """

    @should_pass_compilation()
    def test_valid_postfix_function_folding_2(self):
        """
        fun f(a: std::number::bigint::BigInt, b: std::number::bigint::BigInt) -> std::void::Void { }

        fun g() -> std::void::Void {
            let x = (1, 2, 3, 4)
            let y = (1, 2, 3, 4)
            let mut z = f(x, y)..
        }
        """

    @should_pass_compilation()
    def test_valid_remove_parameter_for_void_substitution(self):
        """
        cls TestClass[T] { }

        sup [T] TestClass[T] {
            fun f(self, a: T) -> std::void::Void { }
        }

        fun g() -> std::void::Void {
            let x = TestClass[std::void::Void]()
            x.f()
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionFoldTupleLengthMismatchError)
    def test_invalid_postfix_function_folding_1(self):
        """
        fun f(a: std::number::bigint::BigInt, b: std::number::bigint::BigInt) -> std::void::Void { }
        fun g() -> std::void::Void {
            let x = (1, 2, 3, 4)
            let y = (1, 2)
            f(x, y)..
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionFoldTupleElementTypeMismatchError)
    def test_invalid_postfix_function_folding_2(self):
        """
        fun f(a: std::number::bigint::BigInt, b: std::number::bigint::BigInt) -> std::void::Void { }
        fun g() -> std::void::Void {
            let x = (1, 2, 3, "4")
            let y = (1, 2, 3, "4")
            f(x, y)..
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_invalid_postfix_function_folding_moving_objects(self):
        """
        fun f(a: std::number::bigint::BigInt, b: std::string::Str) -> std::void::Void { }
        fun g() -> std::void::Void {
            let x = (1, 2, 3)
            let y = "hello world"
            f(x, y)..
        }
        """

    @should_pass_compilation()
    def test_invalid_postfix_function_folding_copying_objects(self):
        """
        fun f(a: std::number::bigint::BigInt, b: std::number::usize::USize) -> std::void::Void { }
        fun g() -> std::void::Void {
            let x = (1, 2, 3)
            let y = 0_uz
            f(x, y)..
        }
        """
