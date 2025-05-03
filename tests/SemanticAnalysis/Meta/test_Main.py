from tests._Utils import *


class TestMain(CustomTestCase):
    @should_pass_compilation(no_main=True)
    def test_valid_main(self) -> None:
        """
        fun main(args: std::vector::Vec[std::string::Str]) -> std::void::Void { }
        """

    @should_pass_compilation(no_main=True)
    def test_valid_main_different_return_type(self) -> None:
        """
        fun main(args: std::vector::Vec[std::string::Str]) -> std::number::bigint::BigInt { ret 0 }
        """

    @should_pass_compilation(no_main=True)
    def test_valid_main_aliased_types(self) -> None:
        """
        use std::vector::Vec
        use std::string::Str
        use std::void::Void
        fun main(args: Vec[Str]) -> Void { }
        """

    @should_fail_compilation(SemanticErrors.MissingMainFunction, no_main=True)
    def test_invalid_main_missing(self) -> None:
        """
        """

    @should_fail_compilation(SemanticErrors.MissingMainFunction, no_main=True)
    def test_invalid_main_no_argument(self) -> None:
        """
        fun main() -> std::void::Void { }
        """

    @should_fail_compilation(SemanticErrors.MissingMainFunction, no_main=True)
    def test_invalid_main_argument_type_mismatch(self) -> None:
        """
        fun main(args: std::vector::Vec[std::number::bigint::BigInt]) -> std::void::Void { }
        """
