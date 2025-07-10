from __future__ import annotations

import copy
import itertools
from dataclasses import dataclass, field
from typing import Optional

from llvmlite import ir

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstTypeUtils import AstTypeUtils
from SPPCompiler.SemanticAnalysis.Asts.Mixins.VisibilityEnabledAst import Visibility
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Scoping.Symbols import AliasSymbol
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import AstPrinter, ast_printer_method
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Utils.CompilerStages import PreProcessingContext
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors
from SPPCompiler.Utils.Sequence import Seq


@dataclass(slots=True)
class TypeStatementAst(Asts.Ast, Asts.Mixins.VisibilityEnabledAst, Asts.Mixins.TypeInferrable):
    annotations: Seq[Asts.AnnotationAst] = field(default_factory=Seq)
    kw_type: Asts.TokenAst = field(default=None)
    new_type: Asts.TypeAst = field(default=None)
    generic_parameter_group: Asts.GenericParameterGroupAst = field(default=None)
    tok_assign: Asts.TokenAst = field(default=None)
    old_type: Asts.TypeAst = field(default=None)

    _generated: bool = field(default=False, init=False, repr=False)
    _alias_symbol: Optional[AliasSymbol] = field(default=None, init=False, repr=False)
    _cls_ast: Optional[Asts.ClassPrototypeAst] = field(default=None, init=False, repr=False)
    _sup_ast: Optional[Asts.SupPrototypeExtensionAst] = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        self.kw_type = self.kw_type or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.KwUse)
        self.generic_parameter_group = self.generic_parameter_group or Asts.GenericParameterGroupAst(pos=self.pos)
        self.tok_assign = self.tok_assign or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkAssign)
        self.new_type = self.new_type or Asts.TypeSingleAst(self.old_type.pos, self.old_type.type_parts[-1])

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            *[a.print(printer) + "\n" for a in self.annotations],
            self.kw_type.print(printer) + " ",
            self.new_type.print(printer),
            self.generic_parameter_group.print(printer) or " ",
            self.tok_assign.print(printer) + " ",
            self.old_type.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.old_type.pos_end

    def _skip_all_type_statement_scopes(self, sm: ScopeManager, **kwargs) -> None:
        # Skip all scopes related to this type statement.
        sm.move_to_next_scope()  # cls scope
        sm.move_to_next_scope()  # type alias scope (+generics)
        sm.move_to_next_scope()  # sup scope
        sm.move_out_of_current_scope()
        sm.move_out_of_current_scope()

    def infer_type(self, sm: ScopeManager, **kwargs) -> Asts.TypeAst:
        # All statements are inferred as "void".
        return CommonTypes.Void(self.pos)

    def pre_process(self, ctx: PreProcessingContext) -> None:
        # Pre-process the annotations.
        Asts.Ast.pre_process(self, ctx)
        for a in self.annotations:
            a.pre_process(self)

    def generate_top_level_scopes(self, sm: ScopeManager, visibility: Optional[Visibility] = None) -> None:
        # Run top level scope logic for the annotations.
        for a in self.annotations:
            a.generate_top_level_scopes(sm)

        # Ensure the old type does not have a convention.
        if c := self.old_type.convention:
            raise SemanticErrors.InvalidConventionLocationError().add(
                c, self.old_type, "use statement old type").scopes(sm.current_scope)

        # Ensure the new type does not have a convention.
        if c := self.new_type.convention:
            raise SemanticErrors.InvalidConventionLocationError().add(
                c, self.new_type, "use statement new type").scopes(sm.current_scope)

        # Create a class ast for the aliased type, and generate it.
        cls_ast = Asts.ClassPrototypeAst(
            pos=self.pos, name=self.new_type, generic_parameter_group=copy.copy(self.generic_parameter_group))
        cls_ast._is_alias = True
        cls_ast._visibility = (visibility, None)
        self._alias_symbol = cls_ast.generate_top_level_scopes(sm)
        self._cls_ast = cls_ast

        # Create a new scope for the new type.
        sm.create_and_move_into_new_scope(f"<type-alias#{self.new_type}#{self.pos}>", ast=self)
        sm.move_out_of_current_scope()

        # Mark this AST as generated, so it is not generated in the analysis phase.
        self._generated = True

    def generate_top_level_aliases(self, sm: ScopeManager, **kwargs) -> None:
        sm.move_to_next_scope()  # cls scope
        sm.move_to_next_scope()  # type alias scope (+generics)

        # Load the generics into the type-alias and class scopes.
        tm = ScopeManager(sm.global_scope, sm.current_scope.get_symbol(self.old_type.without_generics).scope)
        for generic_argument in Asts.GenericArgumentGroupAst.from_parameter_group(self.generic_parameter_group).arguments:
            generic_symbol = AstTypeUtils.create_generic_symbol(sm, generic_argument, tm)
            sm.current_scope.add_symbol(generic_symbol)
            self._cls_ast._scope.add_symbol(generic_symbol)

        # Check the old type is valid, and get the new symbol.
        self.old_type.analyse_semantics(sm, **kwargs)
        self._alias_symbol.old_sym = sm.current_scope.get_symbol(self.old_type)
        self._alias_symbol.generic_impl.old_sym = sm.current_scope.get_symbol(self.old_type)

        # Create a sup ast to allow the attribute and method access.
        self._sup_ast = Asts.SupPrototypeExtensionAst(
            pos=self.pos,
            generic_parameter_group=self.generic_parameter_group.opt_to_req(),
            name=self.new_type,
            super_class=self.old_type)
        self._sup_ast.generate_top_level_scopes(sm)

        # Move out of the type alias scope.
        sm.move_out_of_current_scope()

    def qualify_types(self, sm: ScopeManager, **kwargs) -> None:
        sm.move_to_next_scope()
        sm.move_to_next_scope()

        stripped_old_type_symbol = sm.current_scope.get_symbol(self.old_type.without_generics, ignore_alias=True)
        if not stripped_old_type_symbol.is_generic:
            tm = ScopeManager(sm.global_scope, sm.current_scope.get_symbol(self.old_type.without_generics, ignore_alias=True).scope)

            self.generic_parameter_group.qualify_types(tm, **kwargs)
            self.old_type.qualify_types(tm, **kwargs)
            self.old_type.analyse_semantics(sm, **kwargs)

            self._cls_ast.generic_parameter_group = copy.copy(self.generic_parameter_group)
            self._sup_ast.generic_parameter_group = self.generic_parameter_group.opt_to_req()
            self._alias_symbol.old_sym = sm.current_scope.get_symbol(self.old_type)
            self._alias_symbol.generic_impl.old_sym = sm.current_scope.get_symbol(self.old_type)

        sm.move_to_next_scope()
        sm.move_out_of_current_scope()
        sm.move_out_of_current_scope()

    def load_super_scopes(self, sm: ScopeManager, **kwargs) -> None:
        self._skip_all_type_statement_scopes(sm, **kwargs)

    def pre_analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        self._skip_all_type_statement_scopes(sm, **kwargs)

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # Analyse the annotations.
        for a in self.annotations:
            a.analyse_semantics(sm, **kwargs)

        # If the symbol has already been generated (module/sup level, skip the scopes).
        if self._generated:
            self._skip_all_type_statement_scopes(sm)

        # Otherwise, run all the generation and analysis stages, resetting the scope each time.
        else:
            current_scope = sm.current_scope
            sm._iterator, new_iterator = itertools.tee(sm._iterator)
            self.generate_top_level_scopes(sm)

            sm.reset(current_scope, new_iterator)
            sm._iterator, new_iterator = itertools.tee(sm._iterator)
            self.generate_top_level_aliases(sm, **kwargs)

            sm.reset(current_scope, new_iterator)
            sm._iterator, new_iterator = itertools.tee(sm._iterator)
            self.qualify_types(sm, **kwargs)

    def check_memory(self, sm: ScopeManager, **kwargs) -> None:
        self._skip_all_type_statement_scopes(sm, **kwargs)

    def code_gen_pass_1(self, sm: ScopeManager, llvm_module: ir.Module, **kwargs) -> None:
        self._skip_all_type_statement_scopes(sm, **kwargs)

    def code_gen_pass_2(self, sm: ScopeManager, llvm_module: ir.Module, **kwargs) -> None:
        self._skip_all_type_statement_scopes(sm, **kwargs)


__all__ = ["TypeStatementAst"]
