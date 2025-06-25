from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import AstPrinter, ast_printer_method


@dataclass(slots=True)
class IterPatternExceptionAst(Asts.Ast):
    """
    Represents an iteration pattern that matches an exception, represented by "!<identifier>". This is for when
    generators are allowed to yield errors, for the GenRes type.
    """

    tk_exclamation: Asts.TokenAst = field(default=None)
    """The exclamation token representing the exception pattern."""

    variable: Asts.LocalVariableAst = field(default=None)
    """The local variable that the exception is bound to."""

    _new_ast: Asts.LetStatementInitializedAst = field(default=None, init=False)
    """The AST node that this pattern is transformed into, to create its variable (bound exception)."""

    def __post_init__(self) -> None:
        """Post-initialization to default the AST nodes."""
        self.tk_exclamation = self.tk_exclamation or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkExclamationMark)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        return f"{self.tk_exclamation.print(printer)}{self.variable.print(printer)}"

    def __str__(self) -> str:
        return f"{self.tk_exclamation}{self.variable}"

    @property
    def pos_end(self) -> int:
        return self.variable.pos_end

    def analyse_semantics(self, sm: ScopeManager, cond: Asts.ExpressionAst = None, **kwargs) -> None:
        # Create a dummy type with the same type as the variable's type, to initialize it (hacky).
        dummy_type = cond.infer_type(sm, **kwargs).type_parts[-1].generic_argument_group["Err"].value
        dummy = Asts.ObjectInitializerAst(class_type=dummy_type)

        # Create a new AST node that initializes the variable with the dummy value.
        self._new_ast = Asts.LetStatementInitializedAst(self.pos, assign_to=self.variable, value=dummy)
        self._new_ast.analyse_semantics(sm, **kwargs)

    def check_memory(self, sm: ScopeManager, **kwargs) -> None:
        self._new_ast.check_memory(sm, **kwargs)


__all__ = ["IterPatternExceptionAst"]
