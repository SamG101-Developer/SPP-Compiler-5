from tests._Utils import *


# todo: test coroutine lambdas


class LambdaExpressionAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.MutabilityInvalidMutationError)
    def test_invalid_lambda_expression_mutate_capture(self):
        """
        use std::number::u32::U32
        fun f() -> std::void::Void {
            let a = 5_u32
            let x = |b: U32 caps a| { a = b }
            x()
        }
        """

    @should_fail_compilation(SemanticErrors.IdentifierUnknownError)
    def test_invalid_lambda_expression_accessing_out_of_scope(self):
        """
        use std::number::u32::U32
        fun f() -> std::void::Void {
            let a = 5_u32
            let x = || a
        }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_lambda_expression_different_return_types(self):
        """
        use std::number::u32::U32
        fun f() -> std::void::Void {
            let a = 5_u32
            let x = |caps a| case a < 5_u32 { ret true } else { ret 123 }
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryMovedWhilstPinnedError)
    def test_invalid_lambda_expression_move_pinned_by_ref(self):
        """
        use std::number::u32::U32
        use std::function::FunRef

        fun g(func: FunRef[(), U32]) -> std::void::Void { }

        fun f() -> std::void::Void {
            let a = 5_u32
            let x = |caps &a| 123_u32
            g(x)
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryMovedWhilstPinnedError)
    def test_invalid_lambda_expression_move_pinned_by_mut(self):
        """
        use std::number::u32::U32
        use std::function::FunMut

        fun g(func: FunMut[(), U32]) -> std::void::Void { }

        fun f() -> std::void::Void {
            let mut a = 5_u32
            let x = |caps &mut a| 123_u32
            g(x)
        }
        """

    @should_fail_compilation(SemanticErrors.MutabilityInvalidMutationError)
    def test_valid_lambda_expression_lambda_type_mut(self):
        """
        use std::number::u32::U32
        use std::function::FunMut

        fun f() -> std::void::Void {
            let a = 5_u32
            let x: FunMut[(), U32] = |caps &mut a| 123_u32
        }
        """

    @should_fail_compilation(SemanticErrors.IdentifierUnknownError)
    def test_invalid_lambda_expression_unknown_capture_variable(self):
        """
        use std::number::u32::U32

        fun f() -> std::void::Void {
            let a = 5_u32
            let x = |b: U32 caps a, c| { b = a }
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_invalid_lambda_expression_with_capture_mov(self):
        """
        use std::number::u32::U32
        fun f() -> std::void::Void {
            let a = "test"
            let x = |caps a| a
            let b = a
        }
        """

    @should_pass_compilation()
    def test_valid_lambda_expression_simple(self):
        """
        fun f() -> std::void::Void {
            let x = || 5_u32
        }
        """

    @should_pass_compilation()
    def test_valid_lambda_expression_with_parameters(self):
        """
        use std::number::u32::U32
        fun f() -> std::void::Void {
            let x = |a: U32, b: U32| a + b
        }
        """

    @should_pass_compilation()
    def test_valid_lambda_expression_with_capture_mov(self):
        """
        use std::number::u32::U32
        fun f() -> std::void::Void {
            let a = 5_u32
            let x = |b: U32, c: U32 caps a| a + b + c
        }
        """

    @should_pass_compilation()
    def test_valid_lambda_expression_with_capture_ref(self):
        """
        use std::number::u32::U32
        fun f() -> std::void::Void {
            let a = 5_u32
            let x = |mut b: &U32 caps &a| { b = a }
        }
        """

    @should_pass_compilation()
    def test_valid_lambda_expression_with_capture_mut(self):
        """
        use std::number::u32::U32
        fun f() -> std::void::Void {
            let mut a = 5_u32
            let x = |mut b: &mut U32 caps &mut a| { b = a }
        }
        """

    @should_pass_compilation()
    def test_valid_lambda_expression_lambda_type_mov(self):
        """
        use std::number::u32::U32
        use std::function::FunMov

        fun f() -> std::void::Void {
            let a = 5_u32
            let x: FunMov[(), U32] = |caps a| 123_u32
        }
        """

    @should_pass_compilation()
    def test_valid_lambda_expression_lambda_type_mut(self):
        """
        use std::number::u32::U32
        use std::function::FunMut

        fun f() -> std::void::Void {
            let mut a = 5_u32
            let x: FunMut[(), U32] = |caps &mut a| 123_u32
        }
        """

    @should_pass_compilation()
    def test_valid_lambda_expression_lambda_type_ref(self):
        """
        use std::number::u32::U32
        use std::function::FunRef

        fun f() -> std::void::Void {
            let a = 5_u32
            let x: FunRef[(), U32] = |caps &a| 123_u32
        }
        """

    @should_pass_compilation()
    def test_valid_lambda_expression_correct_return_type(self):
        """
        use std::number::u32::U32
        fun f() -> std::void::Void {
            let a = 5_u32
            let x = |caps a| a
            let mut y = x()
            y = 123_u32
        }
        """

    @should_pass_compilation()
    def test_invalid_lambda_expression_with_capture_mov_use_capture(self):
        """
        use std::number::u32::U32
        fun f() -> std::void::Void {
            let a = "test"
            let x = |caps a| a
        }
        """
