from tests._Utils import *


class TestPostfixExpressionStepKeywordAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.ExpressionNotGeneratorError)
    def test_invalid_postfix_expression_step_keyword_type_mismatch(self):
        """
        fun f() -> std::Void {
            123.step()
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_invalid_postfix_expression_step_borrow_invalidation_1(self):
        """
        cor x() -> std::Gen[Yield=std::BigInt, Send=std::BigInt] {
            let (a, b) = (1, 2)
            gen &a
            gen &b
        }

        fun f() -> std::Void {
            let generator = x()
            let a = generator.step(0)
            let b = generator.step(0)
            let c = a
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_invalid_postfix_expression_step_borrow_invalidation_2(self):
        """
        cor x() -> std::Gen[Yield=std::BigInt, Send=std::BigInt] {
            let (a, b) = (1, 2)
            gen &a
            gen &b
        }

        fun f() -> std::Void {
            let generator = x()
            let a = generator.step(0)
            let b = generator.step(0)
            let c = generator.step(0)
            let d = a
        }
        """

    @should_pass_compilation()
    def test_valid_postfix_expression_step_keyword(self):
        """
        cor x() -> std::Gen[Yield=std::BigInt, Send=std::Str] {
            gen 1
        }

        fun f() -> std::Void {
            let generator = x()
            let a = generator.step("hello")
        }
        """

    @should_pass_compilation()
    def test_valid_postfix_expression_step_keyword_send_void(self):
        """
        cor x() -> std::Gen[Yield=std::BigInt, Send=std::Void] {
            gen 1
        }

        fun f() -> std::Void {
            let generator = x()
            let a = generator.step()
        }
        """
