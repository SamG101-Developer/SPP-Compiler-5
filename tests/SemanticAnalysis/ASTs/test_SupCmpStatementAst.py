from tests._Utils import *


class TestSupCmpStatementAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_sup_cmp_statement_type_mismatch(self):
        """
        cls MyType { }
        sup MyType {
            cmp n: std::number::usize::USize = 123
        }

        fun f() -> std::void::Void {
            let mut local_n = MyType::n
            local_n = "hello world"
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryMovedWhilstPinnedError)
    def test_invalid_sup_cmp_statement_moving_non_copy_cmp(self):
        """
        cls MyType { }
        sup MyType {
            cmp n: std::string::Str = "hello world"
        }

        fun f() -> std::void::Void {
            let mut local_n = MyType::n
            local_n = "hello world"
        }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_sup_use_statement_with_generic(self):
        """
        cls MyType[T, cmp m: T] { }
        sup [T, cmp m: T] MyType[T, m] {
            cmp n: T = m
        }

        fun f() -> std::void::Void {
            let mut x = MyType[std::number::usize::USize, 123_uz]::n
            x = "hello world"
        }
        """

    @should_pass_compilation()
    def test_valid_sup_use_statement(self):
        """
        cls MyType { }
        sup MyType {
            cmp n: std::number::usize::USize = 123_uz
        }

        fun f() -> std::void::Void {
            let mut local_n = MyType::n
            local_n = 456_uz
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryMovedWhilstPinnedError)
    def test_invalid_sup_use_statement_with_generic_move(self):
        """
        cls MyType[T, cmp m: T] { }
        sup [T, cmp m: T] MyType[T, m] {
            cmp n: T = m
        }

        fun f() -> std::void::Void {
            let mut x = MyType[std::number::bigint::BigInt, 123]::n
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryMovedWhilstPinnedError)
    def test_invalid_sup_use_statement_with_generic_copy(self):
        # This fails because T isn't constrained to be a copy type (USize just happens to be).
        """
        cls MyType[T, cmp m: T] { }
        sup [T, cmp m: T] MyType[T, m] {
            cmp n: T = m
        }

        fun f() -> std::void::Void {
        }
        """
