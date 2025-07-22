from tests._Utils import *


class TestSupPrototypeExtensionAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.IdentifierUnknownError)
    def test_invalid_sup_prototype_functions_unknown_type(self):
        """
        sup A {
            fun f(&self) -> std::void::Void { }
        }
        """

    @should_fail_compilation(SemanticErrors.IdentifierUnknownError)
    def test_invalid_sup_prototype_functions_unknown_supertype(self):
        """
        sup std::boolean::Bool ext A {
            fun f(&self) -> std::void::Void { }
        }
        """

    @should_pass_compilation()
    def test_valid_superimposition_extension_generic_name(self):
        """
        cls A { }
        sup [T] T ext A { }
        """

    @should_pass_compilation()
    def test_valid_superimposition_extension_generic_name_more_complex(self):
        """
        cls CanBorrowRef[T] { }
        sup [T] CanBorrowRef[T] {
            cor borrow_ref(&self) -> std::generator::Gen[&T] {
                gen self
            }
        }

        cls CanBorrowMut[T] { }
        sup [T] CanBorrowMut[T] {
            cor borrow_mut(&mut self) -> std::generator::Gen[&mut T] {
                gen self
            }
        }

        sup [T] T ext CanBorrowRef[T] { }
        sup [T] T ext CanBorrowMut[T] { }

        fun f() -> std::void::Void {
            let x = 123
            let y = x.borrow_ref()
        }
        """

    @should_fail_compilation(SemanticErrors.GenericTypeInvalidUsageError)
    def test_invalid_superimposition_extension_generic_superclass(self):
        """
        sup [T] std::vector::Vec[T] ext T { }
        """

    @should_fail_compilation(SemanticErrors.SuperimpositionUnconstrainedGenericParameterError)
    def test_invalid_superimposition_extension_unconstrained_generic(self):
        """
        sup [T] std::boolean::Bool ext std::bignum::bigint::BigInt { }
        """

    @should_fail_compilation(SemanticErrors.SuperimpositionExtensionDuplicateSuperclassError)
    def test_invalid_superimposition_extension_duplication_superclass(self):
        """
        sup std::boolean::Bool ext std::string::Str { }
        sup std::boolean::Bool ext std::string::Str { }
        """

    @should_fail_compilation(SemanticErrors.SuperimpositionExtensionCyclicExtensionError)
    def test_invalid_superimposition_extension_cyclic_extension(self):
        """
        sup std::boolean::Bool ext std::string::Str { }
        sup std::string::Str ext std::boolean::Bool { }
        """

    @should_fail_compilation(SemanticErrors.SuperimpositionExtensionSelfExtensionError)
    def test_invalid_superimposition_extension_self_extension(self):
        """
        cls A { }
        sup A ext A { }
        """

    @should_fail_compilation(SemanticErrors.SuperimpositionExtensionMethodInvalidError)
    def test_invalid_superimposition_extension_invalid_override_method_1(self):
        """
        cls A { }
        sup A {
            fun f(&self) -> std::void::Void { }
        }

        cls B { }
        sup B ext A {
            fun g(&self) -> std::void::Void { }
        }
        """

    @should_fail_compilation(SemanticErrors.SuperimpositionExtensionMethodInvalidError)
    def test_invalid_superimposition_extension_invalid_override_method_2(self):
        """
        cls A { }
        sup A {
            fun f(&self) -> std::void::Void { }
        }

        cls B { }
        sup B ext A {
            fun f(&mut self) -> std::void::Void { }
        }
        """

    @should_fail_compilation(SemanticErrors.SuperimpositionExtensionMethodInvalidError)
    def test_invalid_superimposition_extension_invalid_override_method_3(self):
        """
        cls A { }
        sup A {
            fun f(&self) -> std::void::Void { }
        }

        cls B { }
        sup B ext A {
            fun f(&self, x: std::boolean::Bool = true) -> std::void::Void { }
        }
        """

    @should_fail_compilation(SemanticErrors.SuperimpositionExtensionMethodInvalidError)
    def test_invalid_superimposition_extension_invalid_override_method_4(self):
        """
        cls A { }
        sup A {
            fun f(&self) -> std::void::Void { }
        }

        cls B { }
        sup B ext A {
            fun f(&self) -> std::boolean::Bool { ret true }
        }
        """

    @should_fail_compilation(SemanticErrors.SuperimpositionExtensionNonVirtualMethodOverriddenError)
    def test_invalid_superimposition_extension_non_virtual_method_override(self):
        """
        cls A { }
        sup A {
            fun f(&self) -> std::void::Void { }
        }

        cls B { }
        sup B ext A {
            fun f(&self) -> std::void::Void { }
        }
        """

    @should_fail_compilation(SemanticErrors.SuperimpositionExtensionUseStatementInvalidError)
    def test_invalid_superimposition_extension_invalid_use_statement(self):
        """
        cls A { }

        cls B { }
        sup B ext A {
            use X = std::string::Str
        }
        """

    @should_fail_compilation(SemanticErrors.SuperimpositionExtensionCmpStatementInvalidError)
    def test_invalid_superimposition_extension_invalid_use_statement(self):
        """
        cls A { }

        cls B { }
        sup B ext A {
            cmp x: std::string::Str = "hello world"
        }
        """

    @should_fail_compilation(SemanticErrors.InvalidConventionLocationError)
    def test_invalid_superimposition_extension_type_convention_mut(self):
        """
        cls A { }
        sup &mut A ext std::bignum::bigint::BigInt { }
        """

    @should_fail_compilation(SemanticErrors.InvalidConventionLocationError)
    def test_invalid_superimposition_extension_type_convention_ref(self):
        """
        cls A { }
        sup &A ext std::bignum::bigint::BigInt { }
        """

    @should_fail_compilation(SemanticErrors.InvalidConventionLocationError)
    def test_invalid_superimposition_extension_supertype_convention_mut(self):
        """
        cls A { }
        sup A ext &mut std::bignum::bigint::BigInt { }
        """

    @should_fail_compilation(SemanticErrors.InvalidConventionLocationError)
    def test_invalid_superimposition_extension_supertype_convention_ref(self):
        """
        cls A { }
        sup A ext &std::bignum::bigint::BigInt { }
        """

    @should_pass_compilation()
    def test_valid_superimposition_extension_generic_variants(self):
        """
        cls BaseClass[T] { }

        cls A { }
        sup A ext BaseClass[std::bignum::bigint::BigInt] { }
        sup A ext BaseClass[std::boolean::Bool] { }
        """

    @should_pass_compilation()
    def test_valid_superimposition_extension_stateful(self):
        """
        cls A { a: std::bignum::bigint::BigInt }
        cls B { b: std::bignum::bigint::BigInt }

        sup A {
            @virtual_method
            fun f(mut self) -> std::void::Void {
                self.a = 100
            }
        }

        sup B ext A {
            fun f(mut self) -> std::void::Void {
                self.a = self.b
            }
        }

        fun f() -> std::void::Void {
            let b = B(b=200)
        }
        """

    @should_pass_compilation()
    def test_valid_superimposition_extension_generics_1(self):
        """
        cls A[T] { a: T }
        cls B[T] { b: T }

        sup [T] A[T] {
            @virtual_method
            fun f(mut self) -> std::void::Void { }
        }

        sup [T] B[T] ext A[T] {
            fun f(mut self) -> std::void::Void {
                self.a = self.b
            }
        }

        fun f() -> std::void::Void {
            let b = B(b=100)
        }
        """
