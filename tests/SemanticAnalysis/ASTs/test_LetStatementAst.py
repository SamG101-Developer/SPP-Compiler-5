from tests._Utils import *


class TestLetStatementAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.ExpressionTypeInvalidError)
    def test_invalid_expression_type(self):
        """
        fun f() -> std::void::Void {
            let x = std::boolean::Bool
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

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_explicit_type_hint_1(self):
        """
        fun f() -> std::void::Void {
            let x: std::boolean::Bool = 123
        }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_explicit_type_hint_2(self):
        """
        fun f(b: &std::boolean::Bool) -> std::void::Void {
            let x: std::boolean::Bool = b
        }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_explicit_type_hint_3(self):
        """
        fun f(b: std::boolean::Bool) -> std::void::Void {
            let x: &std::boolean::Bool = b
        }
        """

    @should_fail_compilation(SemanticErrors.InvalidTypeAnnotationError)
    def test_invalid_explicit_type_hint_2(self):
        """
        cls A { a: std::boolean::Bool }

        fun f(aa: A) -> std::void::Void {
            let A(a): A = aa
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

    @should_pass_compilation()
    def test_valid_type_hint_1(self):
        """
        fun f(b: std::boolean::Bool) -> std::void::Void {
            let x: std::boolean::Bool = b
        }
        """

    @should_pass_compilation()
    def test_valid_type_hint_2(self):
        """
        fun f(b: &mut std::boolean::Bool) -> std::void::Void {
            let x: &mut std::boolean::Bool = b
        }
        """

    @should_pass_compilation()
    def test_valid_type_hint_3(self):
        """
        fun f(b: &std::boolean::Bool) -> std::void::Void {
            let x: &std::boolean::Bool = b
        }
        """

    @should_pass_compilation()
    def test_valid_type_hint_variant_1(self):
        """
        fun f() -> std::void::Void {
            let x: std::string::Str or std::number::bigint::BigInt = "hello world"
        }
        """

    @should_pass_compilation()
    def test_valid_type_hint_variant_1(self):
        """
        fun f() -> std::void::Void {
            let x: std::string::Str or std::number::bigint::BigInt or std::boolean::Bool = false
        }
        """

    @should_pass_compilation()
    def test_valid_type_hint_variant_2(self):
        """
        fun f() -> std::void::Void {
            let x: std::option::Opt[std::number::bigint::BigInt] = std::option::Some(val=123)
        }
        """
