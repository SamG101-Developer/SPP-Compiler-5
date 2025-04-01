from tests._Utils import *


class TestFunctionCallArgumentGroupAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.IdentifierDuplicationError)
    def test_invalid_function_call_argument_group_duplicate_named_argument(self):
        """
        fun f(a: std::boolean::Bool, b: std::boolean::Bool) -> std::void::Void { }

        fun g() -> std::void::Void {
            f(a=true, a=false)
        }
        """

    @should_fail_compilation(SemanticErrors.OrderInvalidError)
    def test_invalid_function_call_argument_group_invalid_argument_order(self):
        """
        fun f(a: std::boolean::Bool, b: std::boolean::Bool) -> std::void::Void { }

        fun g() -> std::void::Void {
            f(a=true, false)
        }
        """

    @should_fail_compilation(SemanticErrors.ArgumentTupleExpansionOfNonTupleError)
    def test_invalid_function_call_argument_group_invalid_tuple_expansion(self):
        """
        fun f(a: std::boolean::Bool, b: std::boolean::Bool) -> std::void::Void { }

        fun g() -> std::void::Void {
            let x = 1
            f(..x)
        }
        """

    @should_fail_compilation(SemanticErrors.MutabilityInvalidMutationError)
    def test_invalid_function_call_argument_group_mut_borrow_from_immutable_value(self):
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

    @should_fail_compilation(SemanticErrors.FunctionCallNoValidSignaturesError)
    def test_invalid_function_call_argument_convention_mismatch_7(self):
        # ref-ref borrow parameter & ref borrow argument
        """
        fun f(a: &&std::boolean::Bool) -> std::void::Void { }

        fun g(a: &std::boolean::Bool) -> std::void::Void {
            f(a)
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionCallNoValidSignaturesError)
    def test_invalid_function_call_argument_convention_mismatch_8(self):
        # ref-mut borrow parameter & ref borrow argument
        """
        fun f(a: &&mut std::boolean::Bool) -> std::void::Void { }

        fun g(a: &std::boolean::Bool) -> std::void::Void {
            f(a)
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionCallNoValidSignaturesError)
    def test_invalid_function_call_argument_convention_mismatch_9(self):
        # mut-mut borrow parameter & ref borrow argument
        """
        fun f(a: &mut &mut std::boolean::Bool) -> std::void::Void { }

        fun g(a: &mut std::boolean::Bool) -> std::void::Void {
            f(a)
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionCallNoValidSignaturesError)
    def test_invalid_function_call_argument_convention_mismatch_10(self):
        # mut-ref borrow parameter & ref borrow argument
        """
        fun f(a: &mut &std::boolean::Bool) -> std::void::Void { }

        fun g(a: &mut std::boolean::Bool) -> std::void::Void {
            f(a)
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryOverlapUsageError)
    def test_invalid_function_call_argument_group_invalid_memory_overlap_2(self):
        # mut borrow variable & mut borrow attribute
        """
        cls A {
            a: std::boolean::Bool
            b: std::boolean::Bool
        }

        fun f(a: &mut A, b: &mut std::boolean::Bool) -> std::void::Void { }

        fun g(mut a: A) -> std::void::Void {
            f(&mut a, &mut a.b)
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryOverlapUsageError)
    def test_invalid_function_call_argument_group_invalid_memory_overlap_3(self):
        # ref borrow variable & move attribute
        """
        cls A {
            a: std::boolean::Bool
            b: std::boolean::Bool
        }

        fun f(a: &A, b: std::boolean::Bool) -> std::void::Void { }

        fun g(a: A) -> std::void::Void {
            f(&a, a.b)
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryOverlapUsageError)
    def test_invalid_function_call_argument_group_invalid_memory_overlap_4(self):
        # mut borrow variable & move attribute
        """
        cls A {
            a: std::boolean::Bool
            b: std::boolean::Bool
        }

        fun f(a: &mut A, b: std::boolean::Bool) -> std::void::Void { }

        fun g(mut a: A) -> std::void::Void {
            f(&mut a, a.b)
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryOverlapUsageError)
    def test_invalid_function_call_argument_group_invalid_memory_overlap_7(self):
        # ref borrow variable & mut borrow attribute
        """
        cls A {
            a: std::boolean::Bool
            b: std::boolean::Bool
        }

        fun f(a: &A, b: &mut std::boolean::Bool) -> std::void::Void { }

        fun g(mut a: A) -> std::void::Void {
            f(&a, &mut a.b)
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryOverlapUsageError)
    def test_invalid_function_call_argument_group_invalid_memory_overlap_8(self):
        # mut borrow variable & ref borrow attribute
        """
        cls A {
            a: std::boolean::Bool
            b: std::boolean::Bool
        }

        fun f(a: &mut A, b: &std::boolean::Bool) -> std::void::Void { }

        fun g(mut a: A) -> std::void::Void {
            f(&mut a, &a.b)
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryOverlapUsageError)
    def test_invalid_function_call_argument_group_invalid_memory_overlap_10(self):
        # mut borrow attribute & mut borrow variable
        """
        cls A {
            a: std::boolean::Bool
            b: std::boolean::Bool
        }

        fun f(a: &mut std::boolean::Bool, b: &mut A) -> std::void::Void { }

        fun g(mut a: A) -> std::void::Void {
            f(&mut a.b, &mut a)
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryOverlapUsageError)
    def test_invalid_function_call_argument_group_invalid_memory_overlap_11(self):
        # ref borrow attribute & move variable
        """
        cls A {
            a: std::boolean::Bool
            b: std::boolean::Bool
        }

        fun f(a: &std::boolean::Bool, b: A) -> std::void::Void { }

        fun g(a: A) -> std::void::Void {
            f(&a.b, a)
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryOverlapUsageError)
    def test_invalid_function_call_argument_group_invalid_memory_overlap_12(self):
        # mut borrow attribute & move variable
        """
        cls A {
            a: std::boolean::Bool
            b: std::boolean::Bool
        }

        fun f(a: &mut std::boolean::Bool, b: A) -> std::void::Void { }

        fun g(mut a: A) -> std::void::Void {
            f(&mut a.b, a)
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryOverlapUsageError)
    def test_invalid_function_call_argument_group_invalid_memory_overlap_15(self):
        # ref borrow attribute & mut borrow variable
        """
        cls A {
            a: std::boolean::Bool
            b: std::boolean::Bool
        }

        fun f(a: &std::boolean::Bool, b: &mut A) -> std::void::Void { }

        fun g(mut a: A) -> std::void::Void {
            f(&a.b, &mut a)
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryOverlapUsageError)
    def test_invalid_function_call_argument_group_invalid_memory_overlap_16(self):
        # mut borrow attribute & ref borrow variable
        """
        cls A {
            a: std::boolean::Bool
            b: std::boolean::Bool
        }

        fun f(a: &mut std::boolean::Bool, b: &A) -> std::void::Void { }

        fun g(mut a: A) -> std::void::Void {
            f(&mut a.b, &a)
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryOverlapUsageError)
    def test_invalid_function_call_argument_group_invalid_memory_overlap_18(self):
        # mut borrow variable & mut borrow variable
        """
        cls A {
            a: std::boolean::Bool
            b: std::boolean::Bool
        }

        fun f(a: &mut A, b: &mut A) -> std::void::Void { }

        fun g(mut a: A) -> std::void::Void {
            f(&mut a, &mut a)
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryOverlapUsageError)
    def test_invalid_function_call_argument_group_invalid_memory_overlap_19(self):
        # ref borrow variable & move variable
        """
        cls A {
            a: std::boolean::Bool
            b: std::boolean::Bool
        }

        fun f(a: &A, b: A) -> std::void::Void { }

        fun g(a: A) -> std::void::Void {
            f(&a, a)
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryOverlapUsageError)
    def test_invalid_function_call_argument_group_invalid_memory_overlap_20(self):
        # mut borrow variable & move variable
        """
        cls A {
            a: std::boolean::Bool
            b: std::boolean::Bool
        }

        fun f(a: &mut A, b: A) -> std::void::Void { }

        fun g(mut a: A) -> std::void::Void {
            f(&mut a, a)
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryOverlapUsageError)
    def test_invalid_function_call_argument_group_invalid_memory_overlap_23(self):
        # ref borrow variable & mut borrow variable
        """
        cls A {
            a: std::boolean::Bool
            b: std::boolean::Bool
        }

        fun f(a: &A, b: &mut A) -> std::void::Void { }

        fun g(mut a: A) -> std::void::Void {
            f(&a, &mut a)
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryOverlapUsageError)
    def test_invalid_function_call_argument_group_invalid_memory_overlap_24(self):
        # mut borrow variable & ref borrow variable
        """
        cls A {
            a: std::boolean::Bool
            b: std::boolean::Bool
        }

        fun f(a: &mut A, b: &A) -> std::void::Void { }

        fun g(mut a: A) -> std::void::Void {
            f(&mut a, &a)
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
    def test_valid_function_call_argument_convention_match_4a(self):
        # ref-ref borrow parameter & ref-ref argument
        """
        fun f(a: &&std::boolean::Bool) -> std::void::Void { }

        fun g(a: &&std::boolean::Bool) -> std::void::Void {
            f(a)
        }
        """

    @should_pass_compilation()
    def test_valid_function_call_argument_convention_match_4b(self):
        # ref-ref borrow parameter & ref-ref argument
        """
        fun f(a: &&std::boolean::Bool) -> std::void::Void { }

        fun g(a: &std::boolean::Bool) -> std::void::Void {
            f(&a)
        }
        """

    @should_pass_compilation()
    def test_valid_function_call_argument_convention_match_5a(self):
        # ref-mut borrow parameter & ref-mut borrow argument
        """
        fun f(a: &&mut std::boolean::Bool) -> std::void::Void { }

        fun g(a: &&mut std::boolean::Bool) -> std::void::Void {
            f(a)
        }
        """

    @should_pass_compilation()
    def test_valid_function_call_argument_convention_match_5b(self):
        # ref-mut borrow parameter & ref-mut borrow argument
        """
        fun f(a: &&mut std::boolean::Bool) -> std::void::Void { }

        fun g(a: &mut std::boolean::Bool) -> std::void::Void {
            f(&a)
        }
        """

    @should_pass_compilation()
    def test_valid_function_call_argument_convention_match_6a(self):
        # mut-ref borrow parameter & mut-ref borrow argument
        """
        fun f(a: &mut &std::boolean::Bool) -> std::void::Void { }

        fun g(a: &mut &std::boolean::Bool) -> std::void::Void {
            f(a)
        }
        """

    @should_pass_compilation()
    def test_valid_function_call_argument_convention_match_6b(self):
        # mut-ref borrow parameter & mut-ref borrow argument
        """
        fun f(a: &mut &std::boolean::Bool) -> std::void::Void { }

        fun g(mut a: &std::boolean::Bool) -> std::void::Void {
            f(&mut a)
        }
        """

    @should_pass_compilation()
    def test_valid_function_call_argument_convention_match_7a(self):
        # mut-mut borrow parameter & mut-mut borrow argument
        """
        fun f(a: &mut &mut std::boolean::Bool) -> std::void::Void { }

        fun g(a: &mut &mut std::boolean::Bool) -> std::void::Void {
            f(a)
        }
        """

    @should_pass_compilation()
    def test_valid_function_call_argument_convention_match_7b(self):
        # mut-mut borrow parameter & mut-mut borrow argument
        """
        fun f(a: &mut &mut std::boolean::Bool) -> std::void::Void { }

        fun g(mut a: &mut std::boolean::Bool) -> std::void::Void {
            f(&mut a)
        }
        """

    @should_pass_compilation()
    def test_valid_function_call_argument_group_valid_memory_overlap_1(self):
        # ref borrow variable & ref borrow attribute
        """
        cls A {
            a: std::boolean::Bool
            b: std::boolean::Bool
        }

        fun f(a: &A, b: &std::boolean::Bool) -> std::void::Void { }

        fun g(a: A) -> std::void::Void {
            f(&a, &a.b)
        }
        """

    @should_pass_compilation()
    def test_valid_function_call_argument_group_valid_memory_overlap_2(self):
        # ref borrow attribute & ref borrow variable
        """
        cls A {
            a: std::boolean::Bool
            b: std::boolean::Bool
        }

        fun f(a: &std::boolean::Bool, b: &A) -> std::void::Void { }

        fun g(a: A) -> std::void::Void {
            f(&a.b, &a)
        }
        """

    @should_pass_compilation()
    def test_valid_function_call_argument_group_valid_memory_overlap_3(self):
        # ref borrow variable & ref borrow variable
        """
        cls A {
            a: std::boolean::Bool
            b: std::boolean::Bool
        }

        fun f(a: &A, b: &A) -> std::void::Void { }

        fun g(a: A) -> std::void::Void {
            f(&a, &a)
        }
        """

    @should_pass_compilation()
    def test_valid_function_call_argument_group_valid_memory_overlap_4(self):
        # mut borrow attribute 1 & ref borrow attribute 2
        """
        cls A {
            a: std::boolean::Bool
            b: std::boolean::Bool
        }

        fun f(a: &mut std::boolean::Bool, b: &std::boolean::Bool) -> std::void::Void { }

        fun g(mut a: A) -> std::void::Void {
            f(&mut a.a, &a.b)
        }
        """

    @should_pass_compilation()
    def test_valid_function_call_argument_group_valid_overlap_5(self):
        # ref borrow attribute 1 & mut borrow attribute 2
        """
        cls A {
            a: std::boolean::Bool
            b: std::boolean::Bool
        }

        fun f(a: &std::boolean::Bool, b: &mut std::boolean::Bool) -> std::void::Void { }

        fun g(mut a: A) -> std::void::Void {
            f(&a.a, &mut a.b)
        }
        """

    @should_pass_compilation()
    def test_valid_function_call_argument_group_valid_overlap_6(self):
        # mut borrow attribute 1 & mut borrow attribute 2
        """
        cls A {
            a: std::boolean::Bool
            b: std::boolean::Bool
        }

        fun f(a: &mut std::boolean::Bool, b: &mut std::boolean::Bool) -> std::void::Void { }

        fun g(mut a: A) -> std::void::Void {
            f(&mut a.a, &mut a.b)
        }
        """

    @should_pass_compilation()
    def test_valid_function_call_argument_group_valid_overlap_7(self):
        # ref borrow attribute 1 & ref borrow attribute 2
        """
        cls A {
            a: std::boolean::Bool
            b: std::boolean::Bool
        }

        fun f(a: &std::boolean::Bool, b: &std::boolean::Bool) -> std::void::Void { }

        fun g(a: A) -> std::void::Void {
            f(&a.a, &a.b)
        }
        """
