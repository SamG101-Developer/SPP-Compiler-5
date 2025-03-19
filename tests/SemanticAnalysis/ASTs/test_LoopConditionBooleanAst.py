from unittest import TestCase

from tests._Utils import *


class TestLoopConditionBooleanAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.ExpressionTypeInvalidError)
    def test_invalid_loop_condition_boolean_invalid_expression(self):
        """
        fun f() -> std::void::Void {
            loop std::boolean::Bool { }
        }
        """

    @should_fail_compilation(SemanticErrors.ExpressionNotBooleanError)
    def test_invalid_loop_condition_boolean_invalid_type(self):
        """
        fun f() -> std::void::Void {
            loop 1 { }
        }
        """

    @should_pass_compilation()
    def test_valid_loop_condition_boolean(self):
        """
        fun f() -> std::void::Void {
            loop true { }
        }
        """
