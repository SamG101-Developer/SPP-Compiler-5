from unittest import TestCase

from tst._Utils import *


class TestCoroutinePrototypeAst(TestCase):
    @should_fail_compilation(SemanticErrors.FunctionCoroutineInvalidReturnTypeError)
    def test_invalid_coroutine_invalid_return_type(self):
        """
        cor c() -> std::Void { }
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
