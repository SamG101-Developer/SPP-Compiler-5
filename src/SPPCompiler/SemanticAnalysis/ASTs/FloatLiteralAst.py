from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable, InferredTypeInfo
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


def float_limits(*, e: int, m: int) -> tuple[int, int]:
    b = pow(2, e) - 1
    upper = (1 + (1 - pow(2, -m))) * pow(2, pow(2, e - 1 - b - 1))
    lower = -upper
    return lower, upper


SIZE_MAPPING = {
    "f8": float_limits(e=4, m=3),
    "f16": float_limits(e=5, m=10),
    "f32": float_limits(e=8, m=23),
    "f64": float_limits(e=11, m=52),
    "f128": float_limits(e=14, m=113),
    "f256": float_limits(e=18, m=237)}


@dataclass
class FloatLiteralAst(Ast, TypeInferrable):
    tok_sign: Optional[Asts.TokenAst] = field(default=None)
    integer_value: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.LxDecInteger))
    tok_dot: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.TkDot))
    decimal_value: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.LxDecInteger))
    type: Optional[Asts.TypeAst] = field(default=None)

    def __eq__(self, other: FloatLiteralAst) -> bool:
        # Check both ASTs are the same type and have the same sign, value and type.
        return all([
            isinstance(other, FloatLiteralAst),
            self.tok_sign == other.tok_sign,
            self.integer_value.token.token_metadata == other.integer_value.token.token_metadata,
            self.decimal_value.token.token_metadata == other.decimal_value.token.token_metadata,
            self.type == other.type])

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_sign.print(printer) if self.tok_sign else "",
            self.integer_value.print(printer),
            self.tok_dot.print(printer),
            self.decimal_value.print(printer),
            self.type.print(printer) if self.type else ""]
        return "".join(string)

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredTypeInfo:
        # Match the type against the allowed type postfixes (no postfix is BigDec).
        match self.type:
            case None:
                return InferredTypeInfo(CommonTypes.BigDec(self.pos))
            case type if type.types[-1].value == "f8":
                return InferredTypeInfo(CommonTypes.F8(self.pos))
            case type if type.types[-1].value == "f16":
                return InferredTypeInfo(CommonTypes.F16(self.pos))
            case type if type.types[-1].value == "f32":
                return InferredTypeInfo(CommonTypes.F32(self.pos))
            case type if type.types[-1].value == "f64":
                return InferredTypeInfo(CommonTypes.F64(self.pos))
            case type if type.types[-1].value == "f128":
                return InferredTypeInfo(CommonTypes.F128(self.pos))
            case type if type.types[-1].value == "f256":
                return InferredTypeInfo(CommonTypes.F256(self.pos))
            case _:
                raise

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # No analysis needs to be done for the BigDec automatically inferred type.
        if not self.type:
            return

        # Check if the value is within the bounds.
        lower, upper = SIZE_MAPPING[self.type.types[-1].value]
        true_value = float(self.integer_value.token.token_metadata + "." + self.decimal_value.token.token_metadata)
        if not (lower <= true_value < upper):
            raise SemanticErrors.NumberOutOfBoundsError(self, lower, upper, "float")


__all__ = ["FloatLiteralAst"]
