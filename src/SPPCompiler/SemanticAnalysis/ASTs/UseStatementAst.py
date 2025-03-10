from __future__ import annotations

import copy
import itertools
from dataclasses import dataclass, field
from typing import Optional

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstMutation import AstMutation
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable
from SPPCompiler.SemanticAnalysis.Mixins.VisibilityEnabled import AstVisibility, VisibilityEnabled
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import PreProcessingContext
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Scoping.Symbols import TypeSymbol
from SPPCompiler.SyntacticAnalysis.Parser import SppParser
from SPPCompiler.Utils.Sequence import Seq


# Todo:
#  - this class is a major nasty
#  - it can be in the module/sup scope (all stages normally), or in a runtime block (all stages at once)


@dataclass
class UseStatementAst(Ast, VisibilityEnabled, TypeInferrable):
    annotations: Seq[Asts.AnnotationAst] = field(default_factory=Seq)
    tok_use: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.KwUse))
    new_type: Asts.TypeAst = field(default=None)
    generic_parameter_group: Asts.GenericParameterGroupAst = field(default_factory=lambda: Asts.GenericParameterGroupAst())
    tok_assign: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.TkAssign))
    old_type: Asts.TypeAst = field(default=None)

    _generated: bool = field(default=False, init=False, repr=False)

    def __post_init__(self) -> None:
        assert self.new_type
        assert self.old_type

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.annotations.print(printer, " "),
            self.tok_use.print(printer) + " ",
            self.new_type.print(printer),
            self.generic_parameter_group.print(printer) or " ",
            self.tok_assign.print(printer) + " ",
            self.old_type.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.old_type.pos_end

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> Asts.TypeAst:
        # All statements are inferred as "void".
        return CommonTypes.Void(self.pos)

    def pre_process(self, context: PreProcessingContext) -> None:
        # Pre-process the annotations.
        for a in self.annotations:
            a.pre_process(self)
        super().pre_process(context)

    def generate_top_level_scopes(self, scope_manager: ScopeManager, visibility: Optional[AstVisibility] = None) -> None:
        # Run top level scope logic for the annotations.
        for a in self.annotations:
            a.generate_top_level_scopes(scope_manager)

        # Ensure the old type does not have a convention.
        if type(c := self.old_type.get_convention()) is not Asts.ConventionMovAst:
            raise SemanticErrors.InvalidConventionLocationError().add(c, self.old_type, "use statement old type").scopes(scope_manager.current_scope)

        # Ensure the new type does not have a convention.
        if type(c := self.new_type.get_convention()) is not Asts.ConventionMovAst:
            raise SemanticErrors.InvalidConventionLocationError().add(c, self.new_type, "use statement new type").scopes(scope_manager.current_scope)

        # Create a class ast for the aliased type, and generate it.
        cls_ast = AstMutation.inject_code(f"cls {self.new_type} {{}}", SppParser.parse_class_prototype)
        cls_ast.generic_parameter_group = copy.copy(self.generic_parameter_group)
        cls_ast._is_alias = True
        cls_ast._visibility = (visibility, None)
        cls_ast.generate_top_level_scopes(scope_manager)

        # Create a scope for the alias' generics, so analysing can be done with the generics, without them leaking.
        scope_manager.create_and_move_into_new_scope(f"<type-alias:{self.new_type}:{self.pos}>", self)
        for generic_parameter in self.generic_parameter_group.parameters:
            type_symbol = TypeSymbol(name=generic_parameter.name.type_parts()[0], type=None, is_generic=True)
            scope_manager.current_scope.add_symbol(type_symbol)
        scope_manager.move_out_of_current_scope()

        # Mark this AST as generated, so it is not generated in the analysis phase.
        self._generated = True

    def generate_top_level_aliases(self, scope_manager: ScopeManager, **kwargs) -> None:
        # Skip the class scope and move into the type-alias scope (generic access)
        scope_manager.move_to_next_scope()
        scope_manager.move_to_next_scope()

        # Ensure the validity of the old type.
        self.old_type.analyse_semantics(scope_manager)
        old_type_symbol = scope_manager.current_scope.get_symbol(self.old_type.infer_type(scope_manager))

        # Create a sup ast to allow the attribute and method access.
        sup_ast = AstMutation.inject_code(f"sup {self.generic_parameter_group} {self.new_type} ext {self.old_type} {{}}", SppParser.parse_sup_prototype_extension)
        sup_ast.generate_top_level_scopes(scope_manager)

        # Register the old type against the new alias symbol.
        alias_symbol = scope_manager.current_scope.get_symbol(self.new_type)
        alias_symbol.old_type = old_type_symbol.fq_name

        # Move out of the type-alias scopes.
        scope_manager.move_out_of_current_scope()

    def load_super_scopes(self, scope_manager: ScopeManager) -> None:
        # Skip through the class, type-alias and superimposition scopes.
        scope_manager.move_to_next_scope()
        scope_manager.move_to_next_scope()
        self.old_type.analyse_semantics(scope_manager)
        scope_manager.move_to_next_scope()
        scope_manager.move_out_of_current_scope()
        scope_manager.move_out_of_current_scope()

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # Analyse the annotations.
        for a in self.annotations:
            a.analyse_semantics(scope_manager, **kwargs)

        # If the symbol has already been generated (module/sup level, skip the scopes).
        if self._generated:
            scope_manager.move_to_next_scope()
            scope_manager.move_to_next_scope()
            scope_manager.move_to_next_scope()
            scope_manager.move_out_of_current_scope()
            scope_manager.move_out_of_current_scope()

        # Otherwise, run all the generation and analysis stages, resetting the scope each time.
        else:
            current_scope = scope_manager.current_scope
            scope_manager._iterator, new_iterator = itertools.tee(scope_manager._iterator)
            self.generate_top_level_scopes(scope_manager)

            scope_manager.reset(current_scope, new_iterator)
            scope_manager._iterator, new_iterator = itertools.tee(scope_manager._iterator)
            self.generate_top_level_aliases(scope_manager)

            scope_manager.reset(current_scope, new_iterator)
            scope_manager._iterator, new_iterator = itertools.tee(scope_manager._iterator)
            self.load_super_scopes(scope_manager)


__all__ = ["UseStatementAst"]
