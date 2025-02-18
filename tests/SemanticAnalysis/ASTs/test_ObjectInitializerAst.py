from unittest import TestCase

from tests._Utils import *


class TestObjectInitializerAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.GenericTypeInvalidUsageError)
    def test_generic_type_invalid_usage(self):
        """
        fun f[T]() -> std::Void {
            let foo = T()
        }
        """

    @should_fail_compilation(SemanticErrors.ObjectInitializerAbstractClassError)
    def test_object_initializer_abstract_class(self):
        """
        cls Foo {
            a: std::BigInt
        }

        sup Foo {
            @abstract_method
            fun f() -> std::Void { }
        }

        fun f() -> std::Void {
            let foo = Foo()
        }
        """

    @should_fail_compilation(SemanticErrors.ObjectInitializerAbstractClassError)
    def test_object_initializer_abstract_base_class(self):
        """
        cls Foo {
            a: std::BigInt
        }

        cls Bar { }

        sup Foo {
            @abstract_method
            fun f() -> std::Void { }
        }

        sup Bar ext Foo { }

        fun f() -> std::Void {
            let foo = Bar()
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

    @should_pass_compilation()
    def test_object_initializer_overridden_abstract_base_class(self):
        """
        cls Foo {
            a: std::BigInt
        }

        cls Bar { }

        sup Foo {
            @abstract_method
            fun f() -> std::Void { }
        }

        sup Bar ext Foo {
            fun f() -> std::Void { }
        }

        fun f() -> std::Void {
            let foo = Bar()
        }
        """
