from tests._Utils import *


class TestCoroutinePrototypeAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.FunctionCoroutineInvalidReturnTypeError)
    def test_invalid_coroutine_invalid_return_type(self):
        """
        cor c() -> std::void::Void { }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_invalid_coroutine_invalidated_by_moving_borrow(self):
        """
        cor c(a: &std::number::BigInt) -> std::generator::Gen[std::number::BigInt, std::boolean::Bool] { }
        fun f() -> std::void::Void {
            let x = 123
            let g = c(&x)
            let y = x
            let h = g.res(false)
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_invalid_coroutine_invalidated_previous_borrow(self):
        """
        cor c() -> std::generator::Gen[&std::number::BigInt, std::boolean::Bool] { }
        fun f() -> std::void::Void {
            let g = c()
            let a = g.res(false)
            let b = g.res(false)
            let c = a
        }
        """

    @should_pass_compilation()
    def test_valid_coroutine_valid_return_type_mov(self):
        """
        cor c() -> std::generator::Gen[std::number::BigInt] {
            gen 1
        }
        """

    @should_pass_compilation()
    def test_valid_coroutine_valid_return_type_mut(self):
        """
        cor c() -> std::generator::Gen[&mut std::number::BigInt] {
            gen &mut 1
        }
        """

    @should_pass_compilation()
    def test_valid_coroutine_valid_return_type_ref(self):
        """
        cor c() -> std::generator::Gen[&std::number::BigInt] {
            gen &1
        }
        """

    @should_pass_compilation()
    def test_valid_coroutine_pinned_borrows(self):
        """
        cor c(a: &mut std::boolean::Bool, b: &std::number::BigInt) -> std::generator::Gen[std::number::BigInt] { }
        fun f() -> std::void::Void {
            let (mut x, y) = (false, 123)
            c(&mut x, &y)
        }
        """
