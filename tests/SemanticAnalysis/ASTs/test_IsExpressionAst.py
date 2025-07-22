from tests._Utils import *


class TestIsExpressionAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_is_expression_incorrect_type_destructure(self):
        """
        cls Point {
            x: std::bignum::bigint::BigInt
            y: std::bignum::bigint::BigInt
        }
        fun f() -> std::void::Void {
            let a: Point = Point(x=1, y=2)
            case a is std::string::Str(..) { }
        }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_is_expression_incorrect_type_variant_destructure(self):
        """
        fun f() -> std::void::Void {
            let a: std::string::Str or std::boolean::Bool = "hello"
            case a is std::bignum::bigint::BigInt() { }
        }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_is_expression_incorrect_generic_destructure(self):
        """
        cls Point[T] {
            x: T
            y: T
        }
        fun f() -> std::void::Void {
            let a: Point[std::bignum::bigint::BigInt] = Point[std::bignum::bigint::BigInt](x=1, y=2)
            case a is Point[std::string::Str](x, y) { }
        }
        """

    @should_pass_compilation()
    def test_valid_is_expression_correct_type(self):
        """
        cls Point {
            x: std::bignum::bigint::BigInt
            y: std::bignum::bigint::BigInt
        }
        fun f() -> std::void::Void {
            let a: Point = Point(x=1, y=2)
            case a is Point(x, y) { }
        }
        """

    @should_pass_compilation()
    def test_valid_is_expression_correct_type_variant(self):
        """
        fun f() -> std::void::Void {
            let a: std::string::Str or std::boolean::Bool = "hello"
            case a is std::string::Str(..) { }
        }
        """

    @should_pass_compilation()
    def test_valid_is_expression_correct_type_generic(self):
        """
        cls Point[T] {
            x: T
            y: T
        }
        fun f() -> std::void::Void {
            let a: Point[std::bignum::bigint::BigInt] = Point[std::bignum::bigint::BigInt](x=1, y=2)
            case a is Point[std::bignum::bigint::BigInt](x, y) { }
        }
        """
