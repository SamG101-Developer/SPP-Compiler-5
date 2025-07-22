from tests._Utils import *


class TestCoroutinePrototypeAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.FunctionCoroutineInvalidReturnTypeError)
    def test_invalid_coroutine_invalid_return_type(self):
        """
        cor c() -> std::void::Void { }
        """

    @should_pass_compilation()
    def test_valid_coroutine_valid_return_type_mov(self):
        """
        cor c() -> std::generator::Gen[std::bignum::bigint::BigInt] {
            gen 1
        }
        """

    @should_pass_compilation()
    def test_valid_coroutine_valid_return_type_mut(self):
        """
        cor c() -> std::generator::Gen[&mut std::bignum::bigint::BigInt] {
            gen &mut 1
        }
        """

    @should_pass_compilation()
    def test_valid_coroutine_valid_return_type_ref(self):
        """
        cor c() -> std::generator::Gen[&std::bignum::bigint::BigInt] {
            gen &1
        }
        """

    @should_pass_compilation()
    def test_valid_coroutine_pinned_borrows(self):
        """
        cor c(a: &mut std::boolean::Bool, b: &std::bignum::bigint::BigInt) -> std::generator::Gen[std::bignum::bigint::BigInt] { }
        fun f() -> std::void::Void {
            let (mut x, y) = (false, 123)
            c(&mut x, &y)
        }
        """
