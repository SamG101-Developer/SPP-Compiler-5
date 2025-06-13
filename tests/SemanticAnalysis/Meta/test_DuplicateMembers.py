from tests._Utils import *


class TestDuplicateMembers_SupType(CustomTestCase):
    @should_pass_compilation()
    def test_valid_superimposition_extension_type_statement_diff_levels(self):
        """
        cls A { }
        sup A {
            type X = std::number::bigint::BigInt
        }

        cls B { }
        sup B ext A {
            type X = std::string::Str
        }
        """

    @should_fail_compilation(SemanticErrors.IdentifierDuplicationError)
    def test_invalid_superimposition_extension_type_statement_same_levels(self):
        """
        cls A { }
        sup A {
            type X = std::number::bigint::BigInt
        }

        sup A {
            type X = std::string::Str
        }
        """

    @should_pass_compilation()
    def test_valid_superimposition_extension_type_statement_same_levels_via_inheritance(self):
        """
        cls B { }
        sup B {
            type X = std::number::bigint::BigInt
        }

        cls C { }
        sup C {
            type X = std::string::Str
        }

        cls A { }
        sup A ext B { }
        sup A ext C { }
        """

    @should_fail_compilation(SemanticErrors.AmbiguousMemberAccessError)
    def test_invalid_superimposition_extension_type_statement_same_levels_via_inheritance_with_ambiguous_access_1(self):
        """
        cls B { }
        sup B {
            type X = std::number::bigint::BigInt
        }

        cls C { }
        sup C {
            type X = std::string::Str
        }

        cls A { }
        sup A ext B { }
        sup A ext C { }

        fun f() -> std::void::Void {
            let x: A::X
        }
        """

    @should_fail_compilation(SemanticErrors.AmbiguousMemberAccessError)
    def test_invalid_superimposition_extension_type_statement_same_levels_via_inheritance_with_ambiguous_access_2(self):
        """
        cls B { }
        sup B {
            type X = std::number::bigint::BigInt
        }

        cls C { }
        sup C {
            type X = std::string::Str
        }

        cls A { }
        sup A ext B { }
        sup A ext C { }

        fun f() -> std::void::Void {
            let x = A::X()
        }
        """

    @should_pass_compilation()
    def test_valid_superimposition_extension_type_statement_same_levels_via_inheritance_with_unique_override(self):
        """
        cls B { }
        sup B {
            type X = std::number::bigint::BigInt
        }

        cls C { }
        sup C {
            type X = std::string::Str
        }

        cls A { }
        sup A ext B { }
        sup A ext C { }
        sup A {
            type X = std::boolean::Bool
        }

        fun f() -> std::void::Void {
            let x = A::X()
        }
        """


class TestDuplicateMembers_SupCmp(CustomTestCase):
    @should_pass_compilation()
    def test_valid_superimposition_extension_cmp_statement_diff_levels(self):
        """
        cls A { }
        sup A {
            cmp x: std::number::bigint::BigInt = 123
        }

        cls B { }
        sup B ext A {
            cmp x: std::string::Str = "hello world"
        }
        """

    @should_fail_compilation(SemanticErrors.IdentifierDuplicationError)
    def test_invalid_superimposition_extension_cmp_statement_same_levels(self):
        """
        cls A { }
        sup A {
            cmp x: std::number::bigint::BigInt = 123
        }

        sup A {
            cmp x: std::string::Str = "hello world"
        }
        """

    @should_pass_compilation()
    def test_valid_superimposition_extension_cmp_statement_same_levels_via_inheritance(self):
        """
        cls B { }
        sup B {
            cmp x: std::number::bigint::BigInt = 123
        }

        cls C { }
        sup C {
            cmp x: std::string::Str = "hello world"
        }

        cls A { }
        sup A ext B { }
        sup A ext C { }
        """

    @should_fail_compilation(SemanticErrors.AmbiguousMemberAccessError)
    def test_invalid_superimposition_extension_cmp_statement_same_levels_via_inheritance_with_ambiguous_access_1(self):
        """
        cls B { }
        sup B {
            cmp x: std::number::usize::USize = 123_uz
        }

        cls C { }
        sup C {
            cmp x: std::boolean::Bool = true
        }

        cls A { }
        sup A ext B { }
        sup A ext C { }

        fun f() -> std::void::Void {
            let x = A::x
        }
        """

    @should_pass_compilation()
    def test_valid_superimposition_extension_cmp_statement_same_levels_via_inheritance_with_unique_override(self):
        """
        cls B { }
        sup B {
            cmp x: std::number::usize::USize = 123_uz
        }

        cls C { }
        sup C {
            cmp x: std::boolean::Bool = true
        }

        cls A { }
        sup A ext B { }
        sup A ext C { }
        sup A {
            cmp x: std::number::u64::U64 = 123_u64
        }

        fun f() -> std::void::Void {
            let x = A::x
        }
        """


class TestDuplicateMembers_SupClsAttr(CustomTestCase):
    @should_pass_compilation()
    def test_valid_superimposition_extension_cls_attr_statement_diff_levels(self):
        """
        cls A {
            a: std::number::bigint::BigInt
        }

        cls B {
            a: std::string::Str
        }

        sup B ext A { }
        """

    @should_fail_compilation(SemanticErrors.IdentifierDuplicationError)
    def test_invalid_superimposition_extension_cls_attr_statement_same_levels(self):
        """
        cls A {
            a: std::number::bigint::BigInt
            a: std::string::Str
        }
        """

    @should_pass_compilation()
    def test_valid_superimposition_extension_cls_attr_statement_same_levels_via_inheritance(self):
        """
        cls B {
            a: std::number::bigint::BigInt
        }

        cls C {
            a: std::string::Str
        }

        cls A { }
        sup A ext B { }
        sup A ext C { }
        """

    @should_fail_compilation(SemanticErrors.AmbiguousMemberAccessError)
    def test_invalid_superimposition_extension_cls_attr_statement_same_levels_via_inheritance_with_ambiguous_access(self):
        """
        cls B {
            a: std::number::bigint::BigInt
        }

        cls C {
            a: std::string::Str
        }

        cls A { }
        sup A ext B { }
        sup A ext C { }

        fun f() -> std::void::Void {
            let x = A().a
        }
        """

    @should_pass_compilation()
    def test_valid_superimposition_extension_cls_attr_statement_same_levels_via_inheritance_with_unique_override(self):
        """
        cls B {
            a: std::number::bigint::BigInt
        }

        cls C {
            a: std::string::Str
        }

        cls A {
            a: std::boolean::Bool
        }

        sup A ext B { }
        sup A ext C { }

        fun f() -> std::void::Void {
            let x = A().a
        }
        """
