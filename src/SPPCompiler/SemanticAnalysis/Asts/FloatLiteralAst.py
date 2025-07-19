from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Tuple

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors


def _signed_integer_limits(e: int, m: int) -> Tuple[int, int]:
    return 0, 0


SIZE_MAPPING = {
    "f8": _signed_integer_limits(e=4, m=3),
    "f16": _signed_integer_limits(e=5, m=10),
    "f32": _signed_integer_limits(e=8, m=23),
    "f64": _signed_integer_limits(e=11, m=52),
    "f128": _signed_integer_limits(e=14, m=113)}


@dataclass(slots=True)
class FloatLiteralAst(Asts.Ast, Asts.Mixins.TypeInferrable):
    tok_sign: Optional[Asts.TokenAst] = field(default=None)
    integer_value: Asts.TokenAst = field(default=None)
    tok_dot: Asts.TokenAst = field(default=None)
    decimal_value: Asts.TokenAst = field(default=None)
    type: Optional[Asts.TypeAst] = field(default=None)

    def __post_init__(self) -> None:
        self.integer_value = self.integer_value or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.LxNumber)
        self.tok_dot = self.tok_dot or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkDot)
        self.decimal_value = self.decimal_value or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.LxNumber)

    def __eq__(self, other: FloatLiteralAst) -> bool:
        # Needed for cmp-generic arg checking.
        return isinstance(other, FloatLiteralAst) and self.tok_sign == other.tok_sign and self.integer_value.token_data == other.integer_value.token_data and self.decimal_value.token_data == other.decimal_value.token_data

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_sign.print(printer) if self.tok_sign else "",
            self.integer_value.print(printer),
            self.tok_dot.print(printer),
            self.decimal_value.print(printer),
            ("_" + self.type.print(printer)) if self.type else ""]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.type.pos_end if self.type else self.decimal_value.pos_end

    def infer_type(self, sm: ScopeManager, **kwargs) -> Asts.TypeAst:
        # Match the type against the allowed type postfixes (no postfix is BigDec).
        match self.type:
            case None:
                return CommonTypes.BigDec(self.pos)
            case type if type.type_parts[0].value == "f8":
                return CommonTypes.F8(self.pos)
            case type if type.type_parts[0].value == "f16":
                return CommonTypes.F16(self.pos)
            case type if type.type_parts[0].value == "f32":
                return CommonTypes.F32(self.pos)
            case type if type.type_parts[0].value == "f64":
                return CommonTypes.F64(self.pos)
            case type if type.type_parts[0].value == "f128":
                return CommonTypes.F128(self.pos)
            case _:
                raise

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # No analysis needs to be done for the BigDec automatically inferred type.
        if not self.type:
            return

        # Check if the value is within the bounds.
        lower, upper = SIZE_MAPPING[self.type.type_parts[0].value]
        true_value = float(self.integer_value.token_data + "." + self.decimal_value.token_data)
        if False:  # Todo: true_value < lower or true_value > upper:
            raise SemanticErrors.NumberOutOfBoundsError().add(
                self, lower, upper, "float").scopes(sm.current_scope)


__all__ = [
    "FloatLiteralAst"]
