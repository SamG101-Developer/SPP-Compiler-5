from tests._Utils import *


class TestTypeAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.IdentifierUnknownError)
    def test_invalid_unknown_type(self):
        """
        fun f() -> Unknown { }
        """

    @should_fail_compilation(SemanticErrors.IdentifierUnknownError)
    def test_invalid_unknown_namespaced_type(self):
        """
        fun f() -> std::Unknown { }
        """

    @should_fail_compilation(SemanticErrors.IdentifierUnknownError)
    def test_invalid_type_unknown_namespace(self):
        """
        fun f() -> test::Type { }
        """

    @should_fail_compilation(SemanticErrors.IdentifierUnknownError)
    def test_invalid_type_unknown_namespace_nested(self):
        """
        fun f() -> std::other::Unknown { }
        """

    @should_fail_compilation(SemanticErrors.IdentifierUnknownError)
    def test_invalid_type_unknown_nested_type(self):
        """
        fun f() -> std::string::Str::Type { }
        """

    @should_fail_compilation(SemanticErrors.IdentifierUnknownError)
    def test_invalid_type_generic_nested_type(self):
        """
        fun f[T]() -> T::Type { }
        """

    @should_pass_compilation()
    def test_valid_type(self):
        """
        fun f() -> std::void::Void { }
        """

    @should_pass_compilation()
    def test_valid_type_namespaced(self):
        """
        fun f() -> std::void::Void { }
        """

    @should_pass_compilation()
    def test_valid_type_shorthand_optional(self):
        """
        fun f(mut a: std::string::Str?) -> std::void::Void { a = std::option::Some(val="hello") }
        """

    @should_pass_compilation()
    def test_valid_type_shorthand_optional_default(self):
        """
        fun f(a: std::string::Str? = std::option::Some(val="hello")) -> std::void::Void { }
        """

    @should_pass_compilation()
    def test_valid_type_shorthand_variant(self):
        """
        fun f(mut a: std::string::Str or std::boolean::Bool) -> std::void::Void { a = "hello" }
        """

    @should_pass_compilation()
    def test_valid_type_shorthand_variant_default(self):
        """
        fun f(a: std::string::Str or std::boolean::Bool = "hello") -> std::void::Void { }
        """

    @should_pass_compilation()
    def test_valid_type_shorthand_variant_tuple_1(self):
        """
        fun f(mut a: (std::string::Str,)) -> std::void::Void { a = ("hello",) }
        """

    @should_pass_compilation()
    def test_valid_type_shorthand_variant_tuple_n(self):
        """
        fun f(mut a: (std::string::Str, std::boolean::Bool)) -> std::void::Void { a = ("hello", true) }
        """

    @should_pass_compilation()
    def test_valid_type_shorthand_variant_tuple_default(self):
        """
        fun f(a: (std::string::Str, std::boolean::Bool) = ("hello", true)) -> std::void::Void { }
        """

    @should_pass_compilation()
    def test_valid_type_function_type_with_function_call_1(self):
        """
        fun f(a: std::function::FunRef[(std::string::Str, std::string::Str), std::boolean::Bool]) -> std::void::Void {
            let mut x = a("hello", "world")
            x = false
        }
        """

    @should_pass_compilation()
    def test_valid_type_function_type_with_function_call_2(self):
        """
        fun f(a: std::function::FunRef[(&std::string::Str, &std::string::Str), std::boolean::Bool], b: &std::string::Str, c: &std::string::Str) -> std::void::Void {
            let mut x = a(b, c)
            x = false
        }
        """

    @should_pass_compilation()
    def test_valid_nested_type(self):
        """
        cls MyType { }
        sup MyType {
            use X = std::string::Str
        }

        fun f() -> std::void::Void {
            let x: MyType::X
            x = "hello"
        }
        """

    @should_pass_compilation()
    def test_valid_multiple_nested_type(self):
        """
        cls MyTypeA { }
        cls MyTypeB { }
        cls MyTypeC { }

        sup MyTypeA {
            use X = MyTypeB
        }

        sup MyTypeB {
            use Y = MyTypeC
        }

        fun f() -> std::void::Void {
            let x: MyTypeA::X::Y
            x = MyTypeC()
        }
        """

    @should_pass_compilation()
    def test_valid_nested_type_generic(self):
        """
        cls MyType[T] { }
        sup [T] MyType[T] {
            use X = T
        }

        fun f() -> std::void::Void {
            let x: MyType[std::number::BigInt]::X
            x = 10
        }
        """

    @should_pass_compilation()
    def test_valid_nested_type_nested_generics(self):
        """
        cls TypeA[T, A, B] { }
        cls TypeB[U, B] { }
        cls TypeC[V] { }

        sup [V] TypeC[V] {
            use InnerC[P] = TypeB[V, P]
        }

        sup [U, B] TypeB[U, B] {
            use InnerB[Q] = TypeA[U, Q, B]
        }

        sup [T, A, B] TypeA[T, A, B] {
            use InnerA[R] = (T, B, A, R)
        }

        fun f() -> std::void::Void {
            let x: TypeC[std::number::BigInt]::InnerC[std::string::Str]::InnerB[std::boolean::Bool]::InnerA[std::number::U64]
            x = (10_u64, false, "hello", 10)
        }
        """
