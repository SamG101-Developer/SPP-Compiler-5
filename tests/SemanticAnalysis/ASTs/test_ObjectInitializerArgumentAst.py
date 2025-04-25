from tests._Utils import *


class TestObjectInitializerArgumentAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.InvalidObjectInitializerArgumentError)
    def test_invalid_object_initializer_unnamed_argument_1(self):
        """
        cls Foo {
            a: std::number::bigint::BigInt
        }

        fun f() -> std::void::Void {
            let foo = Foo(123)
        }
        """

    @should_fail_compilation(SemanticErrors.InvalidObjectInitializerArgumentError)
    def test_invalid_object_initializer_unnamed_argument_2(self):
        """
        cls Foo[T] {
            a: T
        }

        fun f() -> std::void::Void {
            let foo = Foo(123)
        }
        """

    @should_fail_compilation(SemanticErrors.ExpressionTypeInvalidError)
    def test_invalid_object_initializer_named_argument_expression_type(self):
        """
        cls Foo {
            a: std::number::bigint::BigInt
        }

        fun f() -> std::void::Void {
            let foo = Foo(a=std::number::bigint::BigInt)
        }
        """

    @should_pass_compilation()
    def test_valid_object_initializer_named_argument(self):
        """
        cls Foo {
            a: std::number::bigint::BigInt
        }

        fun f() -> std::void::Void {
            let foo = Foo(a=1)
        }
        """

    @should_pass_compilation()
    def test_valid_object_initializer_unnamed_argument(self):
        """
        cls Foo {
            a: std::number::bigint::BigInt
        }

        fun f() -> std::void::Void {
            let a = 1
            let foo = Foo(a)
        }
        """
