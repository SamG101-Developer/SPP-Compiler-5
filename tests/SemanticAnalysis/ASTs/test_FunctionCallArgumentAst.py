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
    def test_invalid_function_call_argument_convention_mismatch_1(self):
        # mov parameter & mut borrow argument
        """
        fun f(a: std::boolean::Bool) -> std::void::Void { }

        fun g(mut a: std::boolean::Bool) -> std::void::Void {
            f(&mut a)
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionCallNoValidSignaturesError)
    def test_invalid_function_call_argument_convention_mismatch_2(self):
        # mov parameter & ref borrow argument
        """
        fun f(a: std::boolean::Bool) -> std::void::Void { }

        fun g(a: std::boolean::Bool) -> std::void::Void {
            f(&a)
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionCallNoValidSignaturesError)
    def test_invalid_function_call_argument_convention_mismatch_3(self):
        # mut borrow parameter & mov argument
        """
        fun f(a: &mut std::boolean::Bool) -> std::void::Void { }

        fun g(a: std::boolean::Bool) -> std::void::Void {
            f(a)
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionCallNoValidSignaturesError)
    def test_invalid_function_call_argument_convention_mismatch_4(self):
        # mut borrow parameter & ref borrow argument
        """
        fun f(a: &mut std::boolean::Bool) -> std::void::Void { }

        fun g(a: std::boolean::Bool) -> std::void::Void {
            f(&a)
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionCallNoValidSignaturesError)
    def test_invalid_function_call_argument_convention_mismatch_5(self):
        # ref borrow parameter & mov argument
        """
        fun f(a: &std::boolean::Bool) -> std::void::Void { }

        fun g(a: std::boolean::Bool) -> std::void::Void {
            f(a)
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionCallNoValidSignaturesError)
    def test_invalid_function_call_argument_convention_mismatch_6(self):
        # ref borrow parameter & mut borrow argument
        """
        fun f(a: &std::boolean::Bool) -> std::void::Void { }

        fun g(mut a: std::boolean::Bool) -> std::void::Void {
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
