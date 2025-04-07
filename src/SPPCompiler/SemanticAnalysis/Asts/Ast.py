from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import *
from SPPCompiler.SemanticAnalysis.Utils.CompilerStages import CompilerStages, PreProcessingContext

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class Ast(ABC, CompilerStages):
    """
    The Ast class is the base class of all ASTs created by the parser. Common methods and properties are defined here.
    The "CompilerStages" class is inherited to allow the AST to be processed by the compiler.
    """

    pos: int = field(default=0)
    """The position of the AST (by character in source code)."""

    _ctx: PreProcessingContext = field(default=None, kw_only=True, repr=False)
    """The preprocessing context for this AST (only used in top-level ASTs)"""

    _scope: Optional[Scope] = field(default=None, kw_only=True, repr=False)
    """The scope representing top-level ASTs (function/class scopes)"""

    @ast_printer_method
    @abstractmethod
    def print(self, printer: AstPrinter) -> str:
        """
        Print an AST with indentation for inner scopes. The decorator and AstPrinter object "printer" work together to
        auto-format the output.

        :param printer: The auto-formatting AstPrinter object.
        :return: The output string to be printed.
        """

    @property
    @abstractmethod
    def pos_end(self) -> int:
        """
        The `pos_end` property gets the final index spanned to by this AST. Implementations recursively choose the final
        AST from their attributes and get that AST's end position. This will end up with either an identifier of token's
        end position, and for either AST this is its start position + length of identifier/token.

        :return: The final index spanned by this AST.
        """
        return 0

    def __eq__(self, other: Ast) -> bool:
        return isinstance(other, Ast)

    def __str__(self) -> str:
        printer = AstPrinter()
        return self.print(printer)

    def pre_process(self, ctx: PreProcessingContext) -> None:
        """
        The default AST steps for pre-processing is to save the context into an attribute. This is used in later
        analysis stages.

        :param ctx: The pre-processing context.
        :return: None.
        """

        self._ctx = ctx

    def generate_top_level_scopes(self, sm: ScopeManager) -> None:
        """
        The default AST steps for generating top level scopes is to save the scope into an attribute. This is used in
        later analysis stages.

        :param sm: The scope manager.
        :return: None.
        """

        self._scope = sm.current_scope


__all__ = [
    "Ast"]
