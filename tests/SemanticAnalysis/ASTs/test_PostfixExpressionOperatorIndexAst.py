from tests._Utils import *


class TestPostfixExpressionIndexAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.IdentifierUnknownError)
    def test_invalid_postfix_indexing_non_indexable(self):
        """
        fun f(p: std::number::bigint::BigInt) -> std::void::Void {
            p[0]
        }
        """

    @should_fail_compilation(SemanticErrors.IdentifierUnknownError)
    def test_invalid_postfix_immutable_index_for_mut_only_indexable(self):
        """
        cls A {
            a: std::string::Str
            b: std::string::Str
        }

        sup A ext std::ops::index::IndexMut[std::string::Str, std::number::usize::USize] {
            cor index_mut(&mut self, index: std::number::usize::USize) -> std::generator::GenOnce[&mut std::string::Str] {
                case index of
                    == 0_uz { gen &mut self.a }
                    == 1_uz { gen &mut self.b }
            }
        }

        fun f(p: A) -> std::void::Void {
            let mut x = p[0_uz]
            x = 123
        }
        """

    @should_fail_compilation(SemanticErrors.IdentifierUnknownError)
    def test_invalid_postfix_mutable_index_for_ref_only_indexable(self):
        """
        cls A {
            a: std::string::Str
            b: std::string::Str
        }

        sup A ext std::ops::index::IndexRef[std::string::Str, std::number::usize::USize] {
            cor index_ref(&self, index: std::number::usize::USize) -> std::generator::GenOnce[&std::string::Str] {
                case index of
                    == 0_uz { gen &self.a }
                    == 1_uz { gen &self.b }
            }
        }

        fun f(p: A) -> std::void::Void {
            let mut x = p[mut 0_uz]
            x = 123
        }
        """

    @should_pass_compilation()
    def test_valid_postfix_indexing_ref(self):
        """
        fun f(p: std::vector::Vec[std::string::Str], y: &std::string::Str) -> std::void::Void {
            let mut x = p[0_uz]
            # x = y
        }
        """

    @should_pass_compilation()
    def test_valid_postfix_indexing_mut(self):
        """
        fun f(mut p: std::vector::Vec[std::string::Str], y: &mut std::string::Str) -> std::void::Void {
            let mut x = p[mut 0_uz]
            # x = y
        }
        """
