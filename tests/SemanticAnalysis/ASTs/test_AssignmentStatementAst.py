from tests._Utils import *


class TestAssignmentStatementAst(CustomTestCase):
    @should_pass_compilation()
    def test_valid_assignment_variable(self):
        """
        fun f() -> std::void::Void {
            let mut a = 1
            a = 2
        }
        """

    @should_pass_compilation()
    def test_valid_assignment_attribute_owned(self):
        """
        cls A {
            b: std::boolean::Bool
        }

        fun f(mut a: A) -> std::void::Void {
            a.b = true
        }
        """

    @should_pass_compilation()
    def test_valid_assignment_attribute_mut_borrow(self):
        """
        cls A {
            b: std::boolean::Bool
        }

        fun f(a: &mut A) -> std::void::Void {
            a.b = true
        }
        """

    @should_pass_compilation()
    def test_valid_assignment_mutable_value_ref_borrow(self):
        """
        fun f(mut a: &std::boolean::Bool, b: &std::boolean::Bool) -> std::void::Void {
            a = b
        }
        """

    @should_pass_compilation()
    def test_valid_assignment_non_initialized_non_mut_variable(self):
        """
        fun f() -> std::void::Void {
            let a: std::boolean::Bool
            a = false
        }
        """

    @should_pass_compilation()
    def test_valid_assignment_non_initialized_mut_variable(self):
        """
        fun f() -> std::void::Void {
            let mut a: std::boolean::Bool
            a = false
            a = true
        }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_assignment_convention_mismatch_1(self):
        """
        fun f(b: std::boolean::Bool) -> std::void::Void {
            let mut x: &mut std::boolean::Bool
            x = b
        }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_assignment_convention_mismatch_2(self):
        """
        fun f(b: std::boolean::Bool) -> std::void::Void {
            let mut x: &std::boolean::Bool
            x = b
        }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_assignment_convention_mismatch_3(self):
        """
        fun f(b: &mut std::boolean::Bool) -> std::void::Void {
            let mut x: std::boolean::Bool
            x = b
        }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_assignment_convention_mismatch_4(self):
        """
        fun f(b: &mut std::boolean::Bool) -> std::void::Void {
            let mut x: &std::boolean::Bool
            x = b
        }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_assignment_convention_mismatch_5(self):
        """
        fun f(b: &std::boolean::Bool) -> std::void::Void {
            let mut x: std::boolean::Bool
            x = b
        }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_assignment_convention_mismatch_6(self):
        """
        fun f(b: &std::boolean::Bool) -> std::void::Void {
            let mut x: &mut std::boolean::Bool
            x = b
        }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_assignment_variable_type(self):
        """
        fun f() -> std::void::Void {
            let mut a = 1
            a = "2"
        }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_assignment_attribute_type(self):
        """
        cls A {
            b: std::boolean::Bool
        }

        fun f(mut a: A) -> std::void::Void {
            a.b = "1"
        }
        """

    @should_fail_compilation(SemanticErrors.MutabilityInvalidMutationError)
    def test_invalid_assignment_non_mut_variable(self):
        """
        fun f() -> std::void::Void {
            let a = 1
            a = 2
        }
        """

    @should_fail_compilation(SemanticErrors.MutabilityInvalidMutationError)
    def test_invalid_assignment_non_mut_attribute(self):
        """
        cls A {
            b: std::boolean::Bool
        }

        fun f(a: A) -> std::void::Void {
            a.b = true
        }
        """

    @should_fail_compilation(SemanticErrors.MutabilityInvalidMutationError)
    def test_invalid_assignment_ref_borrow_attribute_1(self):
        """
        cls A {
            b: std::boolean::Bool
        }

        fun f(a: &A) -> std::void::Void {
            a.b = true
        }
        """

    @should_fail_compilation(SemanticErrors.AssignmentInvalidLhsError)
    def test_invalid_assignment_ref_borrow_variable(self):
        """
        fun f() -> std::void::Void {
            1 = 2
        }
        """

    @should_fail_compilation(SemanticErrors.MutabilityInvalidMutationError)
    def test_invalid_assignment_non_initialized_non_mut_variable(self):
        """
        fun f() -> std::void::Void {
            let a: std::boolean::Bool
            a = false
            a = true
        }
        """
