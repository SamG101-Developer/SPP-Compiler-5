from __future__ import annotations

import copy
import itertools
from dataclasses import dataclass, field
from typing import Optional

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Asts.Mixins.VisibilityEnabledAst import Visibility
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Scoping.Symbols import TypeSymbol
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.CodeInjection import CodeInjection
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Utils.CompilerStages import PreProcessingContext
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors
from SPPCompiler.SyntacticAnalysis.Parser import SppParser
from SPPCompiler.Utils.Sequence import Seq


def _skip_all_use_statement_scopes(sm: ScopeManager, **kwargs) -> None:
    # Skip through the class, type-alias and superimposition scopes.
    sm.move_to_next_scope()
    sm.move_to_next_scope()
    sm.move_to_next_scope()
    sm.move_out_of_current_scope()
    sm.move_out_of_current_scope()


@dataclass
class UseStatementAst(Asts.Ast, Asts.Mixins.VisibilityEnabledAst, Asts.Mixins.TypeInferrable):
    annotations: Seq[Asts.AnnotationAst] = field(default_factory=Seq)
    kw_use: Asts.TokenAst = field(default=None)
    new_type: Asts.TypeAst = field(default=None)
    generic_parameter_group: Asts.GenericParameterGroupAst = field(default=None)
    tok_assign: Asts.TokenAst = field(default=None)
    old_type: Asts.TypeAst = field(default=None)

    _generated: bool = field(default=False, init=False, repr=False)

    def __post_init__(self) -> None:
        self.kw_use = self.kw_use or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.KwUse)
        self.generic_parameter_group = self.generic_parameter_group or Asts.GenericParameterGroupAst(pos=self.pos)
        self.tok_assign = self.tok_assign or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkAssign)
        assert self.new_type is not None and self.old_type is not None

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.annotations.print(printer, " "),
            self.kw_use.print(printer) + " ",
            self.new_type.print(printer),
            self.generic_parameter_group.print(printer) or " ",
            self.tok_assign.print(printer) + " ",
            self.old_type.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.old_type.pos_end

    def infer_type(self, sm: ScopeManager, **kwargs) -> Asts.TypeAst:
        # All statements are inferred as "void".
        return CommonTypes.Void(self.pos)

    def pre_process(self, ctx: PreProcessingContext) -> None:
        # Pre-process the annotations.
        for a in self.annotations:
            a.pre_process(self)
        super().pre_process(ctx)

    def generate_top_level_scopes(self, sm: ScopeManager, visibility: Optional[Visibility] = None, **kwargs) -> None:
        # Run top level scope logic for the annotations.
        for a in self.annotations:
            a.generate_top_level_scopes(sm)

        # Ensure the old type does not have a convention.
        if c := self.old_type.get_convention():
            raise SemanticErrors.InvalidConventionLocationError().add(
                c, self.old_type, "use statement old type").scopes(sm.current_scope)

        # Ensure the new type does not have a convention.
        if c := self.new_type.get_convention():
            raise SemanticErrors.InvalidConventionLocationError().add(
                c, self.new_type, "use statement new type").scopes(sm.current_scope)

        # Create a class ast for the aliased type, and generate it.
        cls_ast = CodeInjection.inject_code(
            f"cls {self.new_type} {{}}",
            SppParser.parse_class_prototype, pos_adjust=self.pos)
        cls_ast.generic_parameter_group = copy.copy(self.generic_parameter_group)
        cls_ast._is_alias = True
        cls_ast._visibility = (visibility, None)
        cls_ast.generate_top_level_scopes(sm)

        # Create a scope for the alias' generics, so analysing can be done with the generics, without them leaking.
        sm.create_and_move_into_new_scope(f"<type-alias:{self.new_type}:{self.pos}>", self)
        for generic_parameter in self.generic_parameter_group.parameters:
            type_symbol = TypeSymbol(name=generic_parameter.name.type_parts()[0], type=None, is_generic=True)
            sm.current_scope.add_symbol(type_symbol)
        sm.move_out_of_current_scope()

        # Mark this AST as generated, so it is not generated in the analysis phase.
        self._generated = True

    def generate_top_level_aliases(self, sm: ScopeManager, **kwargs) -> None:
        # Skip the class scope and move into the type-alias scope (generic access)
        sm.move_to_next_scope()
        sm.move_to_next_scope()

        # Ensure the validity of the old type.
        self.old_type.analyse_semantics(sm)
        old_type_symbol = sm.current_scope.get_symbol(self.old_type.infer_type(sm))

        # Create a sup ast to allow the attribute and method access.
        sup_ast = CodeInjection.inject_code(
            f"sup {self.generic_parameter_group} {self.new_type} ext {self.old_type} {{}}",
            SppParser.parse_sup_prototype_extension, pos_adjust=self.pos)
        sup_ast.generate_top_level_scopes(sm)

        # Register the old type against the new alias symbol.
        alias_symbol = sm.current_scope.get_symbol(self.new_type)
        alias_symbol.old_type = old_type_symbol.fq_name

        # Move out of the type-alias scopes.
        sm.move_out_of_current_scope()

    def load_super_scopes(self, sm: ScopeManager, **kwargs) -> None:
        _skip_all_use_statement_scopes(sm, **kwargs)

    def pre_analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        _skip_all_use_statement_scopes(sm, **kwargs)

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # Analyse the annotations.
        for a in self.annotations:
            a.analyse_semantics(sm, **kwargs)

        # If the symbol has already been generated (module/sup level, skip the scopes).
        if self._generated:
            _skip_all_use_statement_scopes(sm)

        # Otherwise, run all the generation and analysis stages, resetting the scope each time.
        else:
            current_scope = sm.current_scope
            sm._iterator, new_iterator = itertools.tee(sm._iterator)
            self.generate_top_level_scopes(sm, **kwargs)

            sm.reset(current_scope, new_iterator)
            sm._iterator, new_iterator = itertools.tee(sm._iterator)
            self.generate_top_level_aliases(sm, **kwargs)

            sm.reset(current_scope, new_iterator)
            sm._iterator, new_iterator = itertools.tee(sm._iterator)
            self.load_super_scopes(sm, **kwargs)


__all__ = ["UseStatementAst"]
