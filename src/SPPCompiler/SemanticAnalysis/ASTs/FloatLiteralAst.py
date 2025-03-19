from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Tuple

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


def _signed_integer_limits(e: int, m: int) -> Tuple[int, int]:
    return 0, 0


SIZE_MAPPING = {
    "f8": _signed_integer_limits(e=4, m=3),
    "f16": _signed_integer_limits(e=5, m=10),
    "f32": _signed_integer_limits(e=8, m=23),
    "f64": _signed_integer_limits(e=11, m=52),
    "f128": _signed_integer_limits(e=14, m=113),
    "f256": _signed_integer_limits(e=18, m=237)}


@dataclass
class FloatLiteralAst(Ast, TypeInferrable):
    tok_sign: Optional[Asts.TokenAst] = field(default=None)
    integer_value: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.LxNumber))
    tok_dot: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.TkDot))
    decimal_value: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.LxNumber))
    type: Optional[Asts.TypeAst] = field(default=None)

    def __eq__(self, other: FloatLiteralAst) -> bool:
        # Check both ASTs are the same type and have the same sign, value and type.
        return all([
            isinstance(other, FloatLiteralAst),
            self.tok_sign == other.tok_sign,
            self.integer_value.token_data == other.integer_value.token_data,
            self.decimal_value.token_data == other.decimal_value.token_data,
            self.type == other.type])

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

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> Asts.TypeAst:
        # Match the type against the allowed type postfixes (no postfix is BigDec).
        match self.type:
            case None:
                return CommonTypes.BigDec(self.pos)
            case type if type.type_parts()[0].value == "f8":
                return CommonTypes.F8(self.pos)
            case type if type.type_parts()[0].value == "f16":
                return CommonTypes.F16(self.pos)
            case type if type.type_parts()[0].value == "f32":
                return CommonTypes.F32(self.pos)
            case type if type.type_parts()[0].value == "f64":
                return CommonTypes.F64(self.pos)
            case type if type.type_parts()[0].value == "f128":
                return CommonTypes.F128(self.pos)
            case type if type.type_parts()[0].value == "f256":
                return CommonTypes.F256(self.pos)
            case _:
                raise

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # No analysis needs to be done for the BigDec automatically inferred type.
        if not self.type:
            return

        # Check if the value is within the bounds.
        lower, upper = SIZE_MAPPING[self.type.type_parts()[0].value]
        true_value = float(self.integer_value.token_data + "." + self.decimal_value.token_data)
        if False:  # Todo: true_value < lower or true_value > upper:
            raise SemanticErrors.NumberOutOfBoundsError().add(self, lower, upper, "float").scopes(scope_manager.current_scope)


__all__ = ["FloatLiteralAst"]
