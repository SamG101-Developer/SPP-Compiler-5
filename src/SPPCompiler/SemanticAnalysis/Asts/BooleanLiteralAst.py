from __future__ import annotations

from dataclasses import dataclass, field

from llvmlite import ir

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import AstPrinter, ast_printer_method
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypes


@dataclass(slots=True, repr=False)
class BooleanLiteralAst(Asts.Ast, Asts.Mixins.TypeInferrable):
    """
    The BooleanLiteralAst class is an AST node that represents a boolean literal. This AST can be used to represent the
    boolean literals "true" and "false".

    Example:

    .. code-block:: S++

        x = true

    The above example would be represented as a BooleanLiteralAst with the value "true". Boolean literals are always
    inferred as the "std::boolean::Bool" type.
    """

    value: Asts.TokenAst = field(default=None)
    """The token representing the boolean value."""

    def __post_init__(self) -> None:
        self.value = self.value or Asts.TokenAst.raw(token_type=SppTokenType.KwFalse)

    def __eq__(self, other: BooleanLiteralAst) -> bool:
        # Needed for cmp-generic arg checking
        return type(other) is BooleanLiteralAst and self.value.token_data == other.value.token_data

    def __hash__(self) -> int:
        return id(self)

    @staticmethod
    def from_python_literal(pos: int, value: bool) -> BooleanLiteralAst:
        """
        Convenience method to construct a BooleanLiteralAst from a Python literal. It uses Asts.TokenAst wrapping, and
        then packs the token into an Asts.BooleanLiteralAst.

        :param pos: Tbe position in the source code.
        :param value: The boolean value from Python.
        :return: The Asts.BooleanLiteralAst containing the Python literal.
        """

        # Create the internal boolean value and wrap it in a token.
        token = Asts.TokenAst.raw(pos=pos, token_type=SppTokenType.KwTrue if value else SppTokenType.KwFalse)
        return BooleanLiteralAst(pos, token)

    def to_python_literal(self) -> bool:
        """
        Converts the BooleanLiteralAst back to a Python boolean literal.

        :return: The Python boolean literal represented by this AST.
        """

        return self.value.token_type == SppTokenType.KwTrue

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        return self.value.print(printer)

    @property
    def pos_end(self) -> int:
        return self.value.pos_end

    def infer_type(self, sm: ScopeManager, **kwargs) -> Asts.TypeAst:
        """
        The inferred type of a Asts.BooleanLiteralAst will always be the "std::boolean::Bool" type.

        :param sm: The scope manager.
        :param kwargs: Additional keyword arguments.
        :return: The "std::boolean::Bool" type.
        """

        # Create the standard "std::boolean::Bool" type.
        return CommonTypes.Bool(self.pos)

    def code_gen_pass_2(self, sm: ScopeManager, llvm_module: ir.Module, **kwargs) -> ir.Constant:
        """
        Generates the LLVM IR for this boolean literal. The literal is converted to an LLVM constant of type i1. The
        true/false state depends on the value of the literal.

        :param sm: The scope manager.
        :param llvm_module: The LLVM module to generate code into.
        :param kwargs: Additional keyword arguments.
        :return: The LLVM constant representing the boolean literal.
        """

        # Create the LLVM constant for the boolean literal.
        return ir.Constant(ir.IntType(1), 1 if self.to_python_literal() else 0)


__all__ = [
    "BooleanLiteralAst"]
