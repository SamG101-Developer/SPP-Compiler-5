from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any, Dict

from llvmlite import ir as llvm

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.CodeGen.LlvmSymbolInfo import LlvmSymbolInfo
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Meta.AstTypeManagement import AstTypeManagement
from SPPCompiler.SemanticAnalysis.Mixins.VisibilityEnabled import VisibilityEnabled
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import PreProcessingContext
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class ClassPrototypeAst(Ast, VisibilityEnabled):
    annotations: Seq[Asts.AnnotationAst] = field(default_factory=Seq)
    tok_cls: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.KwCls))
    name: Asts.TypeAst = field(default=None)
    generic_parameter_group: Asts.GenericParameterGroupAst = field(default_factory=lambda: Asts.GenericParameterGroupAst())
    where_block: Asts.WhereBlockAst = field(default_factory=lambda: Asts.WhereBlockAst())
    body: Asts.ClassImplementationAst = field(default_factory=lambda: Asts.ClassImplementationAst())

    _is_alias: bool = field(default=False, init=False, repr=False)

    def __post_init__(self) -> None:
        assert self.name

    def __json__(self) -> str:
        return f"{self.name}{self.generic_parameter_group}"

    def __deepcopy__(self, memodict: Dict = None) -> ClassPrototypeAst:
        return ClassPrototypeAst(
            self.pos, copy.copy(self.annotations), self.tok_cls, copy.deepcopy(self.name),
            copy.deepcopy(self.generic_parameter_group), copy.deepcopy(self.where_block), copy.deepcopy(self.body),
            _visibility=self._visibility, _ctx=self._ctx, _scope=self._scope)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.annotations.print(printer, " "),
            self.tok_cls.print(printer) + " ",
            self.name.print(printer),
            self.generic_parameter_group.print(printer),
            self.where_block.print(printer),
            self.body.print(printer)]
        return "".join(string)

    def _generate_symbols(self, scope_manager: ScopeManager) -> None:
        from SPPCompiler.SemanticAnalysis import GenericArgumentGroupAst
        from SPPCompiler.SemanticAnalysis.Scoping.Symbols import AliasSymbol, TypeSymbol

        symbol_type = TypeSymbol if not self._is_alias else AliasSymbol
        symbol_name = copy.deepcopy(self.name.types[-1])
        symbol_name.generic_argument_group = GenericArgumentGroupAst.from_parameter_group(self.generic_parameter_group.parameters)

        symbol_1 = symbol_type(name=symbol_name, type=self, scope=scope_manager.current_scope, visibility=self._visibility[0])
        scope_manager.current_scope.parent.add_symbol(symbol_1)
        scope_manager.current_scope._type_symbol = symbol_1

        if self.generic_parameter_group.parameters:
            symbol_2 = symbol_type(name=self.name.types[-1], type=self, visibility=self._visibility[0])
            symbol_2.scope = scope_manager.current_scope
            scope_manager.current_scope.parent.add_symbol(symbol_2)

    def pre_process(self, context: PreProcessingContext) -> None:
        super().pre_process(context)

        # Pre-process the annotations and implementation of this class.
        for a in self.annotations:
            a.pre_process(self)
        self.body.pre_process(self)

    def generate_top_level_scopes(self, scope_manager: ScopeManager, is_alias: bool = False) -> None:
        # Create a new scope for the class.
        scope_manager.create_and_move_into_new_scope(self.name, self)
        super().generate_top_level_scopes(scope_manager)

        # Create a new symbol for the class.
        self._generate_symbols(scope_manager)

        # Generate the generic parameters and attributes of the class.
        for p in self.generic_parameter_group.parameters:
            p.generate_top_level_scopes(scope_manager)
        self.body.generate_top_level_scopes(scope_manager)

        # Move out of the type scope.
        scope_manager.move_out_of_current_scope()

    def generate_top_level_aliases(self, scope_manager: ScopeManager, **kwargs) -> None:
        # Skip the class scope (no sup-scope work to do).
        scope_manager.move_to_next_scope()
        self.body.generate_top_level_aliases(scope_manager, **kwargs)
        scope_manager.move_out_of_current_scope()

    def load_super_scopes(self, scope_manager: ScopeManager) -> None:
        # Skip the class scope (no sup-scope work to do).
        scope_manager.move_to_next_scope()
        self.body.load_super_scopes(scope_manager)
        scope_manager.move_out_of_current_scope()

    def regenerate_generic_aliases(self, scope_manager: ScopeManager) -> None:
        # Skip the class scope (no sup-scope work to do).
        scope_manager.move_to_next_scope()
        self.body.generate_top_level_aliases(scope_manager)
        scope_manager.move_out_of_current_scope()

    def regenerate_generic_types(self, scope_manager: ScopeManager) -> None:
        # Skip the class scope (no sup-scope work to do).
        scope_manager.move_to_next_scope()
        self.body.regenerate_generic_types(scope_manager)
        scope_manager.move_out_of_current_scope()

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # Move into the class scope.
        scope_manager.move_to_next_scope()

        # Analyse the generic parameter group, where block, and body of the class.
        self.generic_parameter_group.analyse_semantics(scope_manager, **kwargs)
        self.where_block.analyse_semantics(scope_manager, **kwargs)
        self.body.analyse_semantics(scope_manager, **kwargs)

        # Check the type isn't recursive, by recursing through all attribute types.
        if recursion := AstTypeManagement.is_type_recursive(self, scope_manager):
            raise SemanticErrors.RecursiveTypeDefinitionError(self, recursion)

        # Move out of the class scope.
        scope_manager.move_out_of_current_scope()

    def generate_llvm_declarations(self, scope_handler: ScopeManager, llvm_module: llvm.Module, **kwargs) -> Any:
        # Move into the class scope.
        scope_handler.move_to_next_scope()
        cls_symbol = scope_handler.current_scope.type_symbol

        # Create the class type in the LLVM module (no implementation).
        llvm_type_name = str(cls_symbol.fq_name)
        llvm_type = llvm_module.context.get_identified_type(llvm_type_name)
        cls_symbol.llvm_info = LlvmSymbolInfo(llvm_type=llvm_type, llvm_module=llvm_module)

        # Move out of the class scope.
        scope_handler.move_out_of_current_scope()

    def generate_llvm_definitions(self, scope_handler: ScopeManager, llvm_module: llvm.Module = None, builder: llvm.IRBuilder = None, block: llvm.Block = None, **kwargs) -> Any:
        # Move into the class scope.
        scope_handler.move_to_next_scope()
        cls_symbol = scope_handler.current_scope.type_symbol

        # Create the super class types for the class's memory layout.
        super_class_types = []
        for super_class in cls_symbol.scope._direct_sup_scopes.filter(lambda s: isinstance(s._ast, ClassPrototypeAst)):
            super_class_types.append(super_class.type_symbol)

        # Create the attribute types for the class's memory layout.
        attribute_types = []
        for attribute in cls_symbol.scope.all_symbols(True).filter_to_type():
            attribute_types.append(attribute.type.llvm_info.llvm_type)

        # Set the body of the LLVM type.
        cls_symbol.llvm_info.llvm_type.set_body(*super_class_types, *attribute_types)

        # Move out of the class scope.
        scope_handler.move_out_of_current_scope()


__all__ = ["ClassPrototypeAst"]
