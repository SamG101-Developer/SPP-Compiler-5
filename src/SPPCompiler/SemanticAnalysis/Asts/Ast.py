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
    """!
    The Ast class is the base class of all ASTs created by the parser. Common methods and properties are defined here.
    The "CompilerStages" class is inherited to allow the AST to be processed by the compiler.
    """

    pos: int = field(default=0)

    _ctx: PreProcessingContext = field(default=None, kw_only=True, repr=False)
    _scope: Optional[Scope] = field(default=None, kw_only=True, repr=False)

    @ast_printer_method
    @abstractmethod
    def print(self, printer: AstPrinter) -> str:
        """!
        Print an AST with indentation for inner scopes. The decorator and AstPrinter object "printer" work together to
        auto-format the output.
        @param printer The auto-formatting AstPrinter object.
        @return The output string to be printed.
        """

    @property
    @abstractmethod
    def pos_end(self) -> int:
        return 0

    def __eq__(self, other: Ast) -> bool:
        return isinstance(other, Ast)

    def __str__(self) -> str:
        printer = AstPrinter()
        return self.print(printer)

    def pre_process(self, ctx: PreProcessingContext) -> None:
        """!
        The default AST steps for pre-processing is to save the context into an attribute. This is used in later
        analysis stages.
        @param context The pre-processing context.
        """

        self._ctx = ctx

    def generate_top_level_scopes(self, sm: ScopeManager) -> None:
        """!
        The default AST steps for generating top level scopes is to save the scope into an attribute. This is used in
        later analysis stages.
        @param sm The scope manager.
        """

        self._scope = sm.current_scope


__all__ = [
    "Ast"]
