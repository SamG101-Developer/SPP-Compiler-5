from tests._Utils import *


class TestTypeStatementAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.InvalidConventionLocationError)
    def test_invalid_type_statement_old_type_convention_mut(self):
        """
        type MyType = &mut std::boolean::Bool
        """

    @should_fail_compilation(SemanticErrors.InvalidConventionLocationError)
    def test_invalid_type_statement_old_type_convention_ref(self):
        """
        type MyType = &std::boolean::Bool
        """

    @should_pass_compilation()
    def test_valid_type_statement_simple_alias(self):
        """
        type MyString = std::string::Str
        type MyBool = std::boolean::Bool

        fun f(a: MyString, b: MyBool) -> std::void::Void { }
        fun g() -> std::void::Void { f("hello", true) }
        """

    @should_pass_compilation()
    def test_valid_type_statement_local_simple_alias(self):
        """
        fun f() -> std::void::Void {
            type MyString = std::string::Str
            type MyBool = std::boolean::Bool

            let x: (MyString, MyBool)
            x = ("hello", true)
        }
        """

    @should_pass_compilation()
    def test_valid_type_statement_variant(self):
        """
        type SomeType = std::string::Str or std::boolean::Bool
        fun f(a: SomeType) -> std::void::Void { }
        fun g() -> std::void::Void { f("hello") }
        """

    @should_pass_compilation()
    def test_valid_type_statement_local_variant(self):
        """
        fun f() -> std::void::Void {
            type SomeType = std::string::Str or std::boolean::Bool
            let x: SomeType
            x = "hello"
        }
        """

    @should_pass_compilation()
    def test_valid_type_statement_generics_alias(self):
        """
        type MyVec[T] = std::vector::Vec[T]

        fun f[T](mut a: MyVec[T], replacement: T) -> std::void::Void {
            # let mut x = a.take_head()
            # x = replacement
        }

        fun g() -> std::void::Void {
            let x = std::vector::Vec[std::string::Str]()
            f(x, "test")
        }
        """

    @should_pass_compilation()
    def test_valid_type_statement_local_generics_alias(self):
        """
        fun f() -> std::void::Void {
            type MyVec[T] = std::vector::Vec[T]
            let x = MyVec[std::string::Str]()
        }
        """

    @should_pass_compilation()
    def test_valid_type_statement_nested_generic_alias(self):
        """
        fun f[T](a: std::option::Opt[T]) -> std::void::Void { }
        fun g() -> std::void::Void {
            let x = std::option::Some(val=123)
            f(x)
        }
        """

    @should_pass_compilation()
    def test_valid_type_statement_reduction_type_generic(self):
        """
        type MyVec[T] = std::vector::Vec[T]

        fun f[T](a: MyVec[T]) -> std::void::Void { }
        """
