from unittest import TestCase

from tests._Utils import *


class TestUnaryExpressionOperatorAsyncAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.ExpressionTypeInvalidError)
    def test_invalid_async_bad_target_1(self):
        """
        fun g() -> std::Void {
            async std::Bool
        }
        """

    @should_fail_compilation(SemanticErrors.AsyncFunctionCallInvalidTargetError)
    def test_invalid_async_bad_target_2(self):
        """
        fun g() -> std::Void {
            async 123
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryUsageOfUnpinnedBorrowError)
    def test_invalid_async_unpinned_borrows_1(self):
        """
        fun g(a: &std::BigInt) -> std::Str { ret "hello" }
        fun f() -> std::Void {
            let x = 123
            async g(&x)
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryUsageOfUnpinnedBorrowError)
    def test_invalid_async_unpinned_borrows_2(self):
        """
        fun g(a: &mut std::Bool, b: &std::BigInt) -> std::Str { ret "hello" }
        fun f() -> std::Void {
            let (mut x, y) = (false, 123)
            async g(&mut x, &y)
        }
        """

    @should_pass_compilation()
    def test_valid_async_good_target(self):
        """
        fun f() -> std::Str { ret "hello" }
        fun g() -> std::Void {
            let mut x = async f()
            x = std::Fut[std::Str]()
        }
        """

    @should_pass_compilation()
    def test_valid_async_unpinned_borrows(self):
        """
        fun g(a: &mut std::Bool, b: &std::BigInt) -> std::Str { ret "hello" }
        fun f() -> std::Void {
            let (mut x, y) = (false, 123)
            pin x, y
            async g(&mut x, &y)
        }
        """
