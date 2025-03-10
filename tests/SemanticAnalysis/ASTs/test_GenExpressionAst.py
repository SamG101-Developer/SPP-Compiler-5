from tests._Utils import *


# Todo: test "gen with"


class TestGenExpressionAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.FunctionSubroutineContainsGenExpressionError)
    def test_invalid_gen_expression_in_subroutine(self):
        """
        fun foo() -> std::Void {
            gen 1
        }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_gen_expression_convention_mismatch_mov(self):
        """
        cor foo() -> std::Gen[std::BigInt] {
            gen &1
        }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_gen_expression_convention_mismatch_mov_2(self):
        """
        cor foo() -> std::Gen[std::BigInt] {
            gen &mut 1
        }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_gen_expression_convention_mismatch_ref(self):
        """
        cor foo() -> std::Gen[&std::BigInt] {
            gen &mut 1
        }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_gen_expression_convention_mismatch_ref_2(self):
        """
        cor foo() -> std::Gen[&std::BigInt] {
            gen 1
        }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_gen_expression_convention_mismatch_mut(self):
        """
        cor foo() -> std::Gen[&mut std::BigInt] {
            gen 1
        }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_gen_expression_convention_mismatch_mut_2(self):
        """
        cor foo() -> std::Gen[&mut std::BigInt] {
            gen &1
        }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_gen_expression_type_mismatch(self):
        """
        cor foo() -> std::Gen[std::BigInt] {
            gen false
        }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_gen_expression_unroll(self):
        """
        cor foo() -> std::Gen[&std::BigInt] {
            gen &1
            gen &2
            gen &3
        }

        cor bar() -> std::Gen[&mut std::BigInt] {
            gen &mut 0
            gen with foo()
            gen &mut 4
        }
        """

    @should_pass_compilation()
    def test_valid_gen_expression_mov(self):
        """
        cor foo() -> std::Gen[std::BigInt] {
            gen 1
        }
        """

    @should_pass_compilation()
    def test_valid_gen_expression_ref(self):
        """
        cor foo() -> std::Gen[&std::BigInt] {
            gen &1
        }
        """

    @should_pass_compilation()
    def test_valid_gen_expression_mut(self):
        """
        cor foo() -> std::Gen[&mut std::BigInt] {
            gen &mut 1
        }
        """

    @should_pass_compilation()
    def test_valid_gen_expression_unroll(self):
        """
        cor foo() -> std::Gen[&mut std::BigInt] {
            gen &mut 1
            gen &mut 2
            gen &mut 3
        }

        cor bar() -> std::Gen[&mut std::BigInt] {
            gen &mut 0
            gen with foo()
            gen &mut 4
        }
        """
