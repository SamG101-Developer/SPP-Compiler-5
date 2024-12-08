from unittest import TestCase

from tst._Utils import *


class TestSupPrototypeInheritanceAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.GenericTypeInvalidUsageError)
    def test_invalid_superimposition_inheritance_generic_name(self):
        """
        sup [T] T ext std::BigInt { }
        """

    @should_fail_compilation(SemanticErrors.GenericTypeInvalidUsageError)
    def test_invalid_superimposition_inheritance_generic_superclass(self):
        """
        sup [T] std::BigInt ext T { }
        """

    @should_fail_compilation(SemanticErrors.SuperimpositionInheritanceDuplicateSuperclassError)
    def test_invalid_superimposition_inheritance_duplication_superclass(self):
        """
        sup std::BigInt ext std::Str { }
        sup std::BigInt ext std::Str { }
        """

    @should_fail_compilation(SemanticErrors.SuperimpositionInheritanceCyclicInheritanceError)
    def test_invalid_superimposition_inheritance_cyclic_inheritance(self):
        """
        sup std::BigInt ext std::Str { }
        sup std::Str ext std::BigInt { }
        """

    @should_fail_compilation(SemanticErrors.SuperimpositionInheritanceMethodInvalidError)
    def test_invalid_superimposition_inheritance_invalid_override_method_1(self):
        """
        cls A { }
        sup A {
            fun f(&self) -> std::Void { }
        }

        cls B { }
        sup B ext A {
            fun g(&self) -> std::Void { }
        }
        """

    @should_fail_compilation(SemanticErrors.SuperimpositionInheritanceMethodInvalidError)
    def test_invalid_superimposition_inheritance_invalid_override_method_2(self):
        """
        cls A { }
        sup A {
            fun f(&self) -> std::Void { }
        }

        cls B { }
        sup B ext A {
            fun f(&mut self) -> std::Void { }
        }
        """

    @should_fail_compilation(SemanticErrors.SuperimpositionInheritanceMethodInvalidError)
    def test_invalid_superimposition_inheritance_invalid_override_method_3(self):
        """
        cls A { }
        sup A {
            fun f(&self) -> std::Void { }
        }

        cls B { }
        sup B ext A {
            fun f(&self, x: std::Bool = true) -> std::Void { }
        }
        """

    @should_fail_compilation(SemanticErrors.SuperimpositionInheritanceMethodInvalidError)
    def test_invalid_superimposition_inheritance_invalid_override_method_4(self):
        """
        cls A { }
        sup A {
            fun f(&self) -> std::Void { }
        }

        cls B { }
        sup B ext A {
            fun f(&self) -> std::Bool { ret true }
        }
        """

    @should_fail_compilation(SemanticErrors.SuperimpositionInheritanceNonVirtualMethodOverriddenError)
    def test_invalid_superimposition_inheritance_non_virtual_method_override(self):
        """
        cls A { }
        sup A {
            fun f(&self) -> std::Void { }
        }

        cls B { }
        sup B ext A {
            fun f(&self) -> std::Void { }
        }
        """

    @should_pass_compilation()
    def test_valid_superimposition_inheritance_generic_variants(self):
        """
        cls BaseClass[T] { }

        cls A { }
        sup A ext BaseClass[std::BigInt] { }
        sup A ext BaseClass[std::Bool] { }
        """

    @should_pass_compilation()
    def test_valid_superimposition_inheritance_stateful(self):
        """
        cls A { a: std::BigInt }
        cls B { b: std::BigInt }

        sup A {
            @virtual_method
            fun f(mut self) -> std::Void {
                self.a = 100
            }
        }

        sup B ext A {
            fun f(mut self) -> std::Void {
                self.a = self.b
            }
        }

        fun f() -> std::Void {
            let b = B(b=200)
        }
        """

    @should_pass_compilation()
    def test_valid_superimposition_inheritance_generics_1(self):
        """
        cls A[T] { a: T }
        cls B[T] { b: T }

        sup [T] A[T] {
            @virtual_method
            fun f(mut self) -> std::Void { }
        }

        sup [T] B[T] ext A[T] {
            fun f(mut self) -> std::Void {
                self.a = self.b
            }
        }

        fun f() -> std::Void {
            let b = B(b=100)
        }
        """
