from tests._Utils import *


# Todo: test "gen with"


class TestGenExpressionAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.FunctionSubroutineContainsGenExpressionError)
    def test_invalid_gen_expression_in_subroutine(self):
        """
        fun foo() -> std::void::Void {
            gen 1
        }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_gen_expression_convention_mismatch_1a(self):
        """
        cor foo() -> std::generator::Gen[std::number::bigint::BigInt] {
            gen &1
        }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_gen_expression_convention_mismatch_1b(self):
        """
        cor foo() -> std::generator::Gen[std::number::bigint::BigInt] {
            gen &mut 1
        }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_gen_expression_convention_mismatch_2a(self):
        """
        cor foo() -> std::generator::Gen[&std::number::bigint::BigInt] {
            gen 1
        }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_gen_expression_convention_mismatch_3a(self):
        """
        cor foo() -> std::generator::Gen[&mut std::number::bigint::BigInt] {
            gen 1
        }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_gen_expression_convention_mismatch_3b(self):
        """
        cor foo() -> std::generator::Gen[&mut std::number::bigint::BigInt] {
            gen &1
        }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_gen_expression_type_mismatch(self):
        """
        cor foo() -> std::generator::Gen[std::number::bigint::BigInt] {
            gen false
        }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_gen_expression_unroll(self):
        """
        cor foo() -> std::generator::Gen[&std::number::bigint::BigInt] {
            gen &1
            gen &2
            gen &3
        }

        cor bar() -> std::generator::Gen[&mut std::number::bigint::BigInt] {
            gen &mut 0
            gen with foo()
            gen &mut 4
        }
        """

    @should_pass_compilation()
    def test_valid_gen_expression_convention_mismatch_ref_coerce(self):
        """
        cor foo() -> std::generator::Gen[&std::number::bigint::BigInt] {
            gen &mut 1
        }
        """

    @should_pass_compilation()
    def test_valid_gen_expression_mov(self):
        """
        cor foo() -> std::generator::Gen[std::number::bigint::BigInt] {
            gen 1
        }
        """

    @should_pass_compilation()
    def test_valid_gen_expression_ref(self):
        """
        cor foo() -> std::generator::Gen[&std::number::bigint::BigInt] {
            gen &1
        }
        """

    @should_pass_compilation()
    def test_valid_gen_expression_mut(self):
        """
        cor foo() -> std::generator::Gen[&mut std::number::bigint::BigInt] {
            gen &mut 1
        }
        """

    @should_pass_compilation()
    def test_valid_gen_expression_unroll(self):
        """
        cor foo() -> std::generator::Gen[&mut std::number::bigint::BigInt] {
            gen &mut 1
            gen &mut 2
            gen &mut 3
        }

        cor bar() -> std::generator::Gen[&mut std::number::bigint::BigInt] {
            gen &mut 0
            gen with foo()
            gen &mut 4
        }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_gen_expression_received_type_mismatch_1a(self):
        """
        cor foo() -> std::generator::Gen[std::number::bigint::BigInt, std::boolean::Bool] {
            gen &1
        }

        fun foo(y: std::number::bigint::BigInt) -> std::void::Void {
            let g = foo()
            let mut x = g.resume(false)
            x = y
        }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_gen_expression_received_type_mismatch_1b(self):
        """
        cor foo() -> std::generator::Gen[std::number::bigint::BigInt, std::boolean::Bool] {
            gen &1
        }

        fun foo(y: &mut std::number::bigint::BigInt) -> std::void::Void {
            let g = foo()
            let mut x = g.resume(false)
            x = y
        }
        """
