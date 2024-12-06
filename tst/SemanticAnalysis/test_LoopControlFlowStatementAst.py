from unittest import TestCase

from tst._Utils import *


class TestLoopControlFlowStatementAst(TestCase):
    @should_fail_compilation(SemanticErrors.ExpressionTypeInvalidError)
    def test_invalid_control_flow_statement_exit_expr(self):
        """
        fun f() -> std::Void {
            loop true {
                exit std::Bool
            }
        }
        """

    @should_fail_compilation(SemanticErrors.LoopTooManyControlFlowStatementsError)
    def test_invalid_control_flow_statement_too_many_control_statements(self):
        """
        fun f() -> std::Void {
            loop true {
                exit exit
            }
        }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_control_flow_statement_exit_types_1(self):
        """
        fun f() -> std::Void {
            loop true {
                exit 1
                exit true
            }
        }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_control_flow_statement_exit_types_2(self):
        """
        fun f() -> std::Void {
            loop true {
                loop true {
                    exit exit 1
                }
                exit true
            }
        }
        """

    @should_pass_compilation()
    def test_valid_control_flow_statement_exit_types(self):
        """
        fun f() -> std::Void {
            loop true {
                exit 1
                exit 1
            }
        }
        """

    @should_pass_compilation()
    def test_valid_control_flow_statement_exit_skip(self):
        """
        fun f() -> std::Void {
            loop true {
                loop true {
                    exit skip
                }
                skip
            }
        }
        """

    @should_pass_compilation()
    def test_valid_control_flow_statement_exit_types_nested(self):
        """
        fun f() -> std::Void {
            loop true {
                loop true {
                    exit exit 1
                }
                exit 1
            }
        }
        """

    @should_pass_compilation()
    def test_valid_control_flow_statement_exit_types_assigned(self):
        """
        fun f() -> std::Void {
            let mut x = loop true {
                exit "hello"
            }
            x = "goodbye"
        }
        """
