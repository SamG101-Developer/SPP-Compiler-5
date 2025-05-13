from tests._Utils import *


class TestAstMemoryPartialMoves(CustomTestCase):
    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_invalid_assign_attribute_to_non_initialized_value(self):
        # Cannot take an attribute off of a non-initialized variable.
        """
        use std::string::Str
        use std::number::u8::U8
        use std::vector::Vec

        fun f() -> std::void::Void {
            let mut x: Str
            x.data = Vec[U8]()
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_invalid_assign_to_non_initialized_attribute(self):
        # Cannot place a value into the attribute of a non-initialized attribute.
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
    def test_invalid_assign_to_non_initialized_attributes_attribute(self):
        # Cannot place a value into the attribute of a non-initialized attribute's attribute.
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
    def test_invalid_assign_to_non_initialized_attributes_attribute_deep(self):
        # Cannot place a value into the attribute of a non-initialized attribute's attribute (deeper).
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
    def test_valid_assign_attribute_on_non_initialized_attribute_4(self):
        # Can place a value into a non-initialized attribute, as a direct replacement.
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
