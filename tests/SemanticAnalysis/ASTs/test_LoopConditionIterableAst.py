from tests._Utils import *


class TestLoopConditionIterableAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.ExpressionTypeInvalidError)
    def test_invalid_loop_condition_iterable_invalid_expression(self):
        """
        fun f() -> std::void::Void {
            loop x in std::iterator::IterMov[std::string::Str] { }
        }
        """

    @should_fail_compilation(SemanticErrors.ExpressionNotGeneratorError)
    def test_invalid_loop_condition_iterable_invalid_type(self):
        """
        fun f() -> std::void::Void {
            loop x in 0 { }
        }
        """

    @should_pass_compilation()
    def test_valid_loop_condition_iterable(self):
        """
        fun f(y: &mut std::string::Str) -> std::void::Void {
            let mut v = std::vector::Vec[std::string::Str]()
            loop mut x in v.iter_mut() {
                x = y
            }
        }
        """

    @should_pass_compilation()
    def test_valid_loop_condition_iterable_move(self):
        """
        fun f() -> std::void::Void {
            let v = std::vector::Vec[std::string::Str]()
            loop mut x in v.iter_mov() {
                x = "hello"
            }
        }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_loop_assign_to_iterator(self):
        """
        fun f() -> std::void::Void {
            let mut v = std::vector::Vec[std::string::Str]()
            loop mut x in v.iter_mut() {
                x = "hello"
            }
        }
        """

    @should_pass_compilation()
    def test_valid_loop_assign_to_iterator(self):
        """
        fun f(s: &mut std::string::Str) -> std::void::Void {
            let mut v = std::vector::Vec[std::string::Str]()
            loop mut x in v.iter_mut() {
                x = s
            }
        }
        """
