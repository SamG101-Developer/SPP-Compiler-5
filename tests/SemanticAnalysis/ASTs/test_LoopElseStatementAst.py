from unittest import TestCase

from tests._Utils import *


class TestLoopElseStatementAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_loop_else_statement_return_type_assigned_from(self):
        """
        fun f() -> std::void::Void {
            let y = loop true {
                exit true
            }
            else {
                1
            }
        }
        """

    @should_pass_compilation()
    def test_invalid_loop_else_statement_return_type_not_assigned_from(self):
        """
        fun f() -> std::void::Void {
            loop true {
                exit true
            }
            else {
                1
            }
        }
        """

    @should_pass_compilation()
    def test_valid_loop_else_statement_return_type(self):
        """
        fun f() -> std::void::Void {
            loop true {
                exit true
            }
            else {
                true
            }
        }
        """
