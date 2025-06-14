from tests._Utils import *


class TestAstGenericArgsWrongClasses(CustomTestCase):
    @should_fail_compilation(SemanticErrors.GenericArgumentIncorrectVariationError)
    def test_use_comp_instead_of_type_generic(self):
        """
        cls A[T] { }

        fun g[T]() -> A[T] { ret A[T]() }

        fun f() -> std::void::Void {
            g[123]()
        }
        """

    @should_fail_compilation(SemanticErrors.GenericArgumentIncorrectVariationError)
    def test_use_comp_instead_of_type_generic_variadic(self):
        """
        cls A[..T] { }

        fun g[..T]() -> A[T] { ret A[T]() }

        fun f() -> std::void::Void {
            g[123, 456, 789]()
        }
        """

    @should_fail_compilation(SemanticErrors.GenericArgumentIncorrectVariationError)
    def test_use_mix_instead_of_type_generic_variadic(self):
        """
        cls A[..T] { }

        fun g[..T]() -> A[T] { ret A[T]() }

        fun f() -> std::void::Void {
            g[std::string::Str, 123, 456, 789]()
        }
        """

    @should_pass_compilation()
    def test_use_type_generic_properly(self):
        """
        cls A[T] { }

        fun g[T]() -> A[T] { ret A[T]() }

        fun f() -> std::void::Void {
            g[std::string::Str]()
        }
        """

    @should_pass_compilation()
    def test_use_type_generic_variadic_properly(self):
        """
        cls A[..T] { }

        fun g[..T]() -> A[T] { ret A[T]() }

        fun f() -> std::void::Void {
            g[std::string::Str, std::number::u32::U32, std::number::u64::U64]()
        }
        """

    @should_fail_compilation(SemanticErrors.GenericArgumentIncorrectVariationError)
    def test_use_type_instead_of_comp_generic(self):
        """
        cls A[cmp n: std::boolean::Bool] { }

        fun g[cmp n: std::boolean::Bool]() -> A[n] { ret A[n]() }

        fun f() -> std::void::Void {
            g[std::string::Str]()
        }
        """

    @should_fail_compilation(SemanticErrors.GenericArgumentIncorrectVariationError)
    def test_use_type_instead_of_comp_generic_variadic(self):
        """
        cls A[cmp ..n: std::boolean::Bool] { }

        fun g[cmp ..n: std::boolean::Bool]() -> A[n] { ret A[n]() }

        fun f() -> std::void::Void {
            g[std::string::Str, std::number::u32::U32, std::number::u64::U64]()
        }
        """

    @should_fail_compilation(SemanticErrors.GenericArgumentIncorrectVariationError)
    def test_use_mix_instead_of_comp_generic_variadic(self):
        """
        cls A[cmp ..n: std::boolean::Bool] { }

        fun g[cmp ..n: std::boolean::Bool]() -> A[n] { ret A[n]() }

        fun f() -> std::void::Void {
            g[123, std::string::Str, std::number::u32::U32, std::number::u64::U64]()
        }
        """

    @should_pass_compilation()
    def test_use_comp_generic_properly(self):
        """
        cls A[cmp n: std::boolean::Bool] { }

        fun g[cmp n: std::boolean::Bool]() -> A[n] { ret A[n]() }

        fun f() -> std::void::Void {
            g[false]()
        }
        """

    @should_pass_compilation()
    def test_use_comp_generic_variadic_properly(self):
        """
        cls A[cmp ..n: std::boolean::Bool] { }

        fun g[cmp ..n: std::boolean::Bool]() -> A[n] { ret A[n]() }

        fun f() -> std::void::Void {
            g[false, true, false]()
        }
        """
