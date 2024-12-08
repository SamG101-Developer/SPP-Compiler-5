from unittest import TestCase

from tst._Utils import *


class TestRelStatementAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.MemoryPinTargetInvalidError)
    def test_invalid_pin_statement_non_symbolic_target(self):
        """
        fun f() -> std::Void {
            rel 5
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryReleasingNonPinnedSymbolError)
    def test_invalid_rel_statement_non_pinned_target_1(self):
        """
        cls Point {
            x: std::BigInt
            y: std::BigInt
        }

        fun f(p: Point) -> std::Void {
            pin p
            rel p.x
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryReleasingNonPinnedSymbolError)
    def test_invalid_rel_statement_non_pinned_target_2(self):
        """
        cls Point {
            x: std::BigInt
            y: std::BigInt
        }

        fun f(p: Point) -> std::Void {
            pin p.x
            rel p
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryReleasingConstantSymbolError)
    def test_invalid_rel_statement_constant_target(self):
        """
        cmp p: Point = Point(x=5, y=5)

        cls Point {
            x: std::BigInt
            y: std::BigInt
        }

        fun f() -> std::Void {
            rel p
        }
        """

    @should_pass_compilation()
    def test_valid_rel_statement(self):
        """
        cls Point {
            x: std::BigInt
            y: std::BigInt
        }

        fun f(p: Point) -> std::Void {
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
            x: std::BigInt
            y: std::BigInt
        }

        fun f(p: Point) -> std::Void {
            pin p.x, p.y
            rel p.x, p.y
        }
        """
