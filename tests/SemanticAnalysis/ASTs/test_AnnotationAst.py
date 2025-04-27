from tests._Utils import *


class TestAnnotationAst(CustomTestCase):
    @should_pass_compilation()
    def test_valid_annotation_virtual_method(self) -> None:
        """
        cls A { }
        sup A {
            @virtual_method
            fun f() -> std::void::Void { }
        }
        """

    @should_pass_compilation()
    def test_valid_annotation_abstract_method(self) -> None:
        """
        cls A { }
        sup A {
            @abstract_method
            fun f() -> A { }
        }
        """

    @should_pass_compilation()
    def test_valid_annotation_no_impl(self) -> None:
        """
        cls A { }
        sup A {
            @no_impl
            fun f() -> A { }
        }

        @no_impl
        fun g() -> A { }
        """

    @should_pass_compilation()
    def test_valid_annotation_public(self) -> None:
        """
        @public
        cls A { }

        sup A {
            @public
            fun f() -> std::void::Void { }
        }

        @public
        fun g() -> std::void::Void { }
        """

    @should_pass_compilation()
    def test_valid_annotation_protected(self) -> None:
        """
        @protected
        cls A { }

        sup A {
            @protected
            fun f() -> std::void::Void { }
        }

        @protected
        fun g() -> std::void::Void { }
        """

    @should_pass_compilation()
    def test_valid_annotation_private(self) -> None:
        """
        @private
        cls A { }

        sup A {
            @private
            fun f() -> std::void::Void { }
        }

        @private
        fun g() -> std::void::Void { }
        """

    @should_pass_compilation()
    def test_valid_annotation_cold(self) -> None:
        """
        cls A { }

        sup A {
            @cold
            fun f() -> std::void::Void { }
        }

        @cold
        fun g() -> std::void::Void { }
        """

    @should_pass_compilation()
    def test_valid_annotation_hot(self) -> None:
        """
        cls A { }

        sup A {
            @hot
            fun f() -> std::void::Void { }
        }

        @hot
        fun g() -> std::void::Void { }
        """

    @should_fail_compilation(SemanticErrors.AnnotationInvalidLocationError)
    def test_invalid_annotation_virtual_method_outside_sup(self) -> None:
        """
        cls A { }

        @virtual_method
        fun f() -> A { }
        """

    @should_fail_compilation(SemanticErrors.AnnotationInvalidLocationError)
    def test_invalid_annotation_abstract_method_outside_sup(self) -> None:
        """
        cls A { }

        @abstract_method
        fun f() -> A { }
        """

    @should_fail_compilation(SemanticErrors.AnnotationInvalidLocationError)
    def test_invalid_annotation_virtual_method_on_non_function(self) -> None:
        """
        @virtual_method
        cls A { }
        """

    @should_fail_compilation(SemanticErrors.AnnotationInvalidLocationError)
    def test_invalid_annotation_abstract_method_on_non_function(self) -> None:
        """
        @abstract_method
        cls A { }
        """

    @should_fail_compilation(SemanticErrors.AnnotationInvalidLocationError)
    def test_invalid_annotation_no_impl_on_non_function(self) -> None:
        """
        @no_impl
        cls A { }
        """

    @should_fail_compilation(SemanticErrors.AnnotationInvalidLocationError)
    def test_invalid_annotation_cold_on_non_function(self) -> None:
        """
        @cold
        cls A { }
        """

    @should_fail_compilation(SemanticErrors.AnnotationInvalidLocationError)
    def test_invalid_annotation_hot_on_non_function(self) -> None:
        """
        @hot
        cls A { }
        """

    @should_fail_compilation(SemanticErrors.AnnotationInvalidLocationError)
    def test_invalid_annotation_access_modifier_inside_sup_ext(self) -> None:
        """
        cls A { }
        sup A {
            @public
            fun f(&self) -> A { }
        }

        cls B { }
        sup B ext A {
            @public
            fun f(&self) -> A { }
        }
        """

    @should_fail_compilation(SemanticErrors.AnnotationInvalidError)
    def test_invalid_annotation(self) -> None:
        """
        cls A { }

        @invalid
        fun f() -> A { }
        """

    @should_fail_compilation(SemanticErrors.AnnotationConflictError)
    def test_invalid_annotation_conflicting_1(self) -> None:
        """
        cls A { }

        @public
        @protected
        fun f() -> A { }
        """

    @should_fail_compilation(SemanticErrors.AnnotationConflictError)
    def test_invalid_annotation_conflicting_2(self) -> None:
        """
        cls A { }

        @protected
        @private
        fun f() -> A { }
        """

    @should_fail_compilation(SemanticErrors.AnnotationConflictError)
    def test_invalid_annotation_conflicting_3(self) -> None:
        """
        cls A { }

        @private
        @public
        fun f() -> A { }
        """

    @should_fail_compilation(SemanticErrors.AnnotationConflictError)
    def test_invalid_annotation_conflicting_4(self) -> None:
        """
        cls A { }

        @cold
        @hot
        fun f() -> A { }
        """

    @should_fail_compilation(SemanticErrors.AnnotationConflictError)
    def test_invalid_annotation_conflicting_5(self) -> None:
        """
        cls A { }

        @hot
        @cold
        fun f() -> A { }
        """

    @should_fail_compilation(SemanticErrors.AnnotationConflictError)
    def test_invalid_annotation_conflicting_6(self) -> None:
        """
        cls A { }
        sup A {
            @virtual_method
            @abstract_method
            fun f() -> A { }
        }
        """

    @should_fail_compilation(SemanticErrors.AnnotationConflictError)
    def test_invalid_annotation_conflicting_7(self) -> None:
        """
        cls A { }
        sup A {
            @abstract_method
            @virtual_method
            fun f() -> A { }
        }
        """
