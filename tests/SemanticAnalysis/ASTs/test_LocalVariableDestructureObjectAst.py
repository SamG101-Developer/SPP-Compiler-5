from tests._Utils import *


class TestLocalVariableDestructureObjectAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_convention_of_target_object_ref(self):
        """
        use std::bignum::bigint::BigInt

        cls Point {
            x: BigInt
            y: BigInt
        }

        fun f(p: &Point) -> std::void::Void {
            let Point(x, y) = p
        }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_convention_of_target_object_mut(self):
        """
        use std::bignum::bigint::BigInt

        cls Point {
            x: BigInt
            y: BigInt
        }

        fun f(p: &mut Point) -> std::void::Void {
            let Point(x, y) = p
        }
        """

    @should_fail_compilation(SemanticErrors.VariableDestructureContainsMultipleMultiSkipsError)
    def test_invalid_local_variable_destructure_object_multiple_multi_skip(self):
        """
        cls Point {
            x: std::bignum::bigint::BigInt
            y: std::bignum::bigint::BigInt
        }

        fun f(p: Point) -> std::void::Void {
            let Point(.., ..) = p
        }
        """

    @should_fail_compilation(SemanticErrors.VariableObjectDestructureWithBoundMultiSkipError)
    def test_invalid_local_variable_destructure_object_bound_multi_skip(self):
        """
        cls Point {
            x: std::bignum::bigint::BigInt
            y: std::bignum::bigint::BigInt
        }

        fun f(p: Point) -> std::void::Void {
            let Point(..mut x) = p
        }
        """

    @should_fail_compilation(SemanticErrors.ArgumentRequiredNameMissingError)
    def test_invalid_local_variable_destructure_object_missing_attribute(self):
        """
        cls Point {
            x: std::bignum::bigint::BigInt
            y: std::bignum::bigint::BigInt
        }

        fun f(p: Point) -> std::void::Void {
            let Point(x) = p
        }
        """

    @should_fail_compilation(SemanticErrors.IdentifierUnknownError)
    def test_invalid_local_variable_destructure_object_invalid_attribute(self):
        """
        cls Point {
            x: std::bignum::bigint::BigInt
            y: std::bignum::bigint::BigInt
        }

        fun f(p: Point) -> std::void::Void {
            let Point(x, y, z) = p
        }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_local_variable_destructure_object_variant_type_1(self):
        """
        fun f(o: std::option::Opt[std::string::Str]) -> std::void::Void {
            let std::result::Pass(val) = o
        }
        """

    @should_pass_compilation()
    def test_valid_local_variable_destructure_object(self):
        """
        cls Point {
            x: std::bignum::bigint::BigInt
            y: std::bignum::bigint::BigInt
        }

        fun f(p: Point) -> std::void::Void {
            let Point(x, y) = p
        }
        """

    @should_pass_compilation()
    def test_valid_local_variable_destructure_object_skip_1(self):
        """
        cls Point {
            x: std::bignum::bigint::BigInt
            y: std::bignum::bigint::BigInt
        }

        fun f(p: Point) -> std::void::Void {
            let Point(x, ..) = p
        }
        """

    @should_pass_compilation()
    def test_valid_local_variable_destructure_object_skip_2(self):
        """
        cls Point {
            x: std::bignum::bigint::BigInt
            y: std::bignum::bigint::BigInt
        }

        fun f(p: Point) -> std::void::Void {
            let Point(.., y) = p
        }
        """

    @should_pass_compilation()
    def test_valid_local_variable_destructure_object_skip_3(self):
        """
        cls Point {
            x: std::bignum::bigint::BigInt
            y: std::bignum::bigint::BigInt
        }

        fun f(p: Point) -> std::void::Void {
            let Point(..) = p
        }
        """

    @should_pass_compilation()
    def test_valid_local_variable_destructure_object_nested_object(self):
        """
        cls Point {
            x: std::bignum::bigint::BigInt
            y: std::bignum::bigint::BigInt
        }

        cls Line {
            start: Point
            end: Point
        }

        fun f(l: Line) -> std::void::Void {
            let Line(start=Point(x, y), ..) = l
        }
        """

    @should_fail_compilation(SemanticErrors.IdentifierUnknownError)
    def test_invalid_local_variable_destructure_object_check_symbols_introduced(self):
        """
        cls Point {
            x: std::bignum::bigint::BigInt
            y: std::bignum::bigint::BigInt
        }

        cls Line {
            start: Point
            end: Point
        }

        fun f(l: Line) -> std::void::Void {
            let Line(start=Point(x, y), ..) = l
            let t = start
        }
        """

    @should_pass_compilation()
    def test_valid_local_variable_destructure_check_symbols_introduced(self):
        """
        cls Point {
            x: std::bignum::bigint::BigInt
            y: std::bignum::bigint::BigInt
        }

        cls Line {
            start: Point
            end: Point
        }

        fun f(l: Line) -> std::void::Void {
            let Line(start=Point(x, y), ..) = l
            let mut t = 100
            t = y
        }
        """

    @should_pass_compilation()
    def test_valid_local_variable_destructure_object_nested_tuple(self):
        """
        cls TestType {
            a: (std::boolean::Bool, std::bignum::bigint::BigInt)
        }

        fun f(t: TestType) -> std::void::Void {
            let TestType(a=(b, mut other_variable)) = t
            other_variable = 2
        }
        """

    @should_pass_compilation()
    def test_valid_local_variable_destructure_object_nested_array(self):
        """
        cls TestType {
            a: std::array::Arr[std::boolean::Bool, 2_uz]
        }

        fun f(t: TestType) -> std::void::Void {
            let TestType(a=[b, mut other_variable]) = t
            other_variable = true
        }
        """
