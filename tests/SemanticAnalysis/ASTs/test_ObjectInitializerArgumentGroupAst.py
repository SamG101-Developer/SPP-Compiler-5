from unittest import TestCase

from tests._Utils import *


class TestObjectInitializerArgumentGroupAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.IdentifierDuplicationError)
    def test_invalid_object_initializer_argument_group_duplicate_argument_names(self):
        """
        cls Foo {
            a: std::number::bigint::BigInt
            b: std::number::bigint::BigInt
        }

        fun f() -> std::void::Void {
            let foo = Foo(a=1, a=2)
        }
        """

    @should_fail_compilation(SemanticErrors.ArgumentNameInvalidError)
    def test_invalid_object_initializer_argument_group_invalid_attribute(self):
        """
        cls Foo {
            a: std::number::bigint::BigInt
        }

        fun f() -> std::void::Void {
            let foo = Foo(a=1, b=1)
        }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_object_initializer_argument_group_type_mismatch(self):
        """
        cls Foo {
            a: std::number::bigint::BigInt
        }

        fun f() -> std::void::Void {
            let foo = Foo(a=true)
        }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_object_initializer_argument_group_def_type_mismatch(self):
        """
        cls Foo {
            a: std::number::bigint::BigInt
        }

        fun f() -> std::void::Void {
            let b = true
            let foo = Foo(..b)
        }
        """

    @should_pass_compilation()
    def test_valid_object_initializer_argument_group(self):
        """
        cls Foo {
            a: std::number::bigint::BigInt
            b: std::number::bigint::BigInt
        }

        fun f() -> std::void::Void {
            let foo = Foo(a=1, b=2)
        }
        """

    @should_pass_compilation()
    def test_valid_object_initializer_argument_group_missing_attribute(self):
        """
        cls Foo {
            a: std::number::bigint::BigInt
            b: std::number::bigint::BigInt
        }

        fun f() -> std::void::Void {
            let foo = Foo(a=1)
        }
        """

    @should_pass_compilation()
    def test_valid_object_initializer_argument_group_default(self):
        """
        cls Foo {
            a: std::number::bigint::BigInt
        }

        fun f(d: Foo) -> std::void::Void {
            let foo = Foo(..d)
        }
        """

    @should_pass_compilation()
    def test_valid_object_initializer_superclasses(self):
        """
        cls A {
            a: std::number::bigint::BigInt
        }

        cls B {
            b: std::number::bigint::BigInt
        }

        sup B ext A { }

        fun f() -> std::void::Void {
            let foo = B(a=1, b=2)
        }
        """
