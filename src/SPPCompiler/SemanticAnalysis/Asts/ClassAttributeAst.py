from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstMemoryUtils import AstMemoryUtils
from SPPCompiler.SemanticAnalysis.AstUtils.AstTypeUtils import AstTypeUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Scoping.Symbols import VariableSymbol
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import AstPrinter, ast_printer_method
from SPPCompiler.SemanticAnalysis.Utils.CompilerStages import PreProcessingContext
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors
from SPPCompiler.Utils.FastDeepcopy import fast_deepcopy
from SPPCompiler.Utils.Sequence import SequenceUtils


@dataclass(slots=True, repr=False)
class ClassAttributeAst(Asts.Ast, Asts.Mixins.VisibilityEnabledAst):
    annotations: list[Asts.AnnotationAst] = field(default_factory=list)
    name: Asts.IdentifierAst = field(default=None)
    tok_colon: Asts.TokenAst = field(default=None)
    type: Asts.TypeAst = field(default=None)
    default: Optional[Asts.ExpressionAst] = None

    def __post_init__(self) -> None:
        self.tok_colon = self.tok_colon or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkColon)

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
        if c := self.type.convention:
            raise SemanticErrors.InvalidConventionLocationError().add(
                c, self.type, "attribute type").scopes(sm.current_scope)

        # Create a variable symbol for this attribute in the current scope (class).
        symbol = VariableSymbol(name=self.name, type=self.type, visibility=self._visibility[0])
        sm.current_scope.add_symbol(symbol)

    def load_super_scopes(self, sm: ScopeManager, **kwargs) -> None:
        self.type.analyse_semantics(sm, **kwargs)

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # Analyse the semantics of the annotations and the type of the attribute.
        for a in self.annotations:
            a.analyse_semantics(sm, **kwargs)

        # Repeat the check here for generic substitution attribute types.
        if c := self.type.convention:
            raise SemanticErrors.InvalidConventionLocationError().add(
                c, self.type, "attribute type").scopes(sm.current_scope)

        try:
            self.type.analyse_semantics(sm, **kwargs)
        except SemanticErrors.IdentifierUnknownError:
            # TODO: This is for generic substitutions. what needs to happen is the generic class's scope (ie Vec[T=U],
            #  where U is generic) needs to made a child of the "current_scope", to access generics from that scope,
            #  like U as a "fun f[U]()" generic, then post attribute analysis, the parent scope can be set back to what
            #  is should have been. The issue (again) is that the type being analysed will mess up because the scope
            #  search order will be broken. The best cause of action is to probably temporarily add the generic symbols
            #  in? Again though, say for the Type[T, U], if a U from the current scope is added, then is messes this up
            #  AGAIN. So I'm not really sure right now, aside from actually storing symbols in the generics AST, and
            #  then using .value as a property accessor to the mapped symbol maybe?
            pass
            
        # If a default value is present, analyse it and check its type.
        # Todo: prevent generic attributes from having defaults + test
        if self.default is not None:
            self.default.analyse_semantics(sm, **kwargs)
            default_type = self.default.infer_type(sm, **kwargs)

            if not AstTypeUtils.symbolic_eq(self.type, default_type, sm.current_scope, sm.current_scope):
                raise SemanticErrors.TypeMismatchError().add(
                    self, self.type, self.default, default_type).scopes(sm.current_scope)

    def check_memory(self, sm: ScopeManager, **kwargs) -> None:
        """
        Check the default value, if given, is memory-enforced. The unique case where this is applicable is if it is
        referring to a comptime constant. This ensures that the constant superimposes the "Copy" type.

        :param sm: The scope manager.
        :param kwargs: Additional keyword arguments.
        """

        # Check the default's memory state (cmp value, so no need to iterate deeper).
        if self.default is not None:
            AstMemoryUtils.enforce_memory_integrity(
                self.default, self.default, sm, check_move=True, check_partial_move=True,
                check_move_from_borrowed_ctx=True, check_pins=True, check_pins_linked=True, **kwargs)


__all__ = [
    "ClassAttributeAst"]
