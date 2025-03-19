from tests._Utils import *


class TestUnaryExpressionOperatorAsyncAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.ExpressionTypeInvalidError)
    def test_invalid_async_bad_target_1(self):
        """
        fun g() -> std::void::Void {
            async std::boolean::Bool
        }
        """

    @should_fail_compilation(SemanticErrors.AsyncFunctionCallInvalidTargetError)
    def test_invalid_async_bad_target_2(self):
        """
        fun g() -> std::void::Void {
            async 123
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_invalid_async_invalidated_by_moving_borrow(self):
        """
        fun f() -> std::string::Str { ret "hello" }
        fun g() -> std::void::Void {
            let x = 123
            let future = async c(&x)
            let y = x
            let h = future
        }
        """

    @should_pass_compilation()
    def test_valid_async_good_target(self):
        """
        fun f() -> std::string::Str { ret "hello" }
        fun g() -> std::void::Void {
            let mut x = async f()
            x = std::future::Fut[std::string::Str]()
        }
        """

    @should_pass_compilation()
    def test_valid_async_good_target_with_args(self):
        """
        fun f(a: &std::string::Str) -> std::void::Void { }
        fun g() -> std::void::Void {
            let mut x = async f("hello")
            x = std::future::Fut[std::void::Void]()
        }
        """
