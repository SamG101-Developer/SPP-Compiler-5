from tests._Utils import *


class TestLetStatementAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.ExpressionTypeInvalidError)
    def test_invalid_expression_type(self):
        """
        fun f() -> std::Void {
            let x = std::Bool
        }
        """

    @should_fail_compilation(SemanticErrors.TypeVoidInvalidUsageError)
    def test_invalid_type_void(self):
        """
        fun f() -> std::Void {
            let x: std::Void
        }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_type_convention(self):
        """
        fun f(b: &std::Bool) -> std::Void {
            let mut x: &mut std::Bool
            x = b
        }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_variant_destructure(self):
        """
        cls A { a: std::Bool }
        cls B { b: std::Bool }

        fun f(value: A or B) -> std::Void {
            let A(a) = value
        }
        """

    @should_pass_compilation()
    def test_valid_let_statement_uninitialized(self):
        """
        fun f() -> std::Void {
            let x: std::Bool
        }
        """

    @should_pass_compilation()
    def test_valid_let_statement_uninitialized_with_convention(self):
        """
        fun f(x: &std::Bool) -> std::Void {
            let mut y: &std::Bool
            y = x
        }
        """

    @should_pass_compilation()
    def test_valid_let_statement_initialized(self):
        """
        fun f() -> std::Void {
            let x = true
        }
        """

    @should_pass_compilation()
    def test_valid_convention(self):
        """
        fun f(b: &std::Bool) -> std::Void {
            let mut x: & std::Bool
            x = b
        }
        """
