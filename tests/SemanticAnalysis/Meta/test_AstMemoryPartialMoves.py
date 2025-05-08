from tests._Utils import *


class TestAstMemoryPartialMoves(CustomTestCase):
    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_assign_attribute_on_non_initialized_variable(self):
        """
        use std::string::Str

        fun f() -> std::void::Void {
            let x: Str
            x.data = Vec[U8]()
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_assign_attribute_on_non_initialized_attribute_1(self):
        """
        use std::string::Str

        cls A { str: Str }
        cls B { a: A }

        fun f() -> std::void::Void {
            let mut b = B()
            let a = b.a
            b.a.str = "hello"
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_assign_attribute_on_non_initialized_attribute_2(self):
        """
        use std::string::Str

        cls A { str: Str }
        cls B { a: A }
        cls C { b: B }

        fun f() -> std::void::Void {
            let mut c = C()
            let b = c.b
            c.b.a.str = "hello"
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_assign_attribute_on_non_initialized_attribute_3(self):
        """
        use std::string::Str

        cls A { str: Str }
        cls B { a: A }
        cls C { b: B }

        fun f() -> std::void::Void {
            let mut c = C()
            let b = c.b.a
            c.b.a.str = "hello"
        }
        """

    @should_pass_compilation()
    def test_assign_attribute_on_non_initialized_attribute_4(self):
        """
        use std::string::Str

        cls A { str: Str }
        cls B { a: A }
        cls C { b: B }

        fun f() -> std::void::Void {
            let mut c = C()
            let x = c.b.a.str
            c.b.a.str = "hello"
        }
        """
