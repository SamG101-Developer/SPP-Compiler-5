from unittest import TestCase

from tst._Utils import *


class TestGenExpressionAst(TestCase):
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
        cor foo() -> std::GenMov[std::BigInt] {
            gen &1
        }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_gen_expression_convention_mismatch_ref(self):
        """
        cor foo() -> std::GenRef[std::BigInt] {
            gen &mut 1
        }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_gen_expression_convention_mismatch_mut(self):
        """
        cor foo() -> std::GenMut[std::BigInt] {
            gen 1
        }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_gen_expression_type_mismatch(self):
        """
        cor foo() -> std::GenMov[std::BigInt] {
            gen false
        }
        """

    @should_pass_compilation()
    def test_valid_gen_expression_mov(self):
        """
        cor foo() -> std::GenMov[std::BigInt] {
            gen 1
        }
        """

    @should_pass_compilation()
    def test_valid_gen_expression_ref(self):
        """
        cor foo() -> std::GenRef[std::BigInt] {
            gen &1
        }
        """

    @should_pass_compilation()
    def test_valid_gen_expression_mut(self):
        """
        cor foo() -> std::GenMut[std::BigInt] {
            gen &mut 1
        }
        """