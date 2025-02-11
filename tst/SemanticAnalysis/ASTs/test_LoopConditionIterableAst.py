from tst._Utils import *
import json_fix


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

    @should_pass_compilation()
    def test_valid_loop_condition_iterable(self):
        """
        fun f() -> std::Void {
            let v = std::Vec[std::Str]()
            loop mut x in v.iter_mut() { }
        }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_loop_assign_to_iterator(self):
        """
        fun f() -> std::Void {
            let v = std::Vec[std::Str]()
            loop mut x in v.iter_mut() {
                x = "hello"
            }
        }
        """

    @should_pass_compilation()
    def test_valid_loop_assign_to_iterator(self):
        """
        fun f(s: &mut std::Str) -> std::Void {
            let v = std::Vec[std::Str]()
            loop mut x in v.iter_mut() {
                x = s
            }
        }
        """
