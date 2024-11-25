from unittest import TestCase

from tst._Utils import *


class ObjectInitializerArgumentGroupAst(TestCase):
    @should_fail_compilation(SemanticErrors.IdentifierDuplicationError)
    def test_invalid_object_initializer_argument_group_duplicate_argument_names(self):
        """
            cls Foo {
                a: std::BigInt
                b: std::BigInt
            }
            
            fun f() -> std::Void {
                let foo = Foo(a=1, a=2)
            }
        """

    @should_fail_compilation(SemanticErrors.ObjectInitializerMultipleSupArgumentsError)
    def test_invalid_object_initializer_argument_group_multiple_def_arguments(self):
        """
            cls Foo {
                a: std::BigInt
            }
            
            fun f(d1: Foo, d2: Foo) -> std::Void {
                let foo = Foo(else=d1, else=d2)
            }
        """

    @should_fail_compilation(SemanticErrors.ObjectInitializerMultipleSupArgumentsError)
    def test_invalid_object_initializer_argument_group_multiple_sup_arguments(self):
        """
            cls Foo {
                a: std::BigInt
            }
            
            fun f() -> std::Void {
                let foo = Foo(sup=(1,), sup=(2,))
            }
        """

    @should_fail_compilation(SemanticErrors.ArgumentRequiredNameMissingError)
    def test_invalid_object_initializer_argument_group_missing_attribute(self):
        """
            cls Foo {
                a: std::BigInt
                b: std::BigInt
            }
            
            fun f() -> std::Void {
                let foo = Foo(a=1)
            }
        """

    @should_fail_compilation(SemanticErrors.ArgumentNameInvalidError)
    def test_invalid_object_initializer_argument_group_invalid_attribute(self):
        """
            cls Foo {
                a: std::BigInt
            }
            
            fun f() -> std::Void {
                let foo = Foo(a=1, b=1)
            }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_object_initializer_argument_group_type_mismatch(self):
        """
            cls Foo {
                a: std::BigInt
            }

            fun f() -> std::Void {
                let foo = Foo(a=true)
            }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_object_initializer_argument_group_def_type_mismatch(self):
        """
            cls Foo {
                a: std::BigInt
            }

            fun f() -> std::Void {
                let foo = Foo(else=false)
            }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_object_initializer_argument_group_sup_type_mismatch(self):
        """
            cls Foo {
                a: std::BigInt
            }

            fun f() -> std::Void {
                let foo = Foo(a=1, sup=1)
            }
        """

    @should_fail_compilation(SemanticErrors.ArgumentRequiredNameMissingError)
    def test_invalid_object_initializer_argument_group_missing_sup(self):
        """
            cls Foo {
                a: std::BigInt
            }

            cls Bar {
                b: std::BigInt
            }

            sup Foo ext Bar { }

            fun f() -> std::Void {
                let foo = Foo(sup=())
            }
        """

    @should_fail_compilation(SemanticErrors.ArgumentNameInvalidError)
    def test_invalid_object_initializer_argument_group_invalid_sup(self):
        """
            cls Foo {
                a: std::BigInt
            }

            cls Bar {
                b: std::BigInt
            }

            sup Foo ext Bar { }

            fun f() -> std::Void {
                let foo = Foo(a=1, sup=(Bar(b=4), false))
            }
        """

    @should_pass_compilation()
    def test_valid_object_initializer_argument_group(self):
        """
            cls Foo {
                a: std::BigInt
                b: std::BigInt
            }

            fun f() -> std::Void {
                let foo = Foo(a=1, b=2)
            }
        """

    @should_pass_compilation()
    def test_valid_object_initializer_argument_group_default(self):
        """
            cls Foo {
                a: std::BigInt
            }

            fun f(d: Foo) -> std::Void {
                let foo = Foo(else=d)
            }
        """

    @should_pass_compilation()
    def test_valid_object_initializer_argument_group_sup(self):
        """
            cls Foo {
                a: std::BigInt
            }

            cls Bar {
                b: std::BigInt
            }

            sup Foo ext Bar { }

            fun f(b: Bar) -> std::Void {
                let foo = Foo(a=1, sup=(b,))
            }
        """
