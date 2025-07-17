from __future__ import annotations

import sys
from dataclasses import dataclass, field
from typing import Optional, Tuple

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import AstPrinter, ast_printer_method
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors


def _unsigned_integer_limits(n: int) -> Tuple[int, int]:
    return 0, pow(2, n) - 1


def _signed_integer_limits(n: int) -> Tuple[int, int]:
    return -pow(2, n - 1), pow(2, n - 1) - 1


SIZE_MAPPING = {
    "s8": _signed_integer_limits(8),
    "u8": _unsigned_integer_limits(8),
    "s16": _signed_integer_limits(16),
    "u16": _unsigned_integer_limits(16),
    "s32": _signed_integer_limits(32),
    "u32": _unsigned_integer_limits(32),
    "s64": _signed_integer_limits(64),
    "u64": _unsigned_integer_limits(64),
    "s128": _signed_integer_limits(128),
    "u128": _unsigned_integer_limits(128),
    "s256": _signed_integer_limits(256),
    "u256": _unsigned_integer_limits(256),
    "sz": _signed_integer_limits(sys.maxsize.bit_length() + 1),
    "uz": _unsigned_integer_limits(sys.maxsize.bit_length() + 1)}


@dataclass(slots=True)
class IntegerLiteralAst(Asts.Ast, Asts.Mixins.TypeInferrable):
    tok_sign: Optional[Asts.TokenAst] = field(default=None)
    value: Asts.TokenAst = field(default=None)
    type: Optional[Asts.TypeAst] = field(default=None)  # why TypeSingleAst? just use str metadata?

    def __hash__(self) -> int:
        return id(self)

    def __eq__(self, other: IntegerLiteralAst) -> bool:
        # Needed for cmp-generic arg checking.
        return isinstance(other, IntegerLiteralAst) and self.tok_sign == other.tok_sign and self.value.token_data == other.value.token_data

    @staticmethod
    def from_python_literal(value: int) -> IntegerLiteralAst:
        token = Asts.TokenAst.raw(token_type=SppTokenType.LxNumber, token_metadata=str(value))
        return IntegerLiteralAst(value=token)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_sign.print(printer) if self.tok_sign else "",
            self.value.print(printer),
            ("_" + self.type.print(printer)) if self.type else ""]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.type.pos_end if self.type else self.value.pos_end

    def infer_type(self, sm: ScopeManager, **kwargs) -> Asts.TypeAst:
        # Create an integer type based on the (optional) type postfix.

        # Match the type against the allowed type postfixes (no postfix is BigInt).
        match self.type:
            case None:
                return CommonTypes.BigInt(self.pos)
            case type if type.type_parts[0].value == "s8":
                return CommonTypes.S8(self.pos)
            case type if type.type_parts[0].value == "u8":
                return CommonTypes.U8(self.pos)
            case type if type.type_parts[0].value == "s16":
                return CommonTypes.S16(self.pos)
            case type if type.type_parts[0].value == "u16":
                return CommonTypes.U16(self.pos)
            case type if type.type_parts[0].value == "s32":
                return CommonTypes.S32(self.pos)
            case type if type.type_parts[0].value == "u32":
                return CommonTypes.U32(self.pos)
            case type if type.type_parts[0].value == "s64":
                return CommonTypes.S64(self.pos)
            case type if type.type_parts[0].value == "u64":
                return CommonTypes.U64(self.pos)
            case type if type.type_parts[0].value == "s128":
                return CommonTypes.S128(self.pos)
            case type if type.type_parts[0].value == "u128":
                return CommonTypes.U128(self.pos)
            case type if type.type_parts[0].value == "s256":
                return CommonTypes.S256(self.pos)
            case type if type.type_parts[0].value == "u256":
                return CommonTypes.U256(self.pos)
            case type if type.type_parts[0].value == "sz":
                return CommonTypes.SSize(self.pos)
            case type if type.type_parts[0].value == "uz":
                return CommonTypes.USize(self.pos)
            case _:
                raise ValueError(f"Invalid type for integer literal: {self.type}.")

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # No analysis needs to be done for the BigInt automatically inferred type.
        if not self.type:
            return

        # Check if the value is within the bounds.
        lower, upper = SIZE_MAPPING[self.type.type_parts[0].value]
        true_value = int((self.tok_sign.token_data if self.tok_sign else "") + self.value.token_data)
        if true_value < lower or true_value > upper:
            raise SemanticErrors.NumberOutOfBoundsError().add(self, lower, upper, "integer").scopes(sm.current_scope)


__all__ = [
    "IntegerLiteralAst"]
