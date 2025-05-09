from tests._Utils import *


class TestLetStatementUninitializedAst(CustomTestCase):
    @should_pass_compilation()
    def test_valid_single_identifier(self):
        """
        fun f() -> std::void::Void {
            let x: std::boolean::Bool
            x = true
        }
        """

    @should_pass_compilation()
    def test_valid_tuple(self):
        """
        fun f() -> std::void::Void {
            let (x, y): (std::boolean::Bool, std::number::bigint::BigInt)
            x = true
            y = 123
        }
        """

    @should_pass_compilation()
    def test_valid_array(self):
        """
        fun f() -> std::void::Void {
            let [x, y]: [std::boolean::Bool, 2]
            x = true
            y = true
        }
        """

    @should_pass_compilation()
    def test_valid_object(self):
        """
        cls Point {
            x: std::number::bigint::BigInt
            y: std::number::bigint::BigInt
        }

        fun f() -> std::void::Void {
            let Point(x, y): Point
            x = 5
            y = 6
        }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_single_identifier_type_mismatch(self):
        """
        fun f() -> std::void::Void {
            let x: std::boolean::Bool
            x = 123
        }
        """

    @should_fail_compilation(SemanticErrors.VariableTupleDestructureTupleSizeMismatchError)
    def test_invalid_tuple_length_too_big(self):
        """
        fun f() -> std::void::Void {
            let (x, y): (std::boolean::Bool, std::number::bigint::BigInt, std::number::bigint::BigInt)
        }
        """

    @should_fail_compilation(SemanticErrors.VariableTupleDestructureTupleSizeMismatchError)
    def test_invalid_tuple_length_too_small(self):
        """
        fun f() -> std::void::Void {
            let (x, y): (std::boolean::Bool,)
        }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def invalid_tuple_element_type_mismatch(self):
        """
        fun f() -> std::void::Void {
            let (x, y): (std::boolean::Bool, std::number::bigint::BigInt)
            x = "hello world"
        }
        """

    @should_fail_compilation(SemanticErrors.VariableArrayDestructureArraySizeMismatchError)
    def test_invalid_array_length_too_big(self):
        """
        fun f() -> std::void::Void {
            let [x, y]: [std::boolean::Bool, 3]
        }
        """

    @should_fail_compilation(SemanticErrors.VariableArrayDestructureArraySizeMismatchError)
    def test_invalid_array_length_too_small(self):
        """
        fun f() -> std::void::Void {
            let [x, y]: [std::boolean::Bool, 1]
        }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_array_element_type_mismatch(self):
        """
        fun f() -> std::void::Void {
            let [x, y]: [std::boolean::Bool, 2]
            x = "hello world"
        }
        """

    @should_fail_compilation(SemanticErrors.IdentifierUnknownError)
    def test_invalid_object_type_attribute(self):
        """
        cls Point {
            x: std::number::bigint::BigInt
            y: std::number::bigint::BigInt
        }

        fun f() -> std::void::Void {
            let Point(z): Point
        }
        """

    @should_fail_compilation(SemanticErrors.ArgumentRequiredNameMissingError)
    def test_invalid_object_type_missing_attributes(self):
        """
        cls Point {
            x: std::number::bigint::BigInt
            y: std::number::bigint::BigInt
        }

        fun f() -> std::void::Void {
            let Point(x): Point
        }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_object_type_mismatch(self):
        """
        cls Point {
            x: std::number::bigint::BigInt
            y: std::number::bigint::BigInt
        }

        fun f() -> std::void::Void {
            let Point(x, y): Point
            x = "hello world"
        }
        """
