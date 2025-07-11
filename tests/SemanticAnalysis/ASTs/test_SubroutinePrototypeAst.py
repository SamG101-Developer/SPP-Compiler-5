from tests._Utils import *


class TestSubroutinePrototypeAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.FunctionSubroutineMissingReturnStatementError)
    def test_invalid_subroutine_missing_ret_statement(self):
        """
        fun c() -> std::number::bigint::BigInt {
            let x = 123
        }
        """

    @should_pass_compilation()
    def test_valid_subroutine_valid_no_ret_statement_void(self):
        """
        fun c() -> std::void::Void { }
        """

    @should_pass_compilation()
    def test_valid_subroutine_valid_ret_statement_void(self):
        """
        fun c() -> std::void::Void {
            ret
        }
        """

    @should_pass_compilation()
    def test_valid_subroutine_valid_ret_statement_non_void(self):
        """
        fun c() -> std::number::bigint::BigInt {
            ret 123
        }
        """
