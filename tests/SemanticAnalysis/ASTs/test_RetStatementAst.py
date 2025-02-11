from unittest import TestCase

from tests._Utils import *


class TestRetStatementAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.FunctionCoroutineContainsReturnStatementError)
    def test_invalid_ret_statement_in_coroutine(self):
        """
        cor f() -> std::GenMov[std::BigInt] {
            ret
        }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_ret_statement_type_mismatch(self):
        """
        fun f() -> std::BigInt {
            ret "hello world"
        }
        """

    @should_pass_compilation()
    def test_valid_ret_statement_1(self):
        """
        fun f() -> std::Void {
            ret
        }
        """

    @should_pass_compilation()
    def test_valid_ret_statement_2(self):
        """
        fun f() -> std::BigInt {
            ret 1
        }
        """
