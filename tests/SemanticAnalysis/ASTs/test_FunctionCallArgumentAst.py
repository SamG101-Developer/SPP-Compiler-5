from tests._Utils import *


class TestFunctionCallArgumentAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.ExpressionTypeInvalidError)
    def test_invalid_function_argument_unnamed_expression(self):
        """
        fun f(a: std::boolean::Bool) -> std::void::Void { }

        fun g() -> std::void::Void {
            f(std::boolean::Bool)
        }
        """

    @should_fail_compilation(SemanticErrors.ExpressionTypeInvalidError)
    def test_invalid_function_argument_named_type(self):
        """
        fun f(a: std::boolean::Bool) -> std::void::Void { }

        fun g() -> std::void::Void {
            f(a=std::boolean::Bool)
        }
        """

    @should_fail_compilation(SemanticErrors.MutabilityInvalidMutationError)
    def test_invalid_function_argument_mut_from_ref(self):
        # can't take a mutable borrow from an immutable borrow
        """
        fun f(a: &mut std::boolean::Bool) -> std::void::Void { }

        fun g(a: &std::boolean::Bool) -> std::void::Void {
            f(&mut a)
        }
        """

    @should_fail_compilation(SemanticErrors.MutabilityInvalidMutationError)
    def test_invalid_function_call_argument_group_mut_borrow_from_immutable_value(self):
        # can't take a mutable borrow from an immutable value
        """
        fun f(a: &mut std::boolean::Bool) -> std::void::Void { }

        fun g(a: std::boolean::Bool) -> std::void::Void {
            f(&mut a)
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionCallNoValidSignaturesError)
    def test_invalid_function_call_argument_convention_mismatch_1a(self):
        # mov parameter & mut borrow argument
        """
        fun f(a: std::boolean::Bool) -> std::void::Void { }

        fun g(mut a: std::boolean::Bool) -> std::void::Void {
            f(&mut a)
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionCallNoValidSignaturesError)
    def test_invalid_function_call_argument_convention_mismatch_1b(self):
        # mov parameter & mut borrow argument
        """
        fun f(a: std::boolean::Bool) -> std::void::Void { }

        fun g(a: &mut std::boolean::Bool) -> std::void::Void {
            f(a)
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionCallNoValidSignaturesError)
    def test_invalid_function_call_argument_convention_mismatch_1c(self):
        # mov parameter & mut borrow argument
        """
        fun f(a: std::boolean::Bool) -> std::void::Void { }

        fun g(mut a: &mut std::boolean::Bool) -> std::void::Void {
            f(&mut a)
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionCallNoValidSignaturesError)
    def test_invalid_function_call_argument_convention_mismatch_2a(self):
        # mov parameter & ref borrow argument
        """
        fun f(a: std::boolean::Bool) -> std::void::Void { }

        fun g(a: std::boolean::Bool) -> std::void::Void {
            f(&a)
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionCallNoValidSignaturesError)
    def test_invalid_function_call_argument_convention_mismatch_2b(self):
        # mov parameter & ref borrow argument
        """
        fun f(a: std::boolean::Bool) -> std::void::Void { }

        fun g(a: &std::boolean::Bool) -> std::void::Void {
            f(a)
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionCallNoValidSignaturesError)
    def test_invalid_function_call_argument_convention_mismatch_2c(self):
        # mov parameter & ref borrow argument
        """
        fun f(a: std::boolean::Bool) -> std::void::Void { }

        fun g(a: &std::boolean::Bool) -> std::void::Void {
            f(&a)
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionCallNoValidSignaturesError)
    def test_invalid_function_call_argument_convention_mismatch_3a(self):
        # mut borrow parameter & mov argument
        """
        fun f(a: &mut std::boolean::Bool) -> std::void::Void { }

        fun g(a: std::boolean::Bool) -> std::void::Void {
            f(a)
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionCallNoValidSignaturesError)
    def test_invalid_function_call_argument_convention_mismatch_4a(self):
        # mut borrow parameter & ref borrow argument
        """
        fun f(a: &mut std::boolean::Bool) -> std::void::Void { }

        fun g(a: std::boolean::Bool) -> std::void::Void {
            f(&a)
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionCallNoValidSignaturesError)
    def test_invalid_function_call_argument_convention_mismatch_4b(self):
        # mut borrow parameter & ref borrow argument
        """
        fun f(a: &mut std::boolean::Bool) -> std::void::Void { }

        fun g(a: &std::boolean::Bool) -> std::void::Void {
            f(a)
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionCallNoValidSignaturesError)
    def test_invalid_function_call_argument_convention_mismatch_4c(self):
        # mut borrow parameter & ref borrow argument
        """
        fun f(a: &mut std::boolean::Bool) -> std::void::Void { }

        fun g(a: &std::boolean::Bool) -> std::void::Void {
            f(&a)
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionCallNoValidSignaturesError)
    def test_invalid_function_call_argument_convention_mismatch_5a(self):
        # ref borrow parameter & mov argument
        """
        fun f(a: &std::boolean::Bool) -> std::void::Void { }

        fun g(a: std::boolean::Bool) -> std::void::Void {
            f(a)
        }
        """

    @should_pass_compilation()
    def test_valid_function_call_argument_convention_mismatch_coerce_1a(self):
        # ref borrow parameter & mut borrow argument
        """
        fun f(a: &std::boolean::Bool) -> std::void::Void { }

        fun g(mut a: std::boolean::Bool) -> std::void::Void {
            f(&mut a)
        }
        """

    @should_pass_compilation()
    def test_valid_function_call_argument_convention_mismatch_coerce_1b(self):
        # ref borrow parameter & mut borrow argument
        """
        fun f(a: &std::boolean::Bool) -> std::void::Void { }

        fun g(a: &mut std::boolean::Bool) -> std::void::Void {
            f(a)
        }
        """

    @should_pass_compilation()
    def test_valid_function_call_argument_convention_mismatch_coerce_1c(self):
        # ref borrow parameter & mut borrow argument
        """
        fun f(a: &std::boolean::Bool) -> std::void::Void { }

        fun g(mut a: &mut std::boolean::Bool) -> std::void::Void {
            f(&mut a)
        }
        """

    @should_pass_compilation()
    def test_valid_function_argument_unnamed_expression(self):
        """
        fun f(a: std::boolean::Bool) -> std::void::Void { }

        fun g() -> std::void::Void {
            f(true)
        }
        """

    @should_pass_compilation()
    def test_valid_function_argument_named_expression(self):
        """
        fun f(a: std::boolean::Bool) -> std::void::Void { }

        fun g() -> std::void::Void {
            f(a=true)
        }
        """

    @should_pass_compilation()
    def test_valid_function_call_argument_convention_match_1a(self):
        # mov parameter & mov argument
        """
        fun f(a: std::boolean::Bool) -> std::void::Void { }

        fun g(a: std::boolean::Bool) -> std::void::Void {
            f(a)
        }
        """

    @should_pass_compilation()
    def test_valid_function_call_argument_convention_match_2a(self):
        # ref borrow parameter & ref borrow argument
        """
        fun f(a: &std::boolean::Bool) -> std::void::Void { }

        fun g(a: &std::boolean::Bool) -> std::void::Void {
            f(a)
        }
        """

    @should_pass_compilation()
    def test_valid_function_call_argument_convention_match_2b(self):
        # ref borrow parameter & ref borrow argument
        """
        fun f(a: &std::boolean::Bool) -> std::void::Void { }

        fun g(a: std::boolean::Bool) -> std::void::Void {
            f(&a)
        }
        """

    @should_pass_compilation()
    def test_valid_function_call_argument_convention_match_2c(self):
        # ref borrow parameter & ref borrow argument
        """
        fun f(a: &std::boolean::Bool) -> std::void::Void { }

        fun g(a: &std::boolean::Bool) -> std::void::Void {
            f(&a)
        }
        """

    @should_pass_compilation()
    def test_valid_function_call_argument_convention_match_3a(self):
        # mut borrow parameter & mut borrow argument
        """
        fun f(a: &mut std::boolean::Bool) -> std::void::Void { }

        fun g(a: &mut std::boolean::Bool) -> std::void::Void {
            f(a)
        }
        """

    @should_pass_compilation()
    def test_valid_function_call_argument_convention_match_3b(self):
        # mut borrow parameter & mut borrow argument
        """
        fun f(a: &mut std::boolean::Bool) -> std::void::Void { }

        fun g(mut a: std::boolean::Bool) -> std::void::Void {
            f(&mut a)
        }
        """

    @should_pass_compilation()
    def test_valid_function_call_argument_convention_match_3c(self):
        # mut borrow parameter & mut borrow argument
        """
        fun f(a: &mut std::boolean::Bool) -> std::void::Void { }

        fun g(mut a: &mut std::boolean::Bool) -> std::void::Void {
            f(&mut a)
        }
        """
