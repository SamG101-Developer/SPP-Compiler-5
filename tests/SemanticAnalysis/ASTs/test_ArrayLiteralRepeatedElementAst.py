from tests._Utils import *


class TestArrayLiteralRepeatedElementAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.InvalidConventionLocationError)
    def test_invalid_array_ref_borrow(self):
        """
        fun f(a: &std::boolean::Bool) -> std::void::Void {
            let b = [a; 1_uz]
        }
        """

    @should_fail_compilation(SemanticErrors.InvalidConventionLocationError)
    def test_invalid_array_mut_borrow(self):
        """
        fun f(a: &mut std::boolean::Bool) -> std::void::Void {
            let b = [a; 1_uz]
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_non_copyable_element(self):
        """
        fun f() -> std::void::Void {
            let a = ["hello"; 1_uz]
        }
        """

    @should_fail_compilation(SemanticErrors.CompileTimeConstantError)
    def test_non_cmp_value(self):
        """
        fun f() -> std::void::Void {
            let b = 100_u32
            let a = [1_u32; b]
        }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_wrong_size_type(self):
        """
        fun f() -> std::void::Void {
            let a = [false; 1]
        }
        """

    @should_pass_compilation()
    def test_valid_array(self):
        """
        fun f() -> std::void::Void {
            let a = [false; 1_uz]
        }
        """

    @should_pass_compilation()
    def test_valid_array_cmp_size(self):
        """
        use std::number::USize
        fun f[cmp n: USize]() -> std::void::Void {
            let a = [false; n]
        }
        """
