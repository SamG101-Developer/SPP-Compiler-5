from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Tuple

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypesPrecompiled
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors


def _unsigned_integer_limits(n: int) -> Tuple[int, int]:
    return 0, pow(2, n) - 1


def _signed_integer_limits(n: int) -> Tuple[int, int]:
    return -pow(2, n - 1), pow(2, n - 1) - 1


# todo: add usize to tests
SIZE_MAPPING = {
    "i8": _signed_integer_limits(8),
    "u8": _unsigned_integer_limits(8),
    "i16": _signed_integer_limits(16),
    "u16": _unsigned_integer_limits(16),
    "i32": _signed_integer_limits(32),
    "u32": _unsigned_integer_limits(32),
    "i64": _signed_integer_limits(64),
    "u64": _unsigned_integer_limits(64),
    "i128": _signed_integer_limits(128),
    "u128": _unsigned_integer_limits(128),
    "i256": _signed_integer_limits(256),
    "u256": _unsigned_integer_limits(256),
    "uz": _unsigned_integer_limits(64)}


@dataclass(slots=True)
class IntegerLiteralAst(Asts.Ast, Asts.Mixins.TypeInferrable):
    tok_sign: Optional[Asts.TokenAst] = field(default=None)
    value: Asts.TokenAst = field(default=None)
    type: Optional[Asts.TypeAst] = field(default=None)

    def __post_init__(self) -> None:
        assert self.value is not None

    def __eq__(self, other: IntegerLiteralAst) -> bool:
        # Check both ASTs are the same type and have the same sign, value and type.
        return isinstance(other, IntegerLiteralAst) and self.tok_sign == other.tok_sign and self.value.token_data == other.value.token_data and self.type == other.type

    @staticmethod
    def from_token(value: Asts.TokenAst, pos: int = 0) -> IntegerLiteralAst:
        return IntegerLiteralAst(pos, None, value, None)

    @staticmethod
    def from_python_literal(value: int) -> IntegerLiteralAst:
        token = Asts.TokenAst.raw(token_type=SppTokenType.LxNumber, token_metadata=str(value))
        return IntegerLiteralAst.from_token(token)

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
                return CommonTypesPrecompiled.BIGINT
            case type if type.type_parts()[0].value == "i8":
                return CommonTypesPrecompiled.I8
            case type if type.type_parts()[0].value == "u8":
                return CommonTypesPrecompiled.U8
            case type if type.type_parts()[0].value == "i16":
                return CommonTypesPrecompiled.I16
            case type if type.type_parts()[0].value == "u16":
                return CommonTypesPrecompiled.U16
            case type if type.type_parts()[0].value == "i32":
                return CommonTypesPrecompiled.I32
            case type if type.type_parts()[0].value == "u32":
                return CommonTypesPrecompiled.U32
            case type if type.type_parts()[0].value == "i64":
                return CommonTypesPrecompiled.I64
            case type if type.type_parts()[0].value == "u64":
                return CommonTypesPrecompiled.U64
            case type if type.type_parts()[0].value == "i128":
                return CommonTypesPrecompiled.I128
            case type if type.type_parts()[0].value == "u128":
                return CommonTypesPrecompiled.U128
            case type if type.type_parts()[0].value == "i256":
                return CommonTypesPrecompiled.I256
            case type if type.type_parts()[0].value == "u256":
                return CommonTypesPrecompiled.U256
            case type if type.type_parts()[0].value == "uz":
                return CommonTypesPrecompiled.USIZE
            case _:
                raise

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # No analysis needs to be done for the BigInt automatically inferred type.
        if not self.type:
            return

        # Check if the value is within the bounds.
        lower, upper = SIZE_MAPPING[self.type.type_parts()[0].value]
        true_value = int((self.tok_sign.token_data if self.tok_sign else "") + self.value.token_data)
        if true_value < lower or true_value > upper:
            raise SemanticErrors.NumberOutOfBoundsError().add(self, lower, upper, "integer").scopes(sm.current_scope)


__all__ = [
    "IntegerLiteralAst"]
