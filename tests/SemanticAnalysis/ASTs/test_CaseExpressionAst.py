from tests._Utils import *


class TestCaseExpressionAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.ExpressionTypeInvalidError)
    def test_invalid_case_expression(self):
        """
        fun f() -> std::void::Void {
            case std::boolean::Bool == 1 { }
        }
        """

    @should_fail_compilation(SemanticErrors.CaseBranchMultipleDestructurePatternsError)
    def test_invalid_case_expression_multiple_destructures_on_single_branch(self):
        """
        fun f() -> std::void::Void {
            case (1, 2) of
                is (a, b), (a, 1) { }
        }
        """

    @should_fail_compilation(SemanticErrors.CaseBranchesElseBranchNotLastError)
    def test_invalid_case_expression_else_branch_not_last(self):
        """
        fun f() -> std::void::Void {
            case 1 of
                else { }
                == 2 { }
        }
        """

    @should_pass_compilation()
    def test_valid_case_expression_1(self):
        """
        fun f() -> std::void::Void {
            case 1 of
                == 1 { }
                == 2 { }
                else { }
        }
        """

    @should_pass_compilation()
    def test_valid_case_expression_2(self):
        """
        fun f() -> std::void::Void {
            case [1, 2, 3] of
                is [1, a, b] { }
                is [2, c, d] { }
        }
        """

    @should_pass_compilation()
    def test_valid_case_expression_3(self):
        """
        fun f(a: std::number::bigint::BigInt, b: std::number::bigint::BigInt) -> std::void::Void {
            let x = case a == 1 {
                "hello world"
            }
            else case b == 2 {
                "goodbye world"
            }
            else {
                "neither"
            }
        }
        """

    @should_pass_compilation()
    def test_valid_case_expression_4(self):
        """
        cls Point {
            x: std::number::bigint::BigInt
            y: std::number::bigint::BigInt
        }

        fun f(p: Point) -> std::void::Void {
            let x = case p is Point(x=10, y) {
                y
            }
            else case p is Point(x, y=10) {
                x
            }
            else {
                0
            }
        }
        """
