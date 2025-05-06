from tests._Utils import *


class TestUseStatementAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.InvalidConventionLocationError)
    def test_invalid_use_statement_old_type_convention_mut(self):
        """
        use MyType = &mut std::boolean::Bool
        """

    @should_fail_compilation(SemanticErrors.InvalidConventionLocationError)
    def test_invalid_use_statement_old_type_convention_ref(self):
        """
        use MyType = &std::boolean::Bool
        """

    @should_pass_compilation()
    def test_valid_use_statement_simple_alias(self):
        """
        use MyString = std::string::Str
        use MyBool = std::boolean::Bool

        fun f(a: MyString, b: MyBool) -> std::void::Void { }
        fun g() -> std::void::Void { f("hello", true) }
        """

    @should_pass_compilation()
    def test_valid_use_statement_local_simple_alias(self):
        """
        fun f() -> std::void::Void {
            use MyString = std::string::Str
            use MyBool = std::boolean::Bool

            let x: (MyString, MyBool)
            x = ("hello", true)
        }
        """

    @should_pass_compilation()
    def test_valid_use_statement_variant(self):
        """
        use SomeType = std::string::Str or std::boolean::Bool
        fun f(a: SomeType) -> std::void::Void { }
        fun g() -> std::void::Void { f("hello") }
        """

    @should_pass_compilation()
    def test_valid_use_statement_local_variant(self):
        """
        fun f() -> std::void::Void {
            use SomeType = std::string::Str or std::boolean::Bool
            let x: SomeType
            x = "hello"
        }
        """

    @should_pass_compilation()
    def test_valid_use_statement_generics_alias(self):
        """
        use MyVec[T] = std::vector::Vec[T]

        fun f[T](mut a: MyVec[T], replacement: T) -> std::void::Void {
            let mut x = a.take_head()
            x = replacement
        }

        fun g() -> std::void::Void {
            let x = std::vector::Vec[std::string::Str]()
            f(x, "test")
        }
        """

    @should_pass_compilation()
    def test_valid_use_statement_local_generics_alias(self):
        """
        fun f() -> std::void::Void {
            use MyVec[T] = std::vector::Vec[T]
            let x = MyVec[std::string::Str]()
        }
        """

    @should_pass_compilation()
    def test_valid_use_statement_nested_generic_alias(self):
        """
        fun f[T](a: std::option::Opt[T]) -> std::void::Void { }
        fun g() -> std::void::Void {
            let x = std::option::Some(val=123)
            f(x)
        }
        """

    @should_pass_compilation()
    def test_valid_use_statement_reduction(self):
        """
        use std::number::bigint::BigInt
        use std::string::Str
        use std::option::Opt
        """

    @should_pass_compilation()
    def test_valid_use_statement_reduction_use_generic_1(self):
        """
        use std::vector::Vec

        fun f[T](a: Vec[T]) -> std::void::Void { }
        """

    @should_pass_compilation()
    def test_valid_use_statement_reduction_use_generic_2(self):
        """
        use std::array::Arr
        use std::void::Void
        use std::number::usize::USize

        fun f[T, cmp n: USize](a: Arr[T, n]) -> Void { }
        """
