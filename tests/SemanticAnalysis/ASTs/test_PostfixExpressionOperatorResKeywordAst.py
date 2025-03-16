from tests._Utils import *


class TestPostfixExpressionResKeywordAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.ExpressionNotGeneratorError)
    def test_invalid_postfix_expression_res_keyword_type_mismatch(self):
        """
        fun f() -> std::void::Void {
            123.res()
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_invalid_postfix_expression_res_borrow_invalidation_1(self):
        """
        cor x() -> std::generator::Gen[Yield=std::number::BigInt, Send=std::number::BigInt] {
            let (a, b) = (1, 2)
            gen &a
            gen &b
        }

        fun f() -> std::void::Void {
            let generator = x()
            let a = generator.res(0)
            let b = generator.res(0)
            let c = a
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_invalid_postfix_expression_res_borrow_invalidation_2(self):
        """
        cor x() -> std::generator::Gen[Yield=std::number::BigInt, Send=std::number::BigInt] {
            let (a, b) = (1, 2)
            gen &a
            gen &b
        }

        fun f() -> std::void::Void {
            let generator = x()
            let a = generator.res(0)
            let b = generator.res(0)
            let c = generator.res(0)
            let d = a
        }
        """

    @should_pass_compilation()
    def test_valid_postfix_expression_res_keyword(self):
        """
        cor x() -> std::generator::Gen[Yield=std::number::BigInt, Send=std::string::Str] {
            gen 1
        }

        fun f() -> std::void::Void {
            let generator = x()
            let a = generator.res("hello")
        }
        """

    @should_pass_compilation()
    def test_valid_postfix_expression_res_keyword_send_void(self):
        """
        cor x() -> std::generator::Gen[Yield=std::number::BigInt, Send=std::boolean::Bool] {
            gen 1
        }

        fun f() -> std::void::Void {
            let generator = x()
            let a = generator.res(true)
        }
        """
