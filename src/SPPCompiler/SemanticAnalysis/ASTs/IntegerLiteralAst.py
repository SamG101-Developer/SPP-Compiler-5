from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


def integer_limits(*, signed: bool, b: int) -> tuple[int, int]:
    upper = pow(2, b - 1) - 1 if signed else pow(2, b) - 1
    lower = pow(2, b - 1) if signed else 0
    return lower, upper


SIZE_MAPPING = {
    "i8": integer_limits(signed=True, b=8),
    "u8": integer_limits(signed=False, b=8),
    "i16": integer_limits(signed=True, b=16),
    "u16": integer_limits(signed=False, b=16),
    "i32": integer_limits(signed=True, b=32),
    "u32": integer_limits(signed=False, b=32),
    "i64": integer_limits(signed=True, b=64),
    "u64": integer_limits(signed=False, b=64),
    "i128": integer_limits(signed=True, b=128),
    "u128": integer_limits(signed=False, b=128),
    "i256": integer_limits(signed=True, b=256),
    "u256": integer_limits(signed=False, b=256)}


@dataclass
class IntegerLiteralAst(Ast, TypeInferrable):
    tok_sign: Optional[Asts.TokenAst] = field(default=None)
    value: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.LxNumber))
    type: Optional[Asts.TypeAst] = field(default=None)

    def __post_init__(self) -> None:
        assert self.value

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
            self.type.print(printer) if self.type else ""]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.type.pos_end if self.type else self.value.pos_end

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> Asts.TypeAst:
        # Create an integer type based on the (optional) type postfix.

        # Match the type against the allowed type postfixes (no postfix is BigInt).
        match self.type:
            case None:
                return CommonTypes.BigInt(self.pos)
            case type if type.type_parts()[0].value == "i8":
                return CommonTypes.I8(self.pos)
            case type if type.type_parts()[0].value == "u8":
                return CommonTypes.U8(self.pos)
            case type if type.type_parts()[0].value == "i16":
                return CommonTypes.I16(self.pos)
            case type if type.type_parts()[0].value == "u16":
                return CommonTypes.U16(self.pos)
            case type if type.type_parts()[0].value == "i32":
                return CommonTypes.I32(self.pos)
            case type if type.type_parts()[0].value == "u32":
                return CommonTypes.U32(self.pos)
            case type if type.type_parts()[0].value == "i64":
                return CommonTypes.I64(self.pos)
            case type if type.type_parts()[0].value == "u64":
                return CommonTypes.U64(self.pos)
            case type if type.type_parts()[0].value == "i128":
                return CommonTypes.I128(self.pos)
            case type if type.type_parts()[0].value == "u128":
                return CommonTypes.U128(self.pos)
            case type if type.type_parts()[0].value == "i256":
                return CommonTypes.I256(self.pos)
            case type if type.type_parts()[0].value == "u256":
                return CommonTypes.U256(self.pos)
            case _:
                raise

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # No analysis needs to be done for the BigInt automatically inferred type.
        if not self.type:
            return

        # Check if the value is within the bounds.
        lower, upper = SIZE_MAPPING[self.type.type_parts()[0].value]
        true_value = float(self.value.token_data)
        if not (lower <= true_value < upper):
            raise SemanticErrors.NumberOutOfBoundsError(self, lower, upper, "integer").scopes(scope_manager.current_scope)


__all__ = ["IntegerLiteralAst"]
