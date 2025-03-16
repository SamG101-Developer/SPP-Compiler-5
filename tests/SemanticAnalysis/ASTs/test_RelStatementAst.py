from unittest import TestCase

from tests._Utils import *


class TestRelStatementAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.MemoryPinTargetInvalidError)
    def test_invalid_pin_statement_non_symbolic_target(self):
        """
        fun f() -> std::void::Void {
            rel 5
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryReleasingNonPinnedSymbolError)
    def test_invalid_rel_statement_non_pinned_target_1(self):
        """
        cls Point {
            x: std::number::BigInt
            y: std::number::BigInt
        }

        fun f(p: Point) -> std::void::Void {
            pin p
            rel p.x
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryReleasingNonPinnedSymbolError)
    def test_invalid_rel_statement_non_pinned_target_2(self):
        """
        cls Point {
            x: std::number::BigInt
            y: std::number::BigInt
        }

        fun f(p: Point) -> std::void::Void {
            pin p.x
            rel p
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryReleasingConstantSymbolError)
    def test_invalid_rel_statement_constant_target(self):
        """
        cmp p: Point = Point(x=5, y=5)

        cls Point {
            x: std::number::BigInt
            y: std::number::BigInt
        }

        fun f() -> std::void::Void {
            rel p
        }
        """

    @should_pass_compilation()
    def test_valid_rel_statement(self):
        """
        cls Point {
            x: std::number::BigInt
            y: std::number::BigInt
        }

        fun f(p: Point) -> std::void::Void {
            pin p.x
            pin p.y
            rel p.x
            rel p.y
        }
        """

    @should_pass_compilation()
    def test_valid_rel_statement_multiple(self):
        """
        cls Point {
            x: std::number::BigInt
            y: std::number::BigInt
        }

        fun f(p: Point) -> std::void::Void {
            pin p.x, p.y
            rel p.x, p.y
        }
        """
