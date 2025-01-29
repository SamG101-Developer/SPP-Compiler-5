from __future__ import annotations

from dataclasses import dataclass, field

import std

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable, InferredType
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class RelStatementAst(Ast, TypeInferrable, CompilerStages):
    tok_rel: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.KwRel))
    expressions: Seq[Asts.ExpressionAst] = field(default_factory=Seq)

    @ast_printer_method
    @std.override_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_rel.print(printer) + " ",
            self.expressions.print(printer, ", ")]
        return "".join(string)

    @std.override_method
    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredType:
        # All statements are inferred as "void".
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
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
            raise SemanticErrors.MemoryPinTargetInvalidError().add(self, non_symbolic_pin_target, False)

        # Prevent overlapping symbols from being created.
        symbols.remove_none()
        for rel_target, symbol in self.expressions.zip(symbols):
            pins = symbol.memory_info.ast_pinned

            # Check for a direct match in the pin list.
            if not pins.find(lambda pin: str(rel_target) == str(pin)):
                raise SemanticErrors.MemoryReleasingNonPinnedSymbolError().add(self, rel_target)

            # Check the rel target isn't a compile-time constant.
            if symbol.memory_info.ast_comptime_const:
                raise SemanticErrors.MemoryReleasingConstantSymbolError().add(self, rel_target, symbol.memory_info.ast_initialization)

            # Cause a pinned generator/future to be invalidated.
            for pin_target in symbol.memory_info.pin_target:
                pin_ast = scope_manager.current_scope.get_symbol(pin_target)
                pin_ast.memory_info.moved_by(self)

            # Remove the pin.
            symbol.memory_info.ast_pinned.remove(rel_target)


__all__ = ["RelStatementAst"]
