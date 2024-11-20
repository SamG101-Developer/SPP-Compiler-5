from unittest import TestCase

from tst._Utils import *


class TestAnnotationAst(TestCase):
    @should_fail_compilation(SemanticErrors.ExpressionTypeInvalidError)
    def test_invalid_case_expression(self):
        """
        fun f() -> std::Void {
            case std::Bool then
                == 1 { }
        }
        """

    @should_fail_compilation(SemanticErrors.CaseBranchMultipleDestructurePatternsError)
    def test_invalid_case_expression_multiple_destructures_on_single_branch(self):
        """
        fun f() -> std::Void {
            case (1, 2) then
                is (a, b), (a, 1) { }
        }
        """

    @should_fail_compilation(SemanticErrors.CaseBranchesElseBranchNotLastError)
    def test_invalid_case_expression_else_branch_not_last(self):
        """
        fun f() -> std::Void {
            case 1 then
                else { }
                == 2 { }
        }
        """

    @should_pass_compilation()
    def test_valid_case_expression(self):
        """
        fun f() -> std::Void {
            case 1 then
                == 1 { }
                == 2 { }
                else { }
        }
        """
