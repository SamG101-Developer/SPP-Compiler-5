from tests._Utils import *


class TestRetStatementAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.FunctionCoroutineContainsReturnStatementError)
    def test_invalid_ret_statement_in_coroutine_with_expr(self):
        """
        cor f() -> std::generator::Gen[std::number::bigint::BigInt] {
            ret 123
        }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_ret_statement_type_mismatch(self):
        """
        fun f() -> std::number::bigint::BigInt {
            ret "hello world"
        }
        """

    @should_pass_compilation()
    def test_valid_ret_statement_in_coroutine_no_expr(self):
        """
        cor f() -> std::generator::Gen[std::number::bigint::BigInt] {
            ret
        }
        """

    @should_pass_compilation()
    def test_valid_ret_statement_in_subroutine_no_expr(self):
        """
        fun f() -> std::void::Void {
            ret
        }
        """

    @should_pass_compilation()
    def test_valid_ret_statement_in_subroutine_with_expr(self):
        """
        fun f() -> std::number::bigint::BigInt {
            ret 1
        }
        """
