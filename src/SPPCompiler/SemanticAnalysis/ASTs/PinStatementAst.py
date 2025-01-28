from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
import std

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstMemory import AstMemoryHandler
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable, InferredType
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages
from SPPCompiler.Utils.Sequence import Seq
import SPPCompiler.SemanticAnalysis as Asts

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class PinStatementAst(Ast, TypeInferrable, CompilerStages):
    tok_pin: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.KwPin))
    expressions: Seq[Asts.ExpressionAst] = field(default_factory=Seq)

    @ast_printer_method
    @std.override_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_pin.print(printer) + " ",
            self.expressions.print(printer, ", ")]
        return "".join(string)

    @std.override_method
    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredType:
        # All statements are inferred as "void".
        void_type = CommonTypes.Void(self.pos)
        return InferredType.from_type(void_type)

    @std.override_method
    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # Analyse the expressions.
        for e in self.expressions:
            e.analyse_semantics(scope_manager, **kwargs)

        # Check each expression is symbolic.
        symbols = self.expressions.map(scope_manager.current_scope.get_variable_symbol_outermost_part)
        if symbols.filter_out_none().length < self.expressions.length:
            non_symbolic_pin_target = self.expressions[symbols.index(None)]
            raise SemanticErrors.MemoryPinTargetInvalidError().add(self, non_symbolic_pin_target, True)

        # Prevent overlapping symbols from being created.
        symbols.remove_none()
        for pin_target, symbol in self.expressions.zip(symbols):
            if overlap := symbol.memory_info.ast_pinned.filter(lambda p: AstMemoryHandler.overlaps(p, pin_target)):
                raise SemanticErrors.MemoryPinOverlapError().add(pin_target, overlap[0])
            symbol.memory_info.ast_pinned.append(pin_target)


__all__ = ["PinStatementAst"]
