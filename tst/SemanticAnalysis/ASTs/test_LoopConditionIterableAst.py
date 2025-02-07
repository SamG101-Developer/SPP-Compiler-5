from unittest import TestCase

from tst._Utils import *


class TestLoopConditionIterableAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.ExpressionTypeInvalidError)
    def test_invalid_loop_condition_iterable_invalid_expression(self):
        """
        fun f() -> std::Void {
            loop x in std::IterMov[std::Str] { }
        }
        """

    @should_fail_compilation(SemanticErrors.ExpressionNotGeneratorError)
    def test_invalid_loop_condition_iterable_invalid_type(self):
        """
        fun f() -> std::Void {
            loop x in 0 { }
        }
        """

    # Todo: this should actually fail because v isn't mutable
    @should_pass_compilation()
    def test_valid_loop_condition_iterable(self):
        """
        fun f() -> std::Void {
            let v = std::Vec[std::Str]()
            loop mut x in v.iter_mut() { }
        }
        """
