from tests._Utils import *


class TestIdentifierAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.IdentifierUnknownError)
    def test_invalid_identifier(self):
        """
        fun f() -> std::void::Void {
            let mut x = y
            x = z
        }
        """

    @should_pass_compilation()
    def test_valid_identifier(self):
        """
        fun f() -> std::void::Void {
            let mut x = 1
            let y = 2
            x = y
        }
        """
