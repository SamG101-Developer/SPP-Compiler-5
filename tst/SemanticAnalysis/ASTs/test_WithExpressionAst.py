from unittest import TestCase

from tst._Utils import *


class WithExpressionAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.ExpressionTypeInvalidError)
    def test_invalid_expression(self):
        """
        fun f() -> std::Void {
            with std::Str { }
        }
        """

    @should_fail_compilation(SemanticErrors.WithExpressionNonContextualConditionError)
    def test_invalid_expression_type(self):
        """
        fun f() -> std::Void {
            with 42 { }
        }
        """

    @should_pass_compilation()
    def test_valid_with_expression(self):
        """
        cls A { }
        sup A ext std::CtxRef[std::Bool] { }

        fun f(a: A) -> std::Void {
            with a {
                let x = 42
            }
        }
        """

    @should_pass_compilation()
    def test_valid_with_expression_alias(self):
        """
        cls A { }
        sup A ext std::CtxRef[std::Bool] {
            fun enter(&self) -> std::Bool { ret true }
        }

        fun f(a: A) -> std::Void {
            with b = a {
                let x = 42
            }
        }
        """
