from tests._Utils import *


class TestFunctionParameterGroupAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.IdentifierDuplicationError)
    def test_invalid_function_parameter_group_duplicate_parameter_name(self):
        """
        fun f(a: std::bignum::bigint::BigInt, b: std::bignum::bigint::BigInt, a: std::bignum::bigint::BigInt) -> std::void::Void { }
        """

    @should_fail_compilation(SemanticErrors.OrderInvalidError)
    def test_invalid_function_parameter_group_order_invalid_req_self(self):
        """
        cls A { }
        sup A {
            fun f(a: std::bignum::bigint::BigInt, self) -> std::void::Void { }
        }
        """

    @should_fail_compilation(SemanticErrors.OrderInvalidError)
    def test_invalid_function_parameter_group_order_invalid_opt_self(self):
        """
        cls A { }
        sup A {
            fun f(a: std::bignum::bigint::BigInt = 0, self) -> std::void::Void { }
        }
        """

    @should_fail_compilation(SemanticErrors.OrderInvalidError)
    def test_invalid_function_parameter_group_order_invalid_var_self(self):
        """
        cls A { }
        sup A {
            fun f(..a: std::bignum::bigint::BigInt, self) -> std::void::Void { }
        }
        """

    @should_fail_compilation(SemanticErrors.OrderInvalidError)
    def test_invalid_function_parameter_group_order_invalid_opt_req(self):
        """
        fun f(a: std::bignum::bigint::BigInt = 0, b: std::bignum::bigint::BigInt) -> std::void::Void { }
        """

    @should_fail_compilation(SemanticErrors.OrderInvalidError)
    def test_invalid_function_parameter_group_order_invalid_var_req(self):
        """
        fun f(..a: std::bignum::bigint::BigInt, b: std::bignum::bigint::BigInt) -> std::void::Void { }
        """

    @should_fail_compilation(SemanticErrors.OrderInvalidError)
    def test_invalid_function_parameter_group_order_invalid_var_opt(self):
        """
        fun f(..a: std::bignum::bigint::BigInt, b: std::bignum::bigint::BigInt = 0) -> std::void::Void { }
        """

    @should_fail_compilation(SemanticErrors.ParameterMultipleSelfError)
    def test_invalid_function_parameter_group_multiple_self(self):
        """
        cls A { }
        sup A {
            fun f(self, &mut self) -> std::void::Void { }
        }
        """

    @should_fail_compilation(SemanticErrors.ParameterMultipleVariadicError)
    def test_invalid_function_parameter_group_multiple_variadic(self):
        """
        fun f(..a: std::bignum::bigint::BigInt, ..b: std::bignum::bigint::BigInt) -> std::void::Void { }
        """

    @should_pass_compilation()
    def test_valid_function_parameter_group_empty(self):
        """
        fun f() -> std::void::Void { }
        """

    @should_pass_compilation()
    def test_valid_function_parameter_group_self(self):
        """
        cls A { }
        sup A {
            fun f(self) -> std::void::Void { }
        }
        """

    @should_pass_compilation()
    def test_valid_function_parameter_group_req(self):
        """
        fun f(a: std::bignum::bigint::BigInt) -> std::void::Void { }
        """

    @should_pass_compilation()
    def test_valid_function_parameter_group_opt(self):
        """
        fun f(a: std::bignum::bigint::BigInt = 0) -> std::void::Void { }
        """

    @should_pass_compilation()
    def test_valid_function_parameter_group_var(self):
        """
        fun f(..a: std::bignum::bigint::BigInt) -> std::void::Void { }
        """

    @should_pass_compilation()
    def test_valid_function_parameter_group_req_opt(self):
        """
        fun f(a: std::bignum::bigint::BigInt, b: std::bignum::bigint::BigInt = 0) -> std::void::Void { }
        """

    @should_pass_compilation()
    def test_valid_function_parameter_group_req_var(self):
        """
        fun f(a: std::bignum::bigint::BigInt, ..b: std::bignum::bigint::BigInt) -> std::void::Void { }
        """

    @should_pass_compilation()
    def test_valid_function_parameter_group_opt_var(self):
        """
        fun f(a: std::bignum::bigint::BigInt = 0, ..b: std::bignum::bigint::BigInt) -> std::void::Void { }
        """

    @should_pass_compilation()
    def test_valid_function_parameter_group_self_req(self):
        """
        cls A { }
        sup A {
            fun f(self, a: std::bignum::bigint::BigInt) -> std::void::Void { }
        }
        """

    @should_pass_compilation()
    def test_valid_function_parameter_group_self_opt(self):
        """
        cls A { }
        sup A {
            fun f(self, a: std::bignum::bigint::BigInt = 0) -> std::void::Void { }
        }
        """

    @should_pass_compilation()
    def test_valid_function_parameter_group_self_var(self):
        """
        cls A { }
        sup A {
            fun f(self, ..a: std::bignum::bigint::BigInt) -> std::void::Void { }
        }
        """
