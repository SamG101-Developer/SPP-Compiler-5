from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING
import functools

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Meta.TypeInferrable import TypeInferrable, InferredType
from SPPCompiler.SemanticAnalysis.MultiStage.Stage4_SemanticAnalyser import Stage4_SemanticAnalyser
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst


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
    "u256": integer_limits(signed=False, b=256)
}


@dataclass
class IntegerLiteralAst(Ast, TypeInferrable, Stage4_SemanticAnalyser):
    tok_sign: Optional[TokenAst]
    value: TokenAst
    type: Optional[TypeAst]

    def __post_init__(self) -> None:
        # Import the necessary classes to create default instances.
        from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst

        # Convert the name to a TypeAst.
        self.type = TypeAst.from_identifier(self.type) if self.type else None

    def __eq__(self, other: IntegerLiteralAst) -> bool:
        # Check both ASTs are the same type and have the same sign, value and type.
        return isinstance(other, IntegerLiteralAst) and self.tok_sign == other.tok_sign and int(self.value.token.token_metadata) == int(other.value.token.token_metadata) and self.type == other.type

    @staticmethod
    def from_token(value: TokenAst, pos: int = -1) -> IntegerLiteralAst:
        return IntegerLiteralAst(pos, None, value, None)

    @staticmethod
    def from_python_literal(value: int) -> IntegerLiteralAst:
        from SPPCompiler.LexicalAnalysis.Token import Token, TokenType
        token = TokenAst(-1, Token(str(value), TokenType.CmDecInteger))
        return IntegerLiteralAst.from_token(token)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_sign.print(printer) if self.tok_sign else "",
            self.value.print(printer),
            self.type.print(printer) if self.type else ""]
        return " ".join(string)

    @functools.cache
    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredType:
        # Create an integer type based on the (optional) type postfix.
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes

        # Match the type against the allowed type postfixes (no postfix is BigInt).
        match self.type:
            case None: float_type = CommonTypes.BigInt(self.pos)
            case type if type.types[-1].value == "i8": CommonTypes.F8(self.pos)
            case type if type.types[-1].value == "u8": CommonTypes.F8(self.pos)
            case type if type.types[-1].value == "i16": CommonTypes.F16(self.pos)
            case type if type.types[-1].value == "u16": CommonTypes.F16(self.pos)
            case type if type.types[-1].value == "i32": CommonTypes.F32(self.pos)
            case type if type.types[-1].value == "u32": CommonTypes.F32(self.pos)
            case type if type.types[-1].value == "i64": CommonTypes.F64(self.pos)
            case type if type.types[-1].value == "u64": CommonTypes.F64(self.pos)
            case type if type.types[-1].value == "i128": CommonTypes.F128(self.pos)
            case type if type.types[-1].value == "u128": CommonTypes.F128(self.pos)
            case type if type.types[-1].value == "i256": CommonTypes.F256(self.pos)
            case type if type.types[-1].value == "u256": CommonTypes.F256(self.pos)

        return InferredType.from_type(float_type)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        from SPPCompiler.SemanticAnalysis.Meta.AstErrors import AstErrors

        # No analysis needs to be done for the BigInt automatically inferred type.
        if self.type.types[-1].value == "BigDec":
            return

        # Check if the value is within the bounds.
        lower, upper = SIZE_MAPPING[self.type.types[-1].value]
        if not (lower <= float(self.value.token.token_metadata) <= upper):
            raise AstErrors.NUMBER_OUT_OF_RANGE(self, lower, upper, "integer")


__all__ = ["IntegerLiteralAst"]
