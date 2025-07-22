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
            g[std::string::Str, std::number::U32, std::number::U64]()
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
            g[std::string::Str, std::number::U32, std::number::U64]()
        }
        """

    @should_fail_compilation(SemanticErrors.GenericArgumentIncorrectVariationError)
    def test_use_mix_instead_of_comp_generic_variadic(self):
        """
        cls A[cmp ..n: std::boolean::Bool] { }

        fun g[cmp ..n: std::boolean::Bool]() -> A[n] { ret A[n]() }

        fun f() -> std::void::Void {
            g[123, std::string::Str, std::number::U32, std::number::U64]()
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
        # Known issue => early analysis names "A[n]" as "A[n=(n)]" due to auto-wrapping arguments into the variadic
        # parameter. But if the arg itself is off a variadic parameter this should not happen.

        """
        cls A[cmp ..n: std::boolean::Bool] { }

        fun g[cmp ..n: std::boolean::Bool]() -> A[n] { ret A[n]() }

        fun f() -> std::void::Void {
            g[false, true, false]()
        }
        """

    @should_pass_compilation()
    def test_use_type_generic_variadic_properly(self):
        # Known issue => see above, but slightly different context (still double tuple wrapping errors though).

        """
        cls A[..Ts] { }

        fun g[..Ts]() -> A[Ts] { ret A[Ts]() }

        fun h[..Ts]() -> (Ts,) { ret std::tuple::Tup[Ts]() }

        fun f() -> std::void::Void {
            let mut x = h[std::boolean::Bool, std::number::U32, std::string::Str]()
            x = (false, 1_u32, "hello")
        }
        """
