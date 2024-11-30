from unittest import TestCase

from tst._Utils import *


class TestSubroutinePrototypeAst(TestCase):
    @should_fail_compilation(SemanticErrors.FunctionSubroutineMissingReturnStatementError)
    def test_invalid_subroutine_missing_ret_statement(self):
        """
        fun c() -> std::BigInt {
            let x = 123
        }
        """

    @should_pass_compilation()
    def test_valid_subroutine_valid_no_ret_statement_void(self):
        """
        fun c() -> std::Void { }
        """

    @should_pass_compilation()
    def test_valid_subroutine_valid_ret_statement_void(self):
        """
        fun c() -> std::Void {
            ret
        }
        """

    @should_pass_compilation()
    def test_valid_subroutine_valid_ret_statement_non_void(self):
        """
        fun c() -> std::BigInt {
            ret 123
        }
        """
