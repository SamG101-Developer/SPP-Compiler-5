from tests._Utils import *


class TestArrayLiteral0ElementAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.InvalidConventionLocationError)
    def test_invalid_array_empty_array_literal_ref(self):
        """
        fun f() -> std::void::Void {
            let a = [&std::boolean::Bool, 1]
        }
        """

    @should_fail_compilation(SemanticErrors.InvalidConventionLocationError)
    def test_invalid_array_empty_array_literal_mut(self):
        """
        fun f() -> std::void::Void {
            let a = [&mut std::boolean::Bool, 1]
        }
        """

    @should_pass_compilation()
    def test_valid_array_empty_array_literal(self):
        """
        fun f() -> std::void::Void {
            let a = [std::boolean::Bool, 1]
        }
        """
