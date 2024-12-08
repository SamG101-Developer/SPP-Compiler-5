from unittest import TestCase

from tst._Utils import *


class TestObjectInitializerArgumentAst(TestCase):
    @should_fail_compilation(SemanticErrors.ExpressionTypeInvalidError)
    def test_invalid_object_initializer_named_argument_expression_type(self):
        """
        cls Foo {
            a: std::BigInt
        }

        fun f() -> std::Void {
            let foo = Foo(a=std::BigInt)
        }
        """

    @should_pass_compilation()
    def test_valid_object_initializer_named_argument(self):
        """
        cls Foo {
            a: std::BigInt
        }

        fun f() -> std::Void {
            let foo = Foo(a=1)
        }
        """

    @should_pass_compilation()
    def test_valid_object_initializer_unnamed_argument(self):
        """
        cls Foo {
            a: std::BigInt
        }

        fun f() -> std::Void {
            let a = 1
            let foo = Foo(a)
        }
        """
