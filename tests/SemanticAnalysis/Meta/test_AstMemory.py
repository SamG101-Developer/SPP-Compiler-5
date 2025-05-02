from tests._Utils import *


class TestAstMemory(CustomTestCase):
    @should_fail_compilation(SemanticErrors.MemoryInconsistentlyInitializedError)
    def test_invalid_memory_inconsistently_initialized_moved(self):
        # Move an initialized value in one branch and not in the other.
        """
        cls Point {
            x: std::number::bigint::BigInt
            y: std::number::bigint::BigInt
        }

        fun f() -> std::void::Void {
            let p = Point(x=5, y=5)

            case 1 of
                == 1 { let r = p }
                == 2 { }

            let r = p
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryInconsistentlyInitializedError)
    def test_invalid_memory_inconsistently_initialized_initialized(self):
        # Initialize a non-initialized value in one branch and not in the other.
        """
        cls Point {
            x: std::number::bigint::BigInt
            y: std::number::bigint::BigInt
        }

        fun f() -> std::void::Void {
            let p: Point
            case 1 of
                == 1 { p = Point(x=5, y=6) }
                == 2 { }

            let r = p
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryInconsistentlyInitializedError)
    def test_invalid_memory_inconsistently_initialized_partially_moved_1(self):
        # Partially move an initialized value in one branch and not in the other.
        """
        cls Point {
            x: std::number::bigint::BigInt
            y: std::number::bigint::BigInt
        }

        fun f() -> std::void::Void {
            let p = Point(x=5, y=6)
            case 1 of
                == 1 { let x = p.x }
                == 2 { }

            let r = p
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryInconsistentlyInitializedError)
    def test_invalid_memory_inconsistently_initialized_partially_moved_2(self):
        # Partially move different parts of an initialized value in both branches.
        """
        cls Point {
            x: std::number::bigint::BigInt
            y: std::number::bigint::BigInt
        }

        fun f() -> std::void::Void {
            let p = Point(x=5, y=6)
            case 1 of
                == 1 { let x = p.x }
                == 2 { let y = p.y }

            let r = p
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryInconsistentlyInitializedError)
    def test_invalid_memory_inconsistently_initialized_partially_initialized_1(self):
        # Partially initialize different parts of a partially initialized value in one branch and not the other.
        """
        cls Point {
            x: std::number::bigint::BigInt
            y: std::number::bigint::BigInt
        }

        fun f() -> std::void::Void {
            let mut p = Point(x=5, y=6)
            let x = p.x

            case 1 of
                == 1 { p.x = 123 }
                == 2 { }

            let r = p
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryInconsistentlyInitializedError)
    def test_invalid_memory_inconsistently_initialized_partially_initialized_2(self):
        # Partially initialize different parts of a partially initialized value in both branches.
        """
        cls Point {
            x: std::number::bigint::BigInt
            y: std::number::bigint::BigInt
        }

        fun f() -> std::void::Void {
            let mut p = Point(x=5, y=6)
            let x = p.x
            let y = p.y

            case 1 of
                == 1 { p.x = 123 }
                == 2 { p.y = 456 }

            let r = p
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryInconsistentlyPinnedError)
    def test_invalid_memory_inconsistently_pinned_1(self):
        # Cause a value to be pinned in one branch and not in the other.
        """
        cls Point {
            x: std::number::bigint::BigInt
            y: std::number::bigint::BigInt
        }

        cor c(p: &Point) -> std::generator::Gen[std::boolean::Bool] { }

        fun f() -> std::void::Void {
            let p = Point(x=5, y=5)
            case 1 of
                == 1 { c(&p) }
                == 2 { }

            let r = p
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryInconsistentlyPinnedError)
    def test_invalid_memory_inconsistently_pinned_2(self):
        # Cause part of a value to be pinned in one branch and not in the other.
        """
        cls Point {
            x: std::number::bigint::BigInt
            y: std::number::bigint::BigInt
        }

        cor c(x: &std::number::bigint::BigInt) -> std::generator::Gen[std::boolean::Bool] { }

        fun f() -> std::void::Void {
            let p = Point(x=5, y=5)
            case 1 of
                == 1 { c(&p.x) }
                == 2 { }

            let r = p
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryInconsistentlyPinnedError)
    def test_invalid_memory_inconsistently_pinned_3(self):
        # Cause different parts of a value to be pinned in both branches.
        """
        cls Point {
            x: std::number::bigint::BigInt
            y: std::number::bigint::BigInt
        }

        cor c(x: &std::number::bigint::BigInt) -> std::generator::Gen[std::boolean::Bool] { }

        fun f() -> std::void::Void {
            let p = Point(x=5, y=5)
            case 1 of
                == 1 { c(&p.x) }
                == 2 { c(&p.y) }

            let r = p
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_invalid_memory_not_initialized_usage_1(self):
        # Use a non-initialized value (never given a value / use-after-free).
        """
        cls Point {
            x: std::number::bigint::BigInt
            y: std::number::bigint::BigInt
        }

        fun f() -> std::void::Void {
            let p: Point
            let q = p
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_invalid_memory_not_initialized_usage_2(self):
        # Use a non-initialized value (value has been moved already / double-free).
        """
        cls Point {
            x: std::number::bigint::BigInt
            y: std::number::bigint::BigInt
        }

        fun f() -> std::void::Void {
            let p = Point(x=5, y=5)
            let q = p
            let r = p
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_invalid_memory_not_initialized_usage_3(self):
        # Use part of a non-initialized value (never given a value / use-after-free).
        """
        cls Point {
            x: std::number::bigint::BigInt
            y: std::number::bigint::BigInt
        }

        fun f() -> std::void::Void {
            let p: Point
            let x = p.x
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_invalid_memory_not_initialized_usage_4(self):
        # Use part of a non-initialized value (value has been moved already / double-free).
        """
        cls Point {
            x: std::number::bigint::BigInt
            y: std::number::bigint::BigInt
        }

        fun f() -> std::void::Void {
            let p = Point(x=5, y=5)
            let q = p
            let x = p.x
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_invalid_memory_partially_initialized_usage_1(self):
        # Use part of a partially-initialized value (value has been moved already / double-free).
        """
        cls Point {
            x: std::number::bigint::BigInt
            y: std::number::bigint::BigInt
        }

        fun f() -> std::void::Void {
            let p = Point(x=5, y=5)
            let x1 = p.x
            let x2 = p.x
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryPartiallyInitializedUsageError)
    def test_invalid_memory_partially_initialized_usage_2(self):
        # Use a value that has been partially moved.
        """
        cls Point {
            x: std::number::bigint::BigInt
            y: std::number::bigint::BigInt
        }

        fun f() -> std::void::Void {
            let p = Point(x=5, y=5)
            let x = p.x
            let q = p
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryMovedFromBorrowedContextError)
    def test_invalid_memory_moved_from_borrowed_context_mut(self):
        # Create a partial move on a mutable borrow.
        """
        cls T { }

        cls Point {
            x: T
            y: T
        }

        fun f(p: &mut Point) -> std::void::Void {
            let x = p.x
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryMovedFromBorrowedContextError)
    def test_invalid_memory_moved_from_borrowed_context_ref(self):
        # Create a partial move in an immutable borrow.
        """
        cls T { }

        cls Point {
            x: T
            y: T
        }

        fun f(p: &Point) -> std::void::Void {
            let x = p.x
        }
        """

    @should_pass_compilation()
    def test_valid_memory_multiple_partial_moves(self):
        # Move different parts of a value over multiple expressions.
        """
        cls Point {
            x: std::number::bigint::BigInt
            y: std::number::bigint::BigInt
        }

        fun f() -> std::void::Void {
            let p = Point(x=5, y=5)
            let x = p.x
            let y = p.y
        }
        """

    @should_pass_compilation()
    def test_valid_memory_copy(self):
        # Perform a "double move" when the compiler superimposes Copy over the type.
        """
        fun f() -> std::void::Void {
            let x = 123_uz
            let a = x
            let b = x
        }
        """

    @should_pass_compilation()
    def test_valid_memory_copy_custom(self):
        # Perform a "double move" when the use superimposes Copy over the type.
        """
        cls Point {
            x: std::number::bigint::BigInt
            y: std::number::bigint::BigInt
        }

        sup Point ext std::copy::Copy { }

        fun f() -> std::void::Void {
            let p = Point(x=5, y=5)
            let a = p
            let b = p
        }
        """

    @should_pass_compilation()
    def test_valid_memory_copy_custom_generic(self):
        # Perform a "double move" when the use superimposes Copy over the generic type.
        """
        cls Point[T] {
            x: T
            y: T
        }

        sup [T] Point[T] ext std::copy::Copy { }

        fun f() -> std::void::Void {
            let p = Point(x=5, y=5)
            let a = p
            let b = p
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_invalid_borrow_invalidated_by_next_borrow_1(self):
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
    def test_invalid_borrow_invalidated_by_next_borrow_2(self):
        # When yielding a second borrow, the first one should be invalidated.
        """
        cls MyType { }
        sup MyType {
            cor custom_iter_ref(&self) -> std::generator::Gen[&std::string::Str, std::boolean::Bool] { }
            cor custom_iter_mut(&mut self) -> std::generator::Gen[&mut std::string::Str, std::boolean::Bool] { }
        }

        fun test() -> std::void::Void {
            let mut object = MyType()
            let generator_mut = object.custom_iter_mut()
            let borrow1 = generator_mut.res(false)
            let generator_ref = object.custom_iter_ref()
            let borrow2 = generator_ref.res(false)
            let value = borrow1
        }
        """

    @should_pass_compilation()
    def test_valid_ref_borrow_usage_invalidated(self):
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

    @should_fail_compilation(SemanticErrors.MemoryMovedWhilstPinnedError)
    def test_invalid_moving_coroutine_with_pins_mov(self):
        """
        cor g(a: &std::string::Str) -> std::generator::Gen[std::string::Str, std::boolean::Bool] { }

        fun f() -> std::void::Void {
            let x = "hello world"
            let coroutine = g(&x)
            let c = coroutine
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryMovedWhilstPinnedError)
    def test_invalid_moving_coroutine_with_pins_ret(self):
        """
        cor g(a: &std::string::Str) -> std::generator::Gen[std::string::Str, std::boolean::Bool] { }

        fun f() -> std::generator::Gen[std::string::Str, std::boolean::Bool] {
            let x = "hello world"
            let coroutine = g(&x)
            ret coroutine
        }
        """

    # TEST ALL INSTANCES OF A NON-INITIALIZED SYMBOL BEING USED

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_array(self):
        """
        fun f() -> std::void::Void {
            let elem: std::string::Str
            let a = [elem]
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_assignment(self):
        """
        cls Point {
            x: std::number::bigint::BigInt
            y: std::number::bigint::BigInt
        }

        fun f() -> std::void::Void {
            let mut point: Point
            point.x = 5
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_binary_expression_lhs(self):
        """
        fun f() -> std::void::Void {
            let elem: std::number::bigint::BigInt
            let a = elem + 123
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_binary_expression_rhs(self):
        """
        fun f() -> std::void::Void {
            let elem: std::number::bigint::BigInt
            let a = 123 + elem
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_case_expression_condition(self):
        """
        fun f() -> std::void::Void {
            let elem: std::number::bigint::BigInt
            case elem of
                == 1 { }
                == 2 { }
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_case_expression_branch(self):
        """
        fun f() -> std::void::Void {
            let elem: std::number::bigint::BigInt
            case 1 of
                == elem { }
                else { }
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_function_call_argument_unnamed(self):
        """
        fun g(a: std::string::Str) -> std::void::Void { }
        fun f() -> std::void::Void {
            let elem: std::string::Str
            let a = g(elem)
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_function_call_argument_named(self):
        """
        fun g(a: std::string::Str) -> std::void::Void { }
        fun f() -> std::void::Void {
            let elem: std::string::Str
            let a = g(a=elem)
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_gen_mov_expression(self):
        """
        cor f() -> std::generator::Gen[std::string::Str] {
            let elem: std::string::Str
            gen elem
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_gen_mut_expression(self):
        """
        cor f() -> std::generator::Gen[&mut std::string::Str] {
            let elem: std::string::Str
            gen &mut elem
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_gen_ref_expression(self):
        """
        cor f() -> std::generator::Gen[&std::string::Str] {
            let elem: std::string::Str
            gen &elem
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_generic_comp_argument_unnamed(self):
        """
        fun g[cmp n: std::string::Str]() -> std::void::Void { }

        fun f() -> std::void::Void {
            let elem: std::string::Str
            let a = g[elem]()
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_generic_comp_argument_named(self):
        """
        fun g[cmp n: std::string::Str]() -> std::void::Void { }

        fun f() -> std::void::Void {
            let elem: std::string::Str
            let a = g[n=elem]()
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_is_expression(self):
        """
        cls Point {
            x: std::number::bigint::BigInt
            y: std::number::bigint::BigInt
        }

        fun f() -> std::void::Void {
            let elem: Point
            case elem of
                is Point(x=0, y) { }
                is Point(x, y=0) { }
                else { }
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_lambda_capture_mov(self):
        """
        fun f() -> std::void::Void {
            let elem: std::string::Str
            let a = |caps elem| { }
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_lambda_capture_mut(self):
        """
        fun f() -> std::void::Void {
            let elem: std::string::Str
            let a = |caps &mut elem| { }
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_lambda_capture_ref(self):
        """
        fun f() -> std::void::Void {
            let elem: std::string::Str
            let a = |caps &elem| { }
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_let_statement(self):
        """
        fun f() -> std::void::Void {
            let elem: std::string::Str
            let a = elem
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_parenthesis(self):
        """
        fun f() -> std::void::Void {
            let elem: std::string::Str
            let a = (elem)
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_loop_condition_boolean(self):
        """
        fun f() -> std::void::Void {
            let elem: std::boolean::Bool
            loop elem { }
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_loop_condition_iterable(self):
        """
        fun f() -> std::void::Void {
            let iterator: std::generator::Gen[std::string::Str]
            loop elem in iterator { }
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_object_initializer_argument_unnamed(self):
        """
        fun f() -> std::void::Void {
            let data: std::vector::Vec[std::number::u8::U8]
            let a = std::string::Str(data)
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_object_initializer_argument_named(self):
        """
        fun f() -> std::void::Void {
            let data_vec: std::vector::Vec[std::number::u8::U8]
            let a = std::string::Str(data=data_vec)
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_pattern_guard(self):
        """
        fun f() -> std::void::Void {
            let elem: std::boolean::Bool
            case true of
                == false and elem { }
                else { }
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_postfix_expression_operator_index(self):
        """
        fun f() -> std::void::Void {
            let elem: std::vector::Vec[std::string::Str]
            let a = elem[0_uz]
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_postfix_expression_operator_member_access_attribute(self):
        """
        fun f() -> std::void::Void {
            let elem: std::string::Str
            elem.data
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_postfix_expression_operator_member_access_index(self):
        """
        fun f() -> std::void::Void {
            let elem: (std::string::Str, std::string::Str)
            elem.0
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_postfix_expression_operator_not_keyword(self):
        """
        fun f() -> std::void::Void {
            let elem: std::boolean::Bool
            elem.not
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_postfix_expression_operator_res_keyword(self):
        """
        fun f() -> std::void::Void {
            let elem: std::generator::Gen[std::string::Str, std::boolean::Bool]
            elem.res(false)
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_ret_statement(self):
        """
        fun f() -> std::string::Str {
            let elem: std::string::Str
            ret elem
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_unary_expression_operator_async(self):
        """
        fun f() -> std::void::Void {
            let elem: std::function::FunRef[(std::string::Str,), std::void::Void]
            let a = async elem("hello world")
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_postfix_expression_operator_function_call(self):
        """
        fun f() -> std::void::Void {
            let elem: std::function::FunRef[(std::string::Str,), std::void::Void]
            let a = elem("hello world")
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_uninitialized_symbol_in_tuple(self):
        """
        fun f() -> std::void::Void {
            let elem: std::string::Str
            let a = (elem,)
        }
        """
