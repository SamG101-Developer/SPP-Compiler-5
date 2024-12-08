from unittest import TestCase

from tst._Utils import *


class TestCoroutinePrototypeAst(TestCase):
    @should_fail_compilation(SemanticErrors.FunctionCoroutineInvalidReturnTypeError)
    def test_invalid_coroutine_invalid_return_type(self):
        """
        cor c() -> std::Void { }
        """

    @should_fail_compilation(SemanticErrors.MemoryUsageOfUnpinnedBorrowError)
    def test_invalid_coroutine_invalid_unpinned_borrows_1(self):
        """
        cor c(a: &std::BigInt) -> std::GenMov[std::BigInt] { }
        fun f() -> std::Void {
            let x = 123
            c(&x)
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryUsageOfUnpinnedBorrowError)
    def test_invalid_coroutine_invalid_unpinned_borrows_2(self):
        """
        cor c(a: &mut std::Bool, b: &std::BigInt) -> std::GenMov[std::BigInt] { }
        fun f() -> std::Void {
            let (mut x, y) = (false, 123)
            c(&mut x, &y)
        }
        """

    @should_pass_compilation()
    def test_valid_coroutine_valid_return_type_1(self):
        """
        cor c() -> std::GenMov[std::BigInt] { }
        """

    @should_pass_compilation()
    def test_valid_coroutine_valid_return_type_2(self):
        """
        cor c() -> std::GenMut[std::BigInt] { }
        """

    @should_pass_compilation()
    def test_valid_coroutine_valid_return_type_3(self):
        """
        cor c() -> std::GenRef[std::BigInt] { }
        """

    @should_pass_compilation()
    def test_valid_coroutine_pinned_borrows(self):
        """
        cor c(a: &mut std::Bool, b: &std::BigInt) -> std::GenMov[std::BigInt] { }
        fun f() -> std::Void {
            let (mut x, y) = (false, 123)
            pin x, y
            c(&mut x, &y)
        }
        """
