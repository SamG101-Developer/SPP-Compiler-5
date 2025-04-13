from tests._Utils import *


class TestFunctionPrototypeAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.FunctionPrototypeConflictError)
    def test_invalid_function_prototype_conflict(self):
        """
        fun f(a: std::boolean::Bool) -> std::void::Void { }
        fun f(a: std::boolean::Bool) -> std::void::Void { }
        """

    @should_fail_compilation(SemanticErrors.FunctionPrototypeConflictError)
    def test_invalid_function_prototype_conflict_optional_parameters_no_param(self):
        """
        fun f() -> std::void::Void { }
        fun f(a: std::boolean::Bool = false) -> std::void::Void { }
        """

    @should_fail_compilation(SemanticErrors.FunctionPrototypeConflictError)
    def test_invalid_function_prototype_conflict_optional_parameters(self):
        """
        fun f(a: std::boolean::Bool) -> std::void::Void { }
        fun f(a: std::boolean::Bool, b: std::boolean::Bool = true) -> std::void::Void { }
        """

    @should_fail_compilation(SemanticErrors.FunctionPrototypeConflictError)
    def test_invalid_function_prototype_conflict_variadic_parameters(self):
        """
        fun f(a: std::boolean::Bool) -> std::void::Void { }
        fun f(a: std::boolean::Bool, ..b: std::boolean::Bool) -> std::void::Void { }
        """

    @should_fail_compilation(SemanticErrors.FunctionPrototypeConflictError)
    def test_invalid_function_prototype_conflict_different_return_type(self):
        """
        fun f(a: std::boolean::Bool) -> std::void::Void { }
        fun f(a: std::boolean::Bool) -> std::boolean::Bool { }
        """

    @should_fail_compilation(SemanticErrors.FunctionPrototypeConflictError)
    def test_invalid_function_prototype_conflict_different_param_variation_1_param(self):
        """
        fun f(a: std::boolean::Bool = false) -> std::void::Void { }
        fun f(a: std::boolean::Bool) -> std::void::Void { }
        """

    @should_fail_compilation(SemanticErrors.FunctionPrototypeConflictError)
    def test_invalid_function_prototype_conflict_different_param_variation_n_params(self):
        """
        fun f(a: std::string::Str, b: std::boolean::Bool = false) -> std::void::Void { }
        fun f(a: std::string::Str, b: std::boolean::Bool) -> std::void::Void { }
        """

    @should_fail_compilation(SemanticErrors.FunctionPrototypeConflictError)
    def test_invalid_function_prototype_conflicts_self_convention(self):
        """
        cls A { }
        sup A {
            fun f(&self, a: std::boolean::Bool) -> std::void::Void { }
            fun f(&mut self, a: std::boolean::Bool) -> std::void::Void { }
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionPrototypeConflictError)
    def test_invalid_function_prototype_conflicts_same_sup_block(self):
        """
        cls A { }
        sup A {
            fun f(&self, a: std::boolean::Bool = false) -> std::void::Void { }
            fun f(&self) -> std::void::Void { }
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionPrototypeConflictError)
    def test_invalid_function_prototype_conflicts_different_sup_blocks(self):
        """
        cls A { }
        sup A {
            fun f(&self, a: std::boolean::Bool = false) -> std::void::Void { }
        }
        sup A {
            fun f(&self) -> std::void::Void { }
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionPrototypeConflictError)
    def test_invalid_function_prototype_overload_parameter_conventions_1(self):
        """
        fun f(a: &std::boolean::Bool) -> std::void::Void { }
        fun f(a: &mut std::boolean::Bool) -> std::void::Void { }
        """

    @should_fail_compilation(SemanticErrors.FunctionPrototypeConflictError)
    def test_invalid_function_prototype_overload_parameter_conventions_2(self):
        """
        fun f(a: &mut std::boolean::Bool) -> std::void::Void { }
        fun f(a: &std::boolean::Bool) -> std::void::Void { }
        """

    @should_fail_compilation(SemanticErrors.IdentifierUnknownError)
    def test_invalid_function_prototype_self_outside_superimposition(self):
        """
        fun f(&self) -> std::void::Void { }
        """

    @should_fail_compilation(SemanticErrors.InvalidConventionLocationError)
    def test_invalid_function_prototype_convention_mut(self):
        """
        fun f() -> &mut std::void::Void { }
        """

    @should_fail_compilation(SemanticErrors.InvalidConventionLocationError)
    def test_invalid_function_prototype_convention_ref(self):
        """
        fun f() -> &std::void::Void { }
        """

    @should_fail_compilation(SemanticErrors.InvalidConventionLocationError)
    def test_invalid_function_prototype_convention_mut_from_generic_substitution(self):
        """
        @no_impl
        fun f[T]() -> T { }

        fun g() -> std::void::Void {
            let x = f[&mut std::string::Str]()
        }
        """

    @should_fail_compilation(SemanticErrors.InvalidConventionLocationError)
    def test_invalid_function_prototype_convention_ref_from_generic_substitution(self):
        """
        @no_impl
        fun f[T]() -> T { }

        fun g() -> std::void::Void {
            let x = f[&std::string::Str]()
        }
        """

    @should_pass_compilation()
    def test_valid_function_prototype_overload_parameter_count(self):
        """
        fun f(a: std::boolean::Bool) -> std::void::Void { }
        fun f(a: std::boolean::Bool, b: std::boolean::Bool) -> std::void::Void { }
        """

    @should_pass_compilation()
    def test_valid_function_prototype_overload_parameter_conventions_1(self):
        """
        fun f(a: &std::boolean::Bool) -> std::void::Void { }
        fun f(a: std::boolean::Bool) -> std::void::Void { }
        """

    @should_pass_compilation()
    def test_valid_function_prototype_overload_parameter_conventions_2(self):
        """
        fun f(a: std::boolean::Bool) -> std::void::Void { }
        fun f(a: &std::boolean::Bool) -> std::void::Void { }
        """

    @should_pass_compilation()
    def test_valid_function_prototype_overload_parameter_conventions_3(self):
        """
        fun f(a: &mut std::boolean::Bool) -> std::void::Void { }
        fun f(a: std::boolean::Bool) -> std::void::Void { }
        """

    @should_pass_compilation()
    def test_valid_function_prototype_overload_parameter_conventions_4(self):
        """
        fun f(a: std::boolean::Bool) -> std::void::Void { }
        fun f(a: &mut std::boolean::Bool) -> std::void::Void { }
        """

    @should_pass_compilation()
    def test_valid_function_prototype_overload_parameter_types(self):
        """
        fun f(a: std::boolean::Bool) -> std::void::Void { }
        fun f(a: std::number::BigInt) -> std::void::Void { }
        """

    @should_pass_compilation()
    def test_valid_generic_function_prototype(self):
        """
        fun f[T](a: T) -> std::void::Void { }
        fun f(a: std::number::BigInt) -> std::void::Void { }
        """

    @should_pass_compilation()
    def test_valid_generic_function_prototype_1(self):
        """
        fun f[T](a: T) -> std::void::Void { }
        """

    @should_pass_compilation()
    def test_valid_generic_function_prototype_2(self):
        """
        fun f[T]() -> std::void::Void { }
        """
