from tests._Utils import *


class TestPostfixExpressionOperatorResumeCoroutineAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.ExpressionNotGeneratorError)
    def test_invalid_postfix_expression_resume_coroutine_on_non_generator_object(self):
        """
        fun g() -> std::string::Str {
            ret "hello"
        }

        fun f() -> std::void::Void {
            let a = g()
            let b = a.res()
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionCallNoValidSignaturesError)
    def test_invalid_resume_type_mismatch_wrong_type(self):
        """
        cor g() -> std::generator::Gen[Yield=std::number::bigint::BigInt, Send=std::string::Str] {
            gen 1
        }

        fun f(c: std::number::bigint::BigInt) -> std::void::Void {
            let a = g()
            let b = a.res(123)
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionCallNoValidSignaturesError)
    def test_invalid_resume_type_mismatch_missing_arg(self):
        """
        cor g() -> std::generator::Gen[Yield=std::number::bigint::BigInt, Send=std::string::Str] {
            gen 1
        }

        fun f(c: std::number::bigint::BigInt) -> std::void::Void {
            let a = g()
            let b = a.res()
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionCallNoValidSignaturesError)
    def test_invalid_resume_type_mismatch_extra_arg(self):
        """
        cor g() -> std::generator::Gen[Yield=std::number::bigint::BigInt, Send=std::void::Void] {
            gen 1
        }

        fun f(c: std::number::bigint::BigInt) -> std::void::Void {
            let a = g()
            let b = a.res(123)
        }
        """

    @should_pass_compilation()
    def test_valid_postfix_expression_resume_on_generator_object_mov(self):
        """
        cor g() -> std::generator::Gen[Yield=std::number::bigint::BigInt, Send=std::string::Str] {
            gen 1
        }

        fun f(c: std::number::bigint::BigInt) -> std::void::Void {
            let a = g()
            let mut b = a.res("123")
            b = c
        }
        """

    @should_pass_compilation()
    def test_valid_postfix_expression_resume_coroutine_on_generator_object_ref(self):
        """
        cor g() -> std::generator::Gen[Yield=&std::number::bigint::BigInt, Send=std::string::Str] {
            gen &1
        }

        fun f(c: &std::number::bigint::BigInt) -> std::void::Void {
            let a = g()
            let mut b = a.res("123")
            b = c
        }
        """

    @should_pass_compilation()
    def test_valid_postfix_expression_resume_coroutine_on_generator_object_mut(self):
        """
        cor g() -> std::generator::Gen[Yield=&mut std::number::bigint::BigInt, Send=std::string::Str] {
            gen &mut 1
        }

        fun f(c: &mut std::number::bigint::BigInt) -> std::void::Void {
            let a = g()
            let mut b = a.res("123")
            b = c
        }
        """

    @should_pass_compilation()
    def test_valid_postfix_expression_resume_coroutine_void(self):
        """
        cor g() -> std::generator::Gen[Yield=std::number::bigint::BigInt] {
            gen 1
            gen 2
        }

        fun f() -> std::void::Void {
            let a = g()
            let b = a.res()
            let c = a.res()
            let d = b
        }
        """
