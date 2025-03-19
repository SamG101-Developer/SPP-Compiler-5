from tests._Utils import *


class TestLetStatementAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.ExpressionTypeInvalidError)
    def test_invalid_expression_type(self):
        """
        fun f() -> std::void::Void {
            let x = std::boolean::Bool
        }
        """

    @should_fail_compilation(SemanticErrors.TypeVoidInvalidUsageError)
    def test_invalid_type_void(self):
        """
        fun f() -> std::void::Void {
            let x: std::void::Void
        }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_variant_destructure(self):
        """
        cls A { a: std::boolean::Bool }
        cls B { b: std::boolean::Bool }

        fun f(value: A or B) -> std::void::Void {
            let A(a) = value
        }
        """

    @should_pass_compilation()
    def test_valid_let_statement_uninitialized(self):
        """
        fun f() -> std::void::Void {
            let x: std::boolean::Bool
        }
        """

    @should_pass_compilation()
    def test_valid_let_statement_uninitialized_with_convention(self):
        """
        fun f(x: &std::boolean::Bool) -> std::void::Void {
            let mut y: &std::boolean::Bool
            y = x
        }
        """

    @should_pass_compilation()
    def test_valid_let_statement_initialized(self):
        """
        fun f() -> std::void::Void {
            let x = true
        }
        """

    @should_pass_compilation()
    def test_valid_convention_1(self):
        """
        fun f(b: std::boolean::Bool) -> std::void::Void {
            let mut x: std::boolean::Bool
            x = b
        }
        """

    @should_pass_compilation()
    def test_valid_convention_2(self):
        """
        fun f(b: &mut std::boolean::Bool) -> std::void::Void {
            let mut x: &mut std::boolean::Bool
            x = b
        }
        """

    @should_pass_compilation()
    def test_valid_convention_3(self):
        """
        fun f(b: &std::boolean::Bool) -> std::void::Void {
            let mut x: &std::boolean::Bool
            x = b
        }
        """
