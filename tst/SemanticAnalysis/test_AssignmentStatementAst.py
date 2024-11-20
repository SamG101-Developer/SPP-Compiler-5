from unittest import TestCase

from tst._Utils import *


class TestAnnotationAst(TestCase):
    @should_pass_compilation()
    def test_valid_assignment_variable(self):
        """
        fun f() -> std::Void {
            let mut a = 1
            a = 2
        }
        """

    @should_pass_compilation()
    def test_valid_assignment_attribute_owned(self):
        """
        cls A {
            b: std::Bool
        }

        fun f(mut a: A) -> std::Void {
            a.b = true
        }
        """

    @should_pass_compilation()
    def test_valid_assignment_attribute_mut_borrow(self):
        """
        cls A {
            b: std::Bool
        }

        fun f(a: &mut A) -> std::Void {
            a.b = true
        }
        """

    @should_pass_compilation()
    def test_valid_assignment_mutable_value_ref_borrow(self):
        """
        fun f(mut a: &std::Bool, b: &std::Bool) -> std::Void {
            a = b
        }
        """

    @should_pass_compilation()
    def test_valid_assignment_non_initialized_non_mut_variable(self):
        """
        fun f() -> std::Void {
            let a: std::Bool
            a = false
        }
        """

    @should_pass_compilation()
    def test_valid_assignment_non_initialized_mut_variable(self):
        """
        fun f() -> std::Void {
            let mut a: std::Bool
            a = false
            a = true
        }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_assignment_variable(self):
        """
        fun f() -> std::Void {
            let mut a = 1
            a = "2"
        }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_assignment_attribute(self):
        """
        cls A {
            b: std::Bool
        }

        fun f(mut a: A) -> std::Void {
            a.b = "1"
        }
        """

    @should_fail_compilation(SemanticErrors.MutabilityInvalidMutationError)
    def test_invalid_assignment_non_mut_variable(self):
        """
        fun f() -> std::Void {
            let a = 1
            a = 2
        }
        """

    @should_fail_compilation(SemanticErrors.MutabilityInvalidMutationError)
    def test_invalid_assignment_non_mut_attribute(self):
        """
        cls A {
            b: std::Bool
        }

        fun f(a: A) -> std::Void {
            a.b = true
        }
        """

    @should_fail_compilation(SemanticErrors.MutabilityInvalidMutationError)
    def test_invalid_assignment_ref_borrow_attribute(self):
        """
        cls A {
            b: std::Bool
        }

        fun f(a: &A) -> std::Void {
            a.b = true
        }
        """

    @should_fail_compilation(SemanticErrors.AssignmentInvalidLhsError)
    def test_invalid_assignment_ref_borrow_variable(self):
        """
        fun f() -> std::Void {
            1 = 2
        }
        """

    @should_fail_compilation(SemanticErrors.MutabilityInvalidMutationError)
    def test_invalid_assignment_non_initialized_non_mut_variable(self):
        """
        fun f() -> std::Void {
            let a: std::Bool
            a = false
            a = true
        }
        """