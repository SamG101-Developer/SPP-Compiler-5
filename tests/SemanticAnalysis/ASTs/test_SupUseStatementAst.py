from tests._Utils import *


class TestSupUseStatementAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_sup_use_statement_type_mismatch(self):
        """
        cls MyType { }
        sup MyType {
            use X = std::string::Str
        }

        fun f() -> std::void::Void {
            let x: MyType::X
            x = 123
        }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_sup_use_statement_nested(self):
        """
        cls MyType1 { }
        sup MyType1 {
            use Z = std::string::Str
        }

        cls MyType2 { }
        sup MyType2 {
            use Y = MyType1
        }

        cls MyType3 { }
        sup MyType3 {
            use X = MyType2
        }

        fun f() -> std::void::Void {
            let x: MyType3::X::Y::Z
            x = 123
        }
        """

    @should_fail_compilation(SemanticErrors.TypeMismatchError)
    def test_invalid_sup_use_statement_with_generic(self):
        """
        cls MyType[T] { }
        sup [T] MyType[T] {
            use X = T
        }

        fun f() -> std::void::Void {
            let x: MyType[std::number::bigint::BigInt]::X
            x = "hello world"
        }
        """

    @should_pass_compilation()
    def test_valid_sup_use_statement(self):
        """
        cls MyType { }
        sup MyType {
            use X = std::string::Str
        }

        fun f() -> std::void::Void {
            let x: MyType::X
            x = "hello world"
        }
        """

    @should_pass_compilation()
    def test_valid_sup_use_statement_nested(self):
        """
        cls MyType1 { }
        sup MyType1 {
            use Z = std::string::Str
        }

        cls MyType2 { }
        sup MyType2 {
            use Y = MyType1
        }

        cls MyType3 { }
        sup MyType3 {
            use X = MyType2
        }

        fun f() -> std::void::Void {
            let x: MyType3::X::Y::Z
            x = "hello world"
        }
        """

    @should_pass_compilation()
    def test_valid_sup_use_statement_with_generic(self):
        """
        cls MyType[T] { }
        sup [T] MyType[T] {
            use X = T
        }

        fun f() -> std::void::Void {
            let x: MyType[std::number::bigint::BigInt]::X
            x = 123
        }
        """
