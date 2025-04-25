from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Optional

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import AstPrinter, ast_printer_method
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Utils.CompilerStages import PreProcessingContext
from SPPCompiler.Utils.Sequence import Seq


@dataclass(slots=True)
class UseStatementReduxAst(Asts.Ast, Asts.Mixins.VisibilityEnabledAst, Asts.Mixins.TypeInferrable):
    annotations: Seq[Asts.AnnotationAst] = field(default_factory=Seq)
    kw_use: Asts.TokenAst = field(default=None)
    old_type: Asts.TypeAst = field(default=None)

    _generated: bool = field(default=False, init=False, repr=False)
    _conversion: Optional[Asts.UseStatementAliasAst] = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        self.kw_use = self.kw_use or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.KwUse)
        assert self.old_type is not None

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.annotations.print(printer, " "),
            self.kw_use.print(printer) + " ",
            self.old_type.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.old_type.pos_end

    def infer_type(self, sm: ScopeManager, **kwargs) -> Asts.TypeAst:
        return CommonTypes.Void(self.pos)

    def pre_process(self, ctx: PreProcessingContext) -> None:
        # Pre-process the annotations.
        Asts.Ast.pre_process(self, ctx)
        for a in self.annotations:
            a.pre_process(self)

    def generate_top_level_scopes(self, sm: ScopeManager) -> None:
        # Run top level scope logic for the annotations.
        for a in self.annotations:
            a.generate_top_level_scopes(sm)

        # Create the conversion AST: "use std::vector::Vec[T]" becomes "use Vec[T] = std::vector::Vec[T]"
        self._conversion = Asts.UseStatementAliasAst(
            pos=self.pos,
            annotations=self.annotations,
            new_type=Asts.TypeSingleAst.from_generic_identifier(self.old_type.type_parts()[-1].without_generics()),
            old_type=self.old_type)
        self._conversion.generate_top_level_scopes(sm)

        # Mark this AST as generated, so it is not generated in the analysis phase.
        self._generated = True

    def generate_top_level_aliases(self, sm: ScopeManager, **kwargs) -> None:
        old_type_symbol = sm.current_scope.get_symbol(self.old_type, ignore_alias=True)
        generic_params = old_type_symbol.type.generic_parameter_group
        self._conversion.generic_parameter_group = copy.copy(generic_params)
        self._conversion._cls_ast.generic_parameter_group = copy.copy(generic_params)
        self._conversion.old_type.type_parts()[-1].generic_argument_group = Asts.GenericArgumentGroupAst.from_parameter_group(generic_params.parameters)

        plain_old_sym = sm.current_scope.get_symbol(self.old_type.without_generics()).generic_impl
        self._conversion.generate_top_level_aliases(sm, old_sym=plain_old_sym, **kwargs)

    def qualify_types(self, sm: ScopeManager, **kwargs) -> None:
        plain_old_sym = sm.current_scope.get_symbol(self.old_type.without_generics()).generic_impl
        self._conversion.qualify_types(sm, old_sym=plain_old_sym, **kwargs)

    def load_super_scopes(self, sm: ScopeManager, **kwargs) -> None:
        self._conversion.load_super_scopes(sm, **kwargs)

    def pre_analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        self._conversion.pre_analyse_semantics(sm, **kwargs)

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        self._conversion.analyse_semantics(sm, **kwargs)
