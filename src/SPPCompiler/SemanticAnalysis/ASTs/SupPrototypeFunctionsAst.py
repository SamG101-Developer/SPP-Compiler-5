from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

from SPPCompiler.LexicalAnalysis.TokenType import TokenType
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.MultiStage.Stage1_PreProcessor import Stage1_PreProcessor, PreProcessingContext
from SPPCompiler.SemanticAnalysis.MultiStage.Stage2_SymbolGenerator import Stage2_SymbolGenerator
from SPPCompiler.SemanticAnalysis.MultiStage.Stage3_SupScopeLoader import Stage3_SupScopeLoader
from SPPCompiler.SemanticAnalysis.MultiStage.Stage4_SemanticAnalyser import Stage4_SemanticAnalyser
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.GenericParameterGroupAst import GenericParameterGroupAst
    from SPPCompiler.SemanticAnalysis.ASTs.SupImplementationAst import SupImplementationAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst
    from SPPCompiler.SemanticAnalysis.ASTs.WhereBlockAst import WhereBlockAst


@dataclass
class SupPrototypeFunctionsAst(Ast, Stage1_PreProcessor, Stage2_SymbolGenerator, Stage3_SupScopeLoader, Stage4_SemanticAnalyser):
    tok_sup: TokenAst
    generic_parameter_group: GenericParameterGroupAst
    name: TypeAst
    where_block: Optional[WhereBlockAst]
    body: SupImplementationAst

    def __post_init__(self) -> None:
        # Import the necessary classes to create default instances.
        from SPPCompiler.SemanticAnalysis import GenericParameterGroupAst
        from SPPCompiler.SemanticAnalysis import WhereBlockAst, TokenAst

        # Create default instances.
        self.tok_sup = self.tok_sup or TokenAst.default(TokenType.KwSup)
        self.generic_parameter_group = self.generic_parameter_group or GenericParameterGroupAst.default()
        self.where_block = self.where_block or WhereBlockAst.default()
        self.body = self.body or SupImplementationAst.default()

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_sup.print(printer) + " ",
            self.generic_parameter_group.print(printer),
            self.name.print(printer) + " ",
            self.where_block.print(printer),
            self.body.print(printer)]
        return "".join(string)

    def pre_process(self, context: PreProcessingContext) -> None:
        super().pre_process(context)

        # Pre-process the members of this superimposition.
        self.body.pre_process(self)

    def generate_symbols(self, scope_manager: ScopeManager, name_override: str = None) -> None:
        scope_manager.create_and_move_into_new_scope(name_override or f"<sup:{self.name}:{self.pos}>", self)
        super().generate_symbols(scope_manager)

        self.generic_parameter_group.parameters.for_each(lambda p: p.generate_symbols(scope_manager))
        self.body.generate_symbols(scope_manager)

        scope_manager.move_out_of_current_scope()

    def load_sup_scopes(self, scope_manager: ScopeManager) -> None:
        scope_manager.move_to_next_scope()

        # Cannot superimpose over a generic type.
        cls_symbol = scope_manager.current_scope.get_symbol(self.name.without_generics())
        if cls_symbol.is_generic:
            raise AstErrors.INVALID_PLACE_FOR_GENERIC(self.name, "superimpose over a generic type")

        # Register the superimposition as a "sup scope" and run the load steps for the body.
        cls_symbol.scope._direct_sup_scopes.append(scope_manager.current_scope)
        self.body.load_sup_scopes(scope_manager)
        scope_manager.move_out_of_current_scope()

    def inject_sup_scopes(self, scope_manager: ScopeManager) -> None:
        scope_manager.move_to_next_scope()
        self.body.inject_sup_scopes(scope_manager)
        scope_manager.move_out_of_current_scope()

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        from SPPCompiler.SemanticAnalysis.Meta.AstErrors import AstErrors

        # Move to the next scope.
        scope_manager.move_to_next_scope()

        # Analyse the generic parameter group.
        self.generic_parameter_group.analyse_semantics(scope_manager, **kwargs)

        # Check every generic parameter is constrained by the type.
        if unconstrained := self.generic_parameter_group.parameters.filter(lambda p: not self.name.contains_generic(p.name)):
            raise AstErrors.SUP_UNCONSTRAINED_GENERIC_PARAMETER(unconstrained[0], self.name)

        # Check there are no optional generic parameters.
        if optional := self.generic_parameter_group.get_opt():
            raise AstErrors.SUP_OPTIONAL_GENERIC_PARAMETER(optional[0])

        # Analyse the name, where block, and body.
        self.name.analyse_semantics(scope_manager, **kwargs)
        self.where_block.analyse_semantics(scope_manager, **kwargs)
        self.body.analyse_semantics(scope_manager, **kwargs)

        # Move out of the current scope.
        scope_manager.move_out_of_current_scope()


__all__ = ["SupPrototypeFunctionsAst"]
