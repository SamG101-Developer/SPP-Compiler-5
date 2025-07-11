from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Optional

from llvmlite import ir

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import AstPrinter, ast_printer_method
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Utils.CompilerStages import PreProcessingContext
from SPPCompiler.Utils.Sequence import SequenceUtils


@dataclass(slots=True)
class UseStatementAst(Asts.Ast, Asts.Mixins.VisibilityEnabledAst, Asts.Mixins.TypeInferrable):
    annotations: list[Asts.AnnotationAst] = field(default_factory=list)
    kw_use: Asts.TokenAst = field(default=None)
    old_type: Asts.TypeAst = field(default=None)

    _generated: bool = field(default=False, init=False, repr=False)
    _conversion: Optional[Asts.TypeStatementAst] = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        self.kw_use = self.kw_use or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.KwUse)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            SequenceUtils.print(printer, self.annotations, sep="\n"),
            self.kw_use.print(printer) + " ",
            self.old_type.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.old_type.pos_end

    def infer_type(self, sm: ScopeManager, **kwargs) -> Asts.TypeAst:
        # All statements are inferred as "Void".
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
        self._conversion = Asts.TypeStatementAst(
            pos=self.pos,
            annotations=self.annotations,
            new_type=self.old_type.type_parts[-1].without_generics,
            old_type=self.old_type)
        self._conversion.generate_top_level_scopes(sm)

        # Mark this AST as generated, so it is not generated in the analysis phase.
        self._generated = True

    def generate_top_level_aliases(self, sm: ScopeManager, **kwargs) -> None:
        # Get the old type. This won't have generics, so is guaranteed to exist as a symbol (given its valid).
        self.old_type.analyse_semantics(sm, skip_generic_check=True, **kwargs)
        old_type_symbol = sm.current_scope.get_symbol(self.old_type, ignore_alias=True)
        generic_params = old_type_symbol.type.generic_parameter_group

        # Add the generic parameters to the conversion AST, and add mock generic arguments to the old type.
        self._conversion.generic_parameter_group = copy.copy(generic_params)
        self._conversion.old_type.type_parts[-1].generic_argument_group = Asts.GenericArgumentGroupAst.from_parameter_group(generic_params)
        self._conversion._cls_ast.generic_parameter_group = copy.copy(generic_params)

        # Generate the top-level aliases for the conversion AST.
        self._conversion.generate_top_level_aliases(sm, **kwargs)

    def qualify_types(self, sm: ScopeManager, **kwargs) -> None:
        self._conversion.qualify_types(sm, **kwargs)

    def load_super_scopes(self, sm: ScopeManager, **kwargs) -> None:
        self._conversion.load_super_scopes(sm, **kwargs)

    def pre_analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        self._conversion.pre_analyse_semantics(sm, **kwargs)

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        self._conversion.analyse_semantics(sm, **kwargs)

    def check_memory(self, sm: ScopeManager, **kwargs) -> None:
        self._conversion.check_memory(sm, **kwargs)

    def code_gen_pass_1(self, sm: ScopeManager, llvm_module: ir.Module, **kwargs) -> None:
        self._conversion.code_gen_pass_1(sm, llvm_module, **kwargs)

    def code_gen_pass_2(self, sm: ScopeManager, llvm_module: ir.Module, **kwargs) -> None:
        self._conversion.code_gen_pass_2(sm, llvm_module, **kwargs)
