from unittest import TestCase

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

    @should_fail_compilation(SemanticErrors.MemoryUsageOfUnpinnedBorrowError)
    def test_invalid_async_unpinned_borrows_1(self):
        """
        fun g(a: &std::number::BigInt) -> std::string::Str { ret "hello" }
        fun f() -> std::void::Void {
            let x = 123
            async g(&x)
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryUsageOfUnpinnedBorrowError)
    def test_invalid_async_unpinned_borrows_2(self):
        """
        fun g(a: &mut std::boolean::Bool, b: &std::number::BigInt) -> std::string::Str { ret "hello" }
        fun f() -> std::void::Void {
            let (mut x, y) = (false, 123)
            async g(&mut x, &y)
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
    def test_valid_async_unpinned_borrows(self):
        """
        fun g(a: &mut std::boolean::Bool, b: &std::number::BigInt) -> std::string::Str { ret "hello" }
        fun f() -> std::void::Void {
            let (mut x, y) = (false, 123)
            pin x, y
            async g(&mut x, &y)
        }
        """
