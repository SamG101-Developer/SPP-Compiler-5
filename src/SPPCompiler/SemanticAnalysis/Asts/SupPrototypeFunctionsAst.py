from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from llvmlite import ir

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Scoping.Symbols import AliasSymbol
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import AstPrinter, ast_printer_method
from SPPCompiler.SemanticAnalysis.Utils.CompilerStages import PreProcessingContext
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors


@dataclass(slots=True, repr=False)
class SupPrototypeFunctionsAst(Asts.Ast):
    tok_sup: Asts.TokenAst = field(default=None)
    generic_parameter_group: Asts.GenericParameterGroupAst = field(default=None)
    name: Asts.TypeAst = field(default=None)
    where_block: Optional[Asts.WhereBlockAst] = field(default=None)
    body: Asts.SupImplementationAst = field(default=None)

    def __post_init__(self) -> None:
        self.tok_sup = self.tok_sup or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.KwSup)
        self.generic_parameter_group = self.generic_parameter_group or Asts.GenericParameterGroupAst(pos=self.pos)
        self.where_block = self.where_block or Asts.WhereBlockAst(pos=self.pos)
        self.body = self.body or Asts.SupImplementationAst(pos=self.pos)

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

    @property
    def pos_end(self) -> int:
        return self.name.pos_end

    def pre_process(self, ctx: PreProcessingContext) -> None:
        # Pre-process the members of this superimposition.
        Asts.Ast.pre_process(self, ctx)
        self.body.pre_process(self)

    def generate_top_level_scopes(self, sm: ScopeManager) -> None:
        # Create a new scope for the superimposition.
        sm.create_and_move_into_new_scope(f"<sup#{self.name}#{self.pos}>", self)
        Asts.Ast.generate_top_level_scopes(self, sm)

        # Check there are no optional generic parameters.
        if optional := self.generic_parameter_group.get_optional_params():
            raise SemanticErrors.SuperimpositionOptionalGenericParameterError().add(
                optional[0]).scopes(sm.current_scope)

        # Check every generic parameter is constrained by the type.
        if unconstrained := [p for p in self.generic_parameter_group.parameters if not self.name.contains_generic(p.name)]:
            raise SemanticErrors.SuperimpositionUnconstrainedGenericParameterError().add(
                unconstrained[0], self.name).scopes(sm.current_scope)

        # Ensure the superimposition type does not have a convention.
        if c := self.name.convention:
            raise SemanticErrors.InvalidConventionLocationError().add(
                c, self.name, "superimposition type").scopes(sm.current_scope)

        # Generate the symbols for the generic parameter group, and the self type.
        for p in self.generic_parameter_group.parameters:
            p.generate_top_level_scopes(sm)
        self.body.generate_top_level_scopes(sm)

        sm.move_out_of_current_scope()

    def generate_top_level_aliases(self, sm: ScopeManager, **kwargs) -> None:
        # Skip the class scope (no sup-scope work to do).
        sm.move_to_next_scope()
        self.body.generate_top_level_aliases(sm, **kwargs)
        sm.move_out_of_current_scope()

    def qualify_types(self, sm: ScopeManager, **kwargs) -> None:
        sm.move_to_next_scope()
        self.generic_parameter_group.qualify_types(sm, **kwargs)
        self.body.qualify_types(sm, **kwargs)
        sm.move_out_of_current_scope()

    def load_super_scopes(self, sm: ScopeManager, **kwargs) -> None:
        sm.move_to_next_scope()
        self.name.analyse_semantics(sm, **kwargs)
        self.name = sm.current_scope.get_symbol(self.name).fq_name

        cls_symbol = sm.current_scope.get_symbol(self.name.without_generics)
        if sm.current_scope.parent is sm.current_scope.parent_module:
            if not cls_symbol.is_generic:
                sm.normal_sup_blocks[cls_symbol].append(sm.current_scope)
            else:
                sm.generic_sup_blocks[cls_symbol] = sm.current_scope

        # Add the "Self" symbol into the scope.
        if self.name.type_parts[0].value[0] != "$":
            cls_symbol = sm.current_scope.get_symbol(self.name)
            sm.current_scope.add_symbol(AliasSymbol(
                name=Asts.TypeIdentifierAst(value="Self"),
                type=None,
                scope=cls_symbol.scope,
                scope_defined_in=sm.current_scope,
                old_sym=cls_symbol))

        self.body.load_super_scopes(sm, **kwargs)
        sm.move_out_of_current_scope()

    def pre_analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        sm.move_to_next_scope()
        self.name.analyse_semantics(sm, **kwargs)
        cls_symbol = sm.current_scope.get_symbol(self.name)

        # Pre-analyse all the members.
        self.body.pre_analyse_semantics(sm, **kwargs)
        sm.move_out_of_current_scope()

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:

        # Move to the next scope.
        sm.move_to_next_scope()

        # Analyse the generic parameter group, name, where block, and body.
        self.name.analyse_semantics(sm, **kwargs)
        self.where_block.analyse_semantics(sm, **kwargs)
        self.body.analyse_semantics(sm, **kwargs)

        # Move out of the current scope.
        sm.move_out_of_current_scope()

    def check_memory(self, sm: ScopeManager, **kwargs) -> None:
        sm.move_to_next_scope()
        self.body.check_memory(sm, **kwargs)
        sm.move_out_of_current_scope()

    def code_gen_pass_1(self, sm: ScopeManager, llvm_module: ir.Module, **kwargs) -> None:
        # Generate the LLVM code for the superimposition.
        sm.move_to_next_scope()
        self.body.code_gen_pass_1(sm, llvm_module, **kwargs)
        sm.move_out_of_current_scope()

    def code_gen_pass_2(self, sm: ScopeManager, llvm_module: ir.Module = None, **kwargs) -> None:
        # Generate the LLVM code for the superimposition.
        sm.move_to_next_scope()
        self.body.code_gen_pass_2(sm, llvm_module, **kwargs)
        sm.move_out_of_current_scope()


__all__ = [
    "SupPrototypeFunctionsAst"]
