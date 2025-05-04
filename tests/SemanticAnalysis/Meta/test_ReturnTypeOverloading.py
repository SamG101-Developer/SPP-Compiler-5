from tests._Utils import *


class TestReturnTypeOverloading(CustomTestCase):
    @should_pass_compilation()
    def test_valid_return_type_overloading_infer_from_assignment(self):
        """
        fun g() -> std::string::Str { ret "" }
        fun g() -> std::boolean::Bool { ret false }

        fun f() -> std::void::Void {
            let mut x = "hello world"
            x = g()
        }
        """

    @should_pass_compilation()
    def test_valid_return_type_overloading_infer_from_let_statement(self):
        """
        fun g() -> std::string::Str { ret "" }
        fun g() -> std::boolean::Bool { ret false }

        fun f() -> std::void::Void {
            let x: std::boolean::Bool = g()
        }
        """

    @should_pass_compilation()
    def test_valid_return_type_overloading_infer_from_return_statement(self):
        """
        fun g() -> std::string::Str { ret "" }
        fun g() -> std::boolean::Bool { ret false }

        fun f() -> std::boolean::Bool {
            ret g()
        }
        """

    @should_pass_compilation()
    def test_valid_return_type_overloading_infer_from_gen_expression(self):
        """
        fun g() -> std::string::Str { ret "" }
        fun g() -> std::boolean::Bool { ret false }

        cor f() -> std::generator::Gen[std::boolean::Bool] {
            gen g()
        }
        """

    @should_pass_compilation()
    def test_valid_return_type_overloading_complex(self):
        """
        cls MyType { }

        cls To[Target] { }
        sup [Target] To[Target] {
            @abstract_method
            fun to(&self) -> Target {  }
        }

        sup MyType ext To[std::string::Str] {
            fun to(&self) -> std::string::Str { ret "" }
        }

        sup MyType ext To[std::boolean::Bool] {
            fun to(&self) -> std::boolean::Bool { ret false }
        }

        fun f() -> std::void::Void {
            let mut x = MyType()
            let string: std::string::Str = x.to()
            let boolean: std::boolean::Bool = x.to()
        }
        """

    @should_pass_compilation()
    def test_valid_return_type_overloading_infer_from_class_attribute(self):
        """
        cls MyType {
            a: std::boolean::Bool
        }

        fun g() -> std::string::Str { ret "" }
        fun g() -> std::boolean::Bool { ret false }

        fun f() -> std::void::Void {
            let mut x = MyType(a=g())
        }
        """

    @should_pass_compilation()
    def test_valid_return_type_overloading_infer_from_generic_class_attribute_explicit_argument(self):
        """
        cls MyType[T] {
            a: T
        }

        fun g() -> std::string::Str { ret "" }
        fun g() -> std::boolean::Bool { ret false }

        fun f() -> std::void::Void {
            let mut x = MyType[T=std::string::Str](a=g())
        }
        """

    @should_fail_compilation(SemanticErrors.FunctionCallAmbiguousSignaturesError)
    def test_invalid_return_type_overloading_infer_from_generic_class_attribute(self):
        """
        cls MyType[T] {
            a: T
        }

        fun g() -> std::string::Str { ret "" }
        fun g() -> std::boolean::Bool { ret false }

        fun f() -> std::void::Void {
            let mut x = MyType(a=g())
        }
        """

    # @should_pass_compilation()
    # def test_valid_return_type_overloading_infer_from_function_parameter(self):
    #     """
    #     fun g() -> std::string::Str { ret "" }
    #     fun g() -> std::boolean::Bool { ret false }
    #     fun h(x: std::boolean::Bool) -> std::void::Void { }
    #
    #     fun f() -> std::void::Void {
    #         h(g())
    #     }
    #     """
    #
    # @should_fail_compilation(SemanticErrors.FunctionCallAmbiguousSignaturesError)
    # def test_invalid_return_type_overloading_infer_from_function_parameter(self):
    #     """
    #     fun g() -> std::string::Str { ret "" }
    #     fun g() -> std::boolean::Bool { ret false }
    #     fun h(x: std::string::Str) -> std::void::Void { }
    #     fun h(x: std::boolean::Bool) -> std::void::Void { }
    #
    #     fun f() -> std::void::Void {
    #         h(g())
    #     }
    #     """
