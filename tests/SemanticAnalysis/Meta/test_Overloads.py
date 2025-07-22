from tests._Utils import *


class TestOverloads_FreeFuncs(CustomTestCase):
    @should_fail_compilation(SemanticErrors.FunctionPrototypeConflictError)
    def test_invalid_overload_parameter_conventions_1(self):
        """
        fun f(a: &std::boolean::Bool) -> std::void::Void { }
        fun f(a: &mut std::boolean::Bool) -> std::void::Void { }
        """

    @should_fail_compilation(SemanticErrors.FunctionPrototypeConflictError)
    def test_invalid_overload_parameter_conventions_2(self):
        """
        fun f(a: &mut std::boolean::Bool) -> std::void::Void { }
        fun f(a: &std::boolean::Bool) -> std::void::Void { }
        """

    @should_pass_compilation()
    def test_valid_overload_different_return_type(self):
        """
        fun f(a: std::boolean::Bool) -> std::void::Void { }
        fun f(a: std::boolean::Bool) -> std::boolean::Bool { ret true }
        """

    @should_pass_compilation()
    def test_valid_overload_parameter_count(self):
        """
        fun f(a: std::boolean::Bool) -> std::void::Void { }
        fun f(a: std::boolean::Bool, b: std::boolean::Bool) -> std::void::Void { }
        """

    @should_pass_compilation()
    def test_valid_overload_parameter_conventions_1(self):
        """
        fun f(a: &std::boolean::Bool) -> std::void::Void { }
        fun f(a: std::boolean::Bool) -> std::void::Void { }
        """

    @should_pass_compilation()
    def test_valid_overload_parameter_conventions_2(self):
        """
        fun f(a: std::boolean::Bool) -> std::void::Void { }
        fun f(a: &std::boolean::Bool) -> std::void::Void { }
        """

    @should_pass_compilation()
    def test_valid_overload_parameter_conventions_3(self):
        """
        fun f(a: &mut std::boolean::Bool) -> std::void::Void { }
        fun f(a: std::boolean::Bool) -> std::void::Void { }
        """

    @should_pass_compilation()
    def test_valid_overload_parameter_conventions_4(self):
        """
        fun f(a: std::boolean::Bool) -> std::void::Void { }
        fun f(a: &mut std::boolean::Bool) -> std::void::Void { }
        """

    @should_pass_compilation()
    def test_valid_overload_parameter_types(self):
        """
        fun f(a: std::boolean::Bool) -> std::void::Void { }
        fun f(a: std::bignum::bigint::BigInt) -> std::void::Void { }
        """

    @should_fail_compilation(SemanticErrors.FunctionPrototypeConflictError)
    def test_invalid_overload_generics_same_name(self):
        """
        fun f[T](a: T) -> std::void::Void { }
        fun f[T](a: T) -> std::void::Void { }
        """

    @should_fail_compilation(SemanticErrors.FunctionPrototypeConflictError)
    def test_invalid_overload_generics_different_name(self):
        """
        fun f[T](a: T) -> std::void::Void { }
        fun f[U](a: U) -> std::void::Void { }
        """

    @should_pass_compilation()
    def test_valid_overload_generics_usage_1(self):
        """
        fun f[T]() -> std::void::Void { }
        fun f[T](b: T) -> std::void::Void { }
        """

    @should_pass_compilation()
    def test_valid_overload_generics_usage_2(self):
        """
        fun f[T](a: T) -> std::void::Void { }
        fun f[T](a: T, b: T) -> std::void::Void { }
        """

    @should_pass_compilation()
    def test_valid_overload_generics_usage_3(self):
        """
        fun f[T]() -> std::void::Void { }
        fun f[T, U]() -> std::void::Void { }
        """


