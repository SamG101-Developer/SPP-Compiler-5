from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable, InferredType
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst
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
    "f256": float_limits(e=18, m=237)
}


@dataclass
class FloatLiteralAst(Ast, TypeInferrable, CompilerStages):
    tok_sign: Optional[TokenAst]
    integer_value: TokenAst
    tok_dot: TokenAst
    decimal_value: TokenAst
    type: Optional[TypeAst]

    def __post_init__(self) -> None:
        # Import the necessary classes to create default instances.
        from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes

        # Convert the name to a TypeAst.
        match self.type:
            case None: self.type = CommonTypes.BigDec()
            case _: self.type = TypeAst.from_identifier(self.type)

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

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredType:
        # Create a float type based on the (optional) type postfix.
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes

        # Match the type against the allowed type postfixes (no postfix is BigDec).
        match self.type:
            case None: float_type = CommonTypes.BigDec(self.pos)
            case type if type.types[-1].value == "f8": float_type = CommonTypes.F8(self.pos)
            case type if type.types[-1].value == "f16": float_type = CommonTypes.F16(self.pos)
            case type if type.types[-1].value == "f32": float_type = CommonTypes.F32(self.pos)
            case type if type.types[-1].value == "f64": float_type = CommonTypes.F64(self.pos)
            case type if type.types[-1].value == "f128": float_type = CommonTypes.F128(self.pos)
            case type if type.types[-1].value == "f256": float_type = CommonTypes.F256(self.pos)
            case _:
                raise

        return InferredType.from_type(float_type)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors

        # No analysis needs to be done for the BigDec automatically inferred type.
        if not self.type:
            return

        # Check if the value is within the bounds.
        lower, upper = SIZE_MAPPING[self.type.types[-1].value]
        if not (lower <= float(self.integer_value.token.token_metadata + "." + self.decimal_value.token.token_metadata) <= upper):
            raise SemanticErrors.NumberOutOfBoundsError(self, lower, upper, "float")


__all__ = ["FloatLiteralAst"]
