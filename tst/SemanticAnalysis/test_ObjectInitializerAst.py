from unittest import TestCase

from tst._Utils import *


class TestObjectInitializerAst(TestCase):
    @should_fail_compilation(SemanticErrors.GenericTypeInvalidUsageError)
    def test_generic_type_invalid_usage(self):
        """
        fun f[T]() -> std::Void {
            let foo = T()
        }
        """

    @should_pass_compilation()
    def test_valid_object_initializer(self):
        """
        cls Foo {
            a: std::BigInt
        }

        fun f() -> std::Void {
            let foo = Foo(a=1)
        }
        """
