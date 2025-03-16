from unittest import TestCase

from tests._Utils import *


class TestPinStatementAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.MemoryPinTargetInvalidError)
    def test_invalid_pin_statement_non_symbolic_target(self):
        """
        fun f() -> std::void::Void {
            pin 5
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryPinOverlapError)
    def test_invalid_pin_statement_overlap_1(self):
        """
        cls Point {
            x: std::number::BigInt
            y: std::number::BigInt
        }

        fun f(p: Point) -> std::void::Void {
            pin p.x
            pin p
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryPinOverlapError)
    def test_invalid_pin_statement_overlap_2(self):
        """
        cls Point {
            x: std::number::BigInt
            y: std::number::BigInt
        }

        fun f(p: Point) -> std::void::Void {
            pin p
            pin p.x
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryPinOverlapError)
    def test_invalid_pin_statement_overlap_3(self):
        """
        cls Point {
            x: std::number::BigInt
            y: std::number::BigInt
        }

        fun f(p: Point) -> std::void::Void {
            pin p.x
            pin p.x
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryPinOverlapError)
    def test_invalid_pin_statement_overlap_4(self):
        """
        cls Point {
            x: std::number::BigInt
            y: std::number::BigInt
        }

        fun f(p: Point) -> std::void::Void {
            pin p
            pin p
        }
        """

    @should_pass_compilation()
    def test_valid_pin_statement(self):
        """
        cls Point {
            x: std::number::BigInt
            y: std::number::BigInt
        }

        fun f(p: Point) -> std::void::Void {
            pin p.x
            pin p.y
        }
        """

    @should_pass_compilation()
    def test_valid_pin_statement_multiple(self):
        """
        cls Point {
            x: std::number::BigInt
            y: std::number::BigInt
        }

        fun f(p: Point) -> std::void::Void {
            pin p.x, p.y
        }
        """
