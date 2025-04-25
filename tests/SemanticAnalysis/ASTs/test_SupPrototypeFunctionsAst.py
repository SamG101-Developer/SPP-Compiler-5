from tests._Utils import *


class TestSupPrototypeFunctionsAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.SuperimpositionUnconstrainedGenericParameterError)
    def test_invalid_sup_prototype_functions_unconstrained_generic_parameter_1(self):
        """
        cls Point {
            x: std::number::bigint::BigInt
            y: std::number::bigint::BigInt
        }

        sup [T] Point { }
        """

    @should_fail_compilation(SemanticErrors.SuperimpositionUnconstrainedGenericParameterError)
    def test_invalid_sup_prototype_functions_unconstrained_generic_parameter_2(self):
        """
        cls Point[T] {
            x: T
            y: T
        }

        sup [T, U] Point[T] { }
        """

    @should_fail_compilation(SemanticErrors.SuperimpositionOptionalGenericParameterError)
    def test_invalid_sup_prototype_functions_optional_generic_parameter(self):
        """
        cls Point[T] {
            x: T
            y: T
        }

        sup [T=std::boolean::Bool] Point[T] { }
        """

    @should_fail_compilation(SemanticErrors.GenericTypeInvalidUsageError)
    def test_invalid_sup_prototype_functions_onto_generic_type(self):
        """
        sup [T] T {
            fun f(&self) -> std::void::Void { }
        }
        """

    @should_fail_compilation(SemanticErrors.InvalidConventionLocationError)
    def test_invalid_superimposition_functions_type_convention_mut(self):
        """
        cls A { }
        sup &mut A { }
        """

    @should_fail_compilation(SemanticErrors.InvalidConventionLocationError)
    def test_invalid_superimposition_functions_type_convention_ref(self):
        """
        cls A { }
        sup &A { }
        """

    @should_fail_compilation(SemanticErrors.IdentifierDuplicationError)
    def test_invalid_superimposition_functions_use_statement_conflict(self):
        """
        cls Base1 { }
        sup Base1 {
            use X = std::string::Str
        }

        cls Base2 { }
        sup Base2 {
            use X = std::number::bigint::BigInt
        }

        cls A { }
        sup A ext Base1 { }
        sup A ext Base2 { }
        """

    @should_fail_compilation(SemanticErrors.IdentifierDuplicationError)
    def test_invalid_superimposition_functions_use_statement_conflict_direct_extension(self):
        """
        cls Base1 { }
        sup Base1 {
            use X = std::string::Str
        }

        cls Base2 { }
        sup Base2 {
            use X = std::number::bigint::BigInt
        }

        sup Base2 ext Base1 { }
        """

    @should_fail_compilation(SemanticErrors.IdentifierDuplicationError)
    def test_invalid_superimposition_functions_cmp_statement_conflict(self):
        """
        cls Base1 { }
        sup Base1 {
            cmp x: std::string::Str = "hello world"
        }

        cls Base2 { }
        sup Base2 {
            cmp x: std::number::bigint::BigInt = 123
        }

        cls A { }
        sup A ext Base1 { }
        sup A ext Base2 { }
        """

    @should_fail_compilation(SemanticErrors.IdentifierDuplicationError)
    def test_invalid_superimposition_functions_cmp_statement_conflict_direct_extension(self):
        """
        cls Base1 { }
        sup Base1 {
            cmp x: std::string::Str = "hello world"
        }

        cls Base2 { }
        sup Base2 {
            cmp x: std::number::bigint::BigInt = 123
        }

        sup Base2 ext Base1 { }
        """

    @should_fail_compilation(SemanticErrors.IdentifierDuplicationError)
    def test_invalid_superimposition_functions_attribute_conflict(self):
        """
        cls Base1 { a: std::string::Str }
        cls Base2 { a: std::number::bigint::BigInt }

        cls A { }
        sup A ext Base1 { }
        sup A ext Base2 { }
        """

    @should_pass_compilation()
    def test_valid_sup_prototype_functions(self):
        """
        cls A { }
        sup A {
            fun f(&self) -> std::void::Void { }
        }
        """

    @should_pass_compilation()
    def test_valid_sup_prototype_functions_generic_fallthrough_explicit(self):
        """
        cls BaseClass[T] { }

        sup [T] BaseClass[T] {
            @no_impl
            fun f(&self) -> T { }
        }

        fun f() -> std::void::Void {
            let x = BaseClass[std::boolean::Bool]()
            let mut y = x.f()
            y = false
        }
        """

    @should_pass_compilation()
    def test_valid_sup_prototype_functions_generic_fallthrough_implicit(self):
        """
        cls BaseClass[T] { a: T }

        sup [T] BaseClass[T] {
            @no_impl
            fun f(&self) -> T { }
        }

        fun f() -> std::void::Void {
            let x = BaseClass(a=false)
            let mut y = x.f()
            y = false
        }
        """

    @should_pass_compilation()
    def test_valid_superimposition_functions_use_statement_different_type_names(self):
        """
        cls Base1 { }
        sup Base1 {
            use X = std::string::Str
        }

        cls Base2 { }
        sup Base2 {
            use Y = std::number::bigint::BigInt
        }

        cls A { }
        sup A ext Base1 { }
        sup A ext Base2 { }
        """

    @should_pass_compilation()
    def test_valid_superimposition_functions_use_statement_override(self):
        """
        cls Base1 { }
        sup Base1 {
            use X = std::string::Str
        }

        cls Base2 { }
        sup Base2 ext Base1 {
            use X = std::number::bigint::BigInt
        }
        """

    @should_pass_compilation()
    def test_valid_superimposition_functions_cmp_statement_different_type_names(self):
        """
        cls Base1 { }
        sup Base1 {
            cmp x: std::string::Str = "hello world"
        }

        cls Base2 { }
        sup Base2 {
            cmp y: std::number::bigint::BigInt = 123
        }

        cls A { }
        sup A ext Base1 { }
        sup A ext Base2 { }
        """

    @should_pass_compilation()
    def test_valid_superimposition_functions_cmp_statement_override(self):
        """
        cls Base1 { }
        sup Base1 {
            cmp x: std::string::Str = "hello world"
        }

        cls Base2 { }
        sup Base2 ext Base1 {
            cmp x: std::number::bigint::BigInt = 123
        }
        """
