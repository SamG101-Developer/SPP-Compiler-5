from unittest import TestCase

from tst._Utils import *


class TestFunctionPrototypeAst(TestCase):
    @should_fail_compilation(SemanticErrors.FunctionPrototypeConflictError)
    def test_invalid_function_prototype_conflict(self):
        """
        fun f(a: std::Bool) -> std::Void { }
        fun f(a: std::Bool) -> std::Void { }
        """

    @should_fail_compilation(SemanticErrors.FunctionPrototypeConflictError)
    def test_invalid_function_prototype_conflict_optional_parameters(self):
        """
        fun f(a: std::Bool) -> std::Void { }
        fun f(a: std::Bool, b: std::Bool = true) -> std::Void { }
        """

    @should_fail_compilation(SemanticErrors.FunctionPrototypeConflictError)
    def test_invalid_function_prototype_conflict_variadic_parameters(self):
        """
        fun f(a: std::Bool) -> std::Void { }
        fun f(a: std::Bool, ..b: std::Bool) -> std::Void { }
        """

    @should_fail_compilation(SemanticErrors.FunctionPrototypeConflictError)
    def test_invalid_function_prototype_conflict_different_return_type(self):
        """
        fun f(a: std::Bool) -> std::Void { }
        fun f(a: std::Bool) -> std::Bool { }
        """

    @should_fail_compilation(SemanticErrors.FunctionPrototypeConflictError)
    def test_invalid_function_prototype_conflicts_self_convention(self):
        """
        cls A { }
        sup A {
            fun f(&self, a: std::Bool) -> std::Void { }
            fun f(&mut self, a: std::Bool) -> std::Void { }
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionPrototypeConflictError)
    def test_invalid_function_prototype_conflicts_same_sup_block(self):
        """
        cls A { }
        sup A {
            fun f(&self, a: std::Bool = false) -> std::Void { }
            fun f(&mut self, a: std::Bool) -> std::Void { }
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionPrototypeConflictError)
    def test_invalid_function_prototype_conflicts_different_sup_blocks(self):
        """
        cls A { }
        sup A {
            fun f(&self, a: std::Bool = false) -> std::Void { }
        }
        sup A {
            fun f(&mut self, a: std::Bool) -> std::Void { }
        }
        """

    @should_pass_compilation()
    def test_valid_function_prototype_overload_parameter_count(self):
        """
        fun f(a: std::Bool) -> std::Void { }
        fun f(a: std::Bool, b: std::Bool) -> std::Void { }
        """

    @should_pass_compilation()
    def test_valid_function_prototype_overload_parameter_conventions(self):
        """
        fun f(a: &std::Bool) -> std::Void { }
        fun f(a: &mut std::Bool) -> std::Void { }
        """

    @should_pass_compilation()
    def test_valid_function_prototype_overload_parameter_types(self):
        """
        fun f(a: std::Bool) -> std::Void { }
        fun f(a: std::BigInt) -> std::Void { }
        """