class TestOverloads_SupBlocks(CustomTestCase):
    @should_fail_compilation(SemanticErrors.FunctionPrototypeConflictError)
    def test_invalid_overload_parameter_conventions_1(self):
        """
        cls A { }
        sup A {
            fun f(a: &std::boolean::Bool) -> std::void::Void { }
        }

        sup A {
            fun f(a: &mut std::boolean::Bool) -> std::void::Void { }
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionPrototypeConflictError)
    def test_invalid_overload_parameter_conventions_2(self):
        """
        cls A { }
        sup A {
            fun f(a: &mut std::boolean::Bool) -> std::void::Void { }
        }

        sup A {
            fun f(a: &std::boolean::Bool) -> std::void::Void { }
        }
        """

    @should_pass_compilation()
    def test_valid_overload_different_return_type(self):
        """
        cls A { }
        sup A {
            fun f(a: std::boolean::Bool) -> std::void::Void { }
        }

        sup A {
            fun f(a: std::boolean::Bool) -> std::boolean::Bool { ret true }
        }
        """

    @should_pass_compilation()
    def test_valid_overload_parameter_count(self):
        """
        cls A { }
        sup A {
            fun f(a: std::boolean::Bool) -> std::void::Void { }
        }

        sup A {
            fun f(a: std::boolean::Bool, b: std::boolean::Bool) -> std::void::Void { }
        }
        """

    @should_pass_compilation()
    def test_valid_overload_parameter_conventions_1(self):
        """
        cls A { }
        sup A {
            fun f(a: &std::boolean::Bool) -> std::void::Void { }
        }

        sup A {
            fun f(a: std::boolean::Bool) -> std::void::Void { }
        }
        """

    @should_pass_compilation()
    def test_valid_overload_parameter_conventions_2(self):
        """
        cls A { }
        sup A {
            fun f(a: std::boolean::Bool) -> std::void::Void { }
        }

        sup A {
            fun f(a: &std::boolean::Bool) -> std::void::Void { }
        }
        """

    @should_pass_compilation()
    def test_valid_overload_parameter_conventions_3(self):
        """
        cls A { }
        sup A {
            fun f(a: &mut std::boolean::Bool) -> std::void::Void { }
        }

        sup A {
            fun f(a: std::boolean::Bool) -> std::void::Void { }
        }
        """

    @should_pass_compilation()
    def test_valid_overload_parameter_conventions_4(self):
        """
        cls A { }
        sup A {
            fun f(a: std::boolean::Bool) -> std::void::Void { }
        }

        sup A {
            fun f(a: &mut std::boolean::Bool) -> std::void::Void { }
        }
        """

    @should_pass_compilation()
    def test_valid_overload_parameter_types(self):
        """
        cls A { }
        sup A {
            fun f(a: std::boolean::Bool) -> std::void::Void { }
        }

        sup A {
            fun f(a: std::bignum::bigint::BigInt) -> std::void::Void { }
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionPrototypeConflictError)
    def test_invalid_overload_generics_same_name(self):
        """
        cls A { }
        sup A {
            fun f[T](a: T) -> std::void::Void { }
        }

        sup A {
            fun f[T](a: T) -> std::void::Void { }
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionPrototypeConflictError)
    def test_invalid_overload_generics_different_name(self):
        """
        cls A { }
        sup A {
            fun f[T](a: T) -> std::void::Void { }
        }

        sup A {
            fun f[U](a: U) -> std::void::Void { }
        }
        """

    @should_pass_compilation()
    def test_valid_overload_generics_usage_1(self):
        """
        cls A { }
        sup A {
            fun f[T]() -> std::void::Void { }
        }

        sup A {
            fun f[T](b: T) -> std::void::Void { }
        }
        """

    @should_pass_compilation()
    def test_valid_overload_generics_usage_2(self):
        """
        cls A { }
        sup A {
            fun f[T](a: T) -> std::void::Void { }
        }

        sup A {
            fun f[T](a: T, b: T) -> std::void::Void { }
        }
        """

    @should_pass_compilation()
    def test_valid_overload_generics_usage_3(self):
        """
        cls A { }
        sup A {
            fun f[T]() -> std::void::Void { }
        }

        sup A {
            fun f[T, U]() -> std::void::Void { }
        }
        """
