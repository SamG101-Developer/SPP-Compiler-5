from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Scoping.Symbols import VariableSymbol
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypesPrecompiled
from SPPCompiler.SemanticAnalysis.Utils.CompilerStages import PreProcessingContext
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors
from SPPCompiler.Utils.FastDeepcopy import fast_deepcopy
from SPPCompiler.Utils.Sequence import Seq, SequenceUtils


@dataclass(slots=True)
class ClassAttributeAst(Asts.Ast, Asts.Mixins.VisibilityEnabledAst):
    annotations: Seq[Asts.AnnotationAst] = field(default_factory=Seq)
    name: Asts.IdentifierAst = field(default=None)
    tok_colon: Asts.TokenAst = field(default=None)
    type: Asts.TypeAst = field(default=None)
    default: Optional[Asts.ExpressionAst] = None

    def __post_init__(self) -> None:
        self.tok_colon = self.tok_colon or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkColon)
        assert self.name is not None and self.type is not None

    def __deepcopy__(self, memodict: Dict = None) -> ClassAttributeAst:
        return ClassAttributeAst(
            self.pos, self.annotations, fast_deepcopy(self.name), self.tok_colon,
            fast_deepcopy(self.type), _visibility=self._visibility, _ctx=self._ctx, _scope=self._scope)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            SequenceUtils.print(printer, self.annotations, sep="\n"),
            self.name.print(printer),
            self.tok_colon.print(printer) + " ",
            self.type.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.type.pos_end

    def pre_process(self, ctx: PreProcessingContext) -> None:
        Asts.Ast.pre_process(self, ctx)

        # Pre-process the annotations of this attribute.
        for a in self.annotations:
            a.pre_process(self)

    def generate_top_level_scopes(self, sm: ScopeManager) -> None:
        # Run top level scope logic for the annotations.
        for a in self.annotations:
            a.generate_top_level_scopes(sm)

        # Ensure the attribute type does not have a convention.
        if c := self.type.get_convention():
            raise SemanticErrors.InvalidConventionLocationError().add(
                c, self.type, "attribute type").scopes(sm.current_scope)

        # Create a variable symbol for this attribute in the current scope (class).
        symbol = VariableSymbol(name=self.name, type=self.type, visibility=self._visibility[0])
        sm.current_scope.add_symbol(symbol)

    def load_super_scopes(self, sm: ScopeManager, **kwargs) -> None:
        self.type.analyse_semantics(sm, **kwargs)

        # Ensure the attribute type is not void.
        # Todo: Check the order of comparison (variants).
        if self.type.symbolic_eq(CommonTypesPrecompiled.VOID, sm.current_scope, sm.current_scope):
            raise SemanticErrors.TypeVoidInvalidUsageError().add(
                self.type).scopes(sm.current_scope)

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # Analyse the semantics of the annotations and the type of the attribute.
        for a in self.annotations:
            a.analyse_semantics(sm, **kwargs)

        # Repeat the check here for generic substitution attribute types.
        if c := self.type.get_convention():
            raise SemanticErrors.InvalidConventionLocationError().add(
                c, self.type, "attribute type").scopes(sm.current_scope)
            
        # If a default value is present, analyse it and check its type.
        if self.default:
            self.default.analyse_semantics(sm, **kwargs)
            default_type = self.default.infer_type(sm)

            if not self.type.symbolic_eq(default_type, sm.current_scope, sm.current_scope):
                raise SemanticErrors.TypeMismatchError().add(
                    self, self.type, self.default, default_type).scopes(sm.current_scope)


__all__ = [
    "ClassAttributeAst"]
