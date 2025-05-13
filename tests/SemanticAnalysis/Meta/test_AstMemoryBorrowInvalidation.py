from tests._Utils import *


class TestAstMemoryBorrowInvalidation(CustomTestCase):
    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_invalid_borrow_invalidated_by_next_borrow_mut_mut_with_let(self):
        # When yielding a second borrow, the first one should be invalidated.
        """
        cls MyType { }
        sup MyType {
            cor custom_iter_mut(&mut self) -> std::generator::Gen[&mut std::string::Str, std::boolean::Bool] { }
        }

        fun test() -> std::void::Void {
            let mut object = MyType()
            let generator = object.custom_iter_mut()
            let borrow1 = generator.res(false)
            let borrow2 = generator.res(false)
            let value = borrow1
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_invalid_borrow_invalidated_by_next_borrow_mut_mut_with_assign(self):
        # When yielding a second borrow, the first one should be invalidated.
        """
        cls MyType { }
        sup MyType {
            cor custom_iter_mut(&mut self) -> std::generator::Gen[&mut std::string::Str, std::boolean::Bool] { }
        }

        fun test() -> std::void::Void {
            let (borrow1, borrow2): (&mut std::string::Str, &mut std::string::Str)
            let mut object = MyType()
            let generator = object.custom_iter_mut()
            borrow1 = generator.res(false)
            borrow2 = generator.res(false)
            let value = borrow1
        }
        """

    @should_pass_compilation()
    def test_valid_borrow_usage_no_invalidation_ref_ref_with_let(self):
        # Immutable borrows don't invalidate other immutable borrows.
        """
        cls MyType {
            x: std::number::bigint::BigInt
        }

        sup MyType {
            cor custom_iter_ref(&self) -> std::generator::Gen[&std::number::bigint::BigInt, std::boolean::Bool] { }
        }

        fun f() -> std::void::Void {
            let my_type = MyType(x=123)
            let generator1 = my_type.custom_iter_ref()
            let generator2 = my_type.custom_iter_ref()
            let a = generator2.res(false)
        }
        """

    @should_pass_compilation()
    def test_valid_borrow_usage_no_invalidation_ref_ref_with_assign(self):
        # Immutable borrows don't invalidate other immutable borrows.
        """
        cls MyType {
            x: std::number::bigint::BigInt
        }

        sup MyType {
            cor custom_iter_ref(&self) -> std::generator::Gen[&std::number::bigint::BigInt, std::boolean::Bool] { }
        }

        fun f() -> std::void::Void {
            let (generator1, generator2): (std::generator::Gen[&std::number::bigint::BigInt, std::boolean::Bool], std::generator::Gen[&std::number::bigint::BigInt, std::boolean::Bool])
            let my_type = MyType(x=123)
            generator1 = my_type.custom_iter_ref()
            generator2 = my_type.custom_iter_ref()
            let a = generator2.res(false)
        }
        """
