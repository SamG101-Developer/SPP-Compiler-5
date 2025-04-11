from tests._Utils import *


class TestObjectInitializerAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.GenericTypeInvalidUsageError)
    def test_generic_type_invalid_usage(self):
        """
        fun f[T]() -> std::void::Void {
            let foo = T()
        }
        """

    @should_pass_compilation()
    def test_valid_object_initializer(self):
        """
        cls Foo {
            a: std::number::BigInt
        }

        fun f() -> std::void::Void {
            let foo = Foo(a=1)
        }
        """

    @should_pass_compilation()
    def test_object_initializer_overridden_abstract_base_class(self):
        """
        cls Foo {
            a: std::number::BigInt
        }

        cls Bar { }

        sup Foo {
            @abstract_method
            fun f() -> std::void::Void { }
        }

        sup Bar ext Foo {
            fun f() -> std::void::Void { }
        }

        fun f() -> std::void::Void {
            let foo = Bar()
        }
        """
