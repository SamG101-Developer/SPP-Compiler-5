from tests._Utils import *


# Todo: Nested types are not supported yet.


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

    @should_fail_compilation(SemanticErrors.GenericTypeInvalidUsageError)
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
        fun f(mut a: std::string::Str?) -> std::void::Void { a = std::option::Some("hello") }
        """

    @should_pass_compilation()
    def test_valid_type_shorthand_optional_default(self):
        """
        fun f(a: std::string::Str? = std::option::Some("hello")) -> std::void::Void { }
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
