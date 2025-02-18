from unittest import TestCase

from tests._Utils import *


class TestUseStatementAst(CustomTestCase):
    @should_pass_compilation()
    def test_valid_use_statement_simple_alias(self):
        """
        use MyString = std::Str
        use MyBool = std::Bool

        fun f(a: MyString, b: MyBool) -> std::Void { }
        fun g() -> std::Void { f("hello", true) }
        """

    @should_pass_compilation()
    def test_valid_use_statement_local_simple_alias(self):
        """
        fun f() -> std::Void {
            use MyString = std::Str
            use MyBool = std::Bool

            let x: (MyString, MyBool)
            x = ("hello", true)
        }
        """

    @should_pass_compilation()
    def test_valid_use_statement_variant(self):
        """
        use SomeType = std::Str or std::Bool
        fun f(a: SomeType) -> std::Void { }
        fun g() -> std::Void { f("hello") }
        """

    @should_pass_compilation()
    def test_valid_use_statement_local_variant(self):
        """
        fun f() -> std::Void {
            use SomeType = std::Str or std::Bool
            let x: SomeType
            x = "hello"
        }
        """

    @should_pass_compilation()
    def test_valid_use_statement_generics_alias(self):
        """
        use MyVec[T] = std::Vec[T]

        fun f[T](mut a: MyVec[T], replacement: T) -> std::Void {
            let mut x = a.take_head()
            x = replacement
        }

        fun g() -> std::Void {
            let x = std::Vec[std::Str]()
            f(x, "test")
        }
        """

    @should_pass_compilation()
    def test_valid_use_statement_local_generics_alias(self):
        """
        fun f() -> std::Void {
            use MyVec[T] = std::Vec[T]
            let x = MyVec[std::Str]()
        }
        """

    @should_pass_compilation()
    def test_valid_use_statement_nested_generic_alias(self):
        """
        fun f[T](a: std::Opt[T]) -> std::Void { }
        fun g() -> std::Void {
            let x = std::Some(123)
            f(x)
        }
        """
