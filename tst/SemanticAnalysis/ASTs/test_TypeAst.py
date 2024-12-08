from unittest import TestCase

from tst._Utils import *


# Todo: Nested types are not supported yet.


class TestTypeAst(TestCase):
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
        fun f() -> std::Str::Type { }
        """

    @should_fail_compilation(SemanticErrors.GenericTypeInvalidUsageError)
    def test_invalid_type_generic_nested_type(self):
        """
        fun f[T]() -> T::Type { }
        """

    @should_pass_compilation()
    def test_valid_type(self):
        """
        fun f() -> std::Void { }
        """

    @should_pass_compilation()
    def test_valid_type_namespaced(self):
        """
        fun f() -> std::Void { }
        """

    @should_pass_compilation()
    def test_valid_type_shorthand_optional(self):
        """
        fun f(mut a: ?std::Str) -> std::Void { a = std::Some("hello") }
        """

    @should_pass_compilation()
    def test_valid_type_shorthand_optional_default(self):
        """
        fun f(a: ?std::Str = std::Some("hello")) -> std::Void { }
        """

    @should_pass_compilation()
    def test_valid_type_shorthand_variant(self):
        """
        fun f(mut a: std::Str | std::Bool) -> std::Void { a = "hello" }
        """

    @should_pass_compilation()
    def test_valid_type_shorthand_variant_default(self):
        """
        fun f(a: std::Str | std::Bool = "hello") -> std::Void { }
        """

    @should_pass_compilation()
    def test_valid_type_shorthand_variant_tuple(self):
        """
        fun f(mut a: (std::Str, std::Bool)) -> std::Void { a = ("hello", true) }
        """

    @should_pass_compilation()
    def test_valid_type_shorthand_variant_tuple_default(self):
        """
        fun f(a: (std::Str, std::Bool) = ("hello", true)) -> std::Void { }
        """
