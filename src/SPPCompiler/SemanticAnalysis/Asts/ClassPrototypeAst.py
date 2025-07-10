from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Dict, Optional, Type

from llvmlite import ir

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstTypeUtils import AstTypeUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Scoping.Symbols import AliasSymbol, TypeSymbol
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import AstPrinter, ast_printer_method
from SPPCompiler.SemanticAnalysis.Utils.CompilerStages import PreProcessingContext
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors
from SPPCompiler.Utils.FastDeepcopy import fast_deepcopy
from SPPCompiler.Utils.Sequence import SequenceUtils


@dataclass(slots=True)
class ClassPrototypeAst(Asts.Ast, Asts.Mixins.VisibilityEnabledAst):
    annotations: list[Asts.AnnotationAst] = field(default_factory=list)
    tok_cls: Asts.TokenAst = field(default=None)
    name: Asts.TypeAst = field(default=None)
    generic_parameter_group: Asts.GenericParameterGroupAst = field(default=None)
    where_block: Asts.WhereBlockAst = field(default=None)
    body: Asts.ClassImplementationAst = field(default=None)

    _is_alias: bool = field(default=False, init=False, repr=False)
    _cls_sym: Optional[TypeSymbol] = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        self.tok_cls = self.tok_cls or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.KwCls)
        self.generic_parameter_group = self.generic_parameter_group or Asts.GenericParameterGroupAst(pos=self.pos)
        self.where_block = self.where_block or Asts.WhereBlockAst(pos=self.pos)
        self.body = self.body or Asts.ClassImplementationAst(pos=self.pos)

    def __json__(self) -> str:
        return f"{self.name}{self.generic_parameter_group}"

    def __deepcopy__(self, memodict: Dict = None) -> ClassPrototypeAst:
        return ClassPrototypeAst(
            self.pos, copy.copy(self.annotations), self.tok_cls, self.name,
            fast_deepcopy(self.generic_parameter_group), self.where_block, fast_deepcopy(self.body),
            _visibility=self._visibility, _ctx=self._ctx, _scope=self._scope)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            SequenceUtils.print(printer, self.annotations, sep="\n"),
            self.tok_cls.print(printer) + " ",
            self.name.print(printer),
            self.generic_parameter_group.print(printer),
            self.where_block.print(printer),
            self.body.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.name.pos_end

    def _generate_symbols(self, sm: ScopeManager) -> TypeSymbol:
        SymbolType: Type[TypeSymbol] = TypeSymbol if not self._is_alias else AliasSymbol

        symbol_name = fast_deepcopy(self.name.type_parts[0])
        symbol_name.generic_argument_group = Asts.GenericArgumentGroupAst.from_parameter_group(
            self.generic_parameter_group)

        symbol_1 = SymbolType(
            name=symbol_name, type=self, scope=sm.current_scope, visibility=self._visibility[0],
            scope_defined_in=sm.current_scope)
        sm.current_scope.parent.add_symbol(symbol_1)
        sm.current_scope._type_symbol = symbol_1
        self._cls_sym = symbol_1

        if self.generic_parameter_group.parameters:
            symbol_2 = SymbolType(
                name=self.name.type_parts[0], type=self, scope=sm.current_scope, visibility=self._visibility[0],
                scope_defined_in=sm.current_scope)
            symbol_2.generic_impl = symbol_1
            sm.current_scope.parent.add_symbol(symbol_2)
            return symbol_2

        return symbol_1

    def pre_process(self, ctx: PreProcessingContext) -> None:
        Asts.Ast.pre_process(self, ctx)

        # Pre-process the annotations and implementation of this class.
        for a in self.annotations:
            a.pre_process(self)
        self.body.pre_process(self)

    def generate_top_level_scopes(self, sm: ScopeManager) -> TypeSymbol | AliasSymbol:
        # Create a new scope for the class.
        sm.create_and_move_into_new_scope(self.name, self)
        Asts.Ast.generate_top_level_scopes(self, sm)

        # Run top level scope logic for the annotations.
        for a in self.annotations:
            a.generate_top_level_scopes(sm)

        # Create a new symbol for the class.
        sym = self._generate_symbols(sm)

        # Generate the generic parameters and attributes of the class.
        for g in self.generic_parameter_group.parameters:
            g.generate_top_level_scopes(sm)
        self.body.generate_top_level_scopes(sm)

        # Move out of the type scope.
        sm.move_out_of_current_scope()
        return sym

    def generate_top_level_aliases(self, sm: ScopeManager, **kwargs) -> None:
        # Skip the class scope (no sup-scope work to do).
        sm.move_to_next_scope()
        sm.move_out_of_current_scope()

    def qualify_types(self, sm: ScopeManager, **kwargs) -> None:
        # Qualify the types in the class implementation.
        sm.move_to_next_scope()
        self.generic_parameter_group.qualify_types(sm, **kwargs)
        self.body.qualify_types(sm)
        sm.move_out_of_current_scope()

    def load_super_scopes(self, sm: ScopeManager, **kwargs) -> None:
        # Skip the class scope (no sup-scope work to do).
        sm.move_to_next_scope()
        self.body.load_super_scopes(sm, **kwargs)
        sm.move_out_of_current_scope()

    def pre_analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # Skip the class scope (no sup-scope work to do).
        sm.move_to_next_scope()
        self.body.pre_analyse_semantics(sm, **kwargs)
        sm.move_out_of_current_scope()

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # Move into the class scope.
        sm.move_to_next_scope()

        # Analyse the annotations.
        for a in self.annotations:
            a.analyse_semantics(sm, **kwargs)

        # Analyse the generic parameter group, where block, and body of the class.
        self.generic_parameter_group.analyse_semantics(sm, **kwargs)
        self.where_block.analyse_semantics(sm, **kwargs)
        self.body.analyse_semantics(sm, **kwargs)

        # Check the type isn't recursive, by recursing through all attribute types.
        if recursion := AstTypeUtils.is_type_recursive(self, sm):
            raise SemanticErrors.RecursiveTypeDefinitionError(self, recursion).scopes(sm.current_scope)

        # Move out of the class scope.
        sm.move_out_of_current_scope()

    def check_memory(self, sm: ScopeManager, **kwargs) -> None:
        sm.move_to_next_scope()
        self.body.check_memory(sm, **kwargs)
        sm.move_out_of_current_scope()

    def code_gen_pass_1(self, sm: ScopeManager, llvm_module: ir.Module, **kwargs) -> None:
        # Move into the class scope and get the class symbol.
        sm.move_to_next_scope()
        sm.move_out_of_current_scope()

    def code_gen_pass_2(self, sm: ScopeManager, llvm_module: ir.Module = None, **kwargs) -> None:
        # Move into the class scope and get the class symbol.
        sm.move_to_next_scope()
        cls_symbol = sm.current_scope.type_symbol

        # Create the attribute types for the class's memory layout.
        # if type(cls_symbol) is TypeSymbol and self.name.type_parts[-1].value[0] != "$":
        #
        #     # Get the class scope and sup scopes' class scope ASTs.
        #     scopes = [cls_symbol.scope] + [c for c in cls_symbol.scope.sup_scopes]
        #     asts   = [scope._ast for scope in scopes if type(scope._ast) is ClassPrototypeAst]
        #
        #     # Get the attribute types from the class ASTs.
        #     attribute_types = []
        #     for ast in asts:
        #         attribute_types.extend([a.type for a in ast.body.members])
        #
        #     # Set the body of the LLVM type.
        #     print(cls_symbol)
        #     print(self.name.type_parts[-1].value)
        #     cls_symbol.llvm_info.llvm_type.set_body(*attribute_types)

        # Move out of the class scope.
        sm.move_out_of_current_scope()


__all__ = [
    "ClassPrototypeAst"]
