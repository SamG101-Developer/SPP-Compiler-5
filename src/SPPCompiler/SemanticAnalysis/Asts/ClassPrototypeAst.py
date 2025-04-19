from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from llvmlite import ir as llvm

from SPPCompiler.CodeGen.LlvmSymbolInfo import LlvmSymbolInfo
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstTypeUtils import AstTypeUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Scoping.Symbols import AliasSymbol, TypeSymbol
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.CompilerStages import PreProcessingContext
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class ClassPrototypeAst(Asts.Ast, Asts.Mixins.VisibilityEnabledAst):
    annotations: Seq[Asts.AnnotationAst] = field(default_factory=Seq)
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
        assert self.name is not None

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

    @property
    def pos_end(self) -> int:
        return self.body.pos_end

    def _generate_symbols(self, sm: ScopeManager) -> TypeSymbol:
        SymbolType = TypeSymbol if not self._is_alias else AliasSymbol

        symbol_name = copy.deepcopy(self.name.type_parts()[0])
        symbol_name.generic_argument_group = Asts.GenericArgumentGroupAst.from_parameter_group(self.generic_parameter_group.parameters, use_default=True)

        symbol_1 = SymbolType(name=symbol_name, type=self, scope=sm.current_scope, visibility=self._visibility[0])
        sm.current_scope.parent.add_symbol(symbol_1)
        sm.current_scope._type_symbol = symbol_1
        self._cls_sym = symbol_1

        if self.generic_parameter_group.parameters:
            symbol_2 = SymbolType(name=self.name.type_parts()[0], type=self, scope=sm.current_scope, visibility=self._visibility[0])
            symbol_2.generic_impl = symbol_1
            sm.current_scope.parent.add_symbol(symbol_2)
            return symbol_2

        return symbol_1

    def pre_process(self, ctx: PreProcessingContext) -> None:
        super().pre_process(ctx)

        # Pre-process the annotations and implementation of this class.
        for a in self.annotations:
            a.pre_process(self)
        self.body.pre_process(self)

    def generate_top_level_scopes(self, sm: ScopeManager) -> TypeSymbol | AliasSymbol:
        # Create a new scope for the class.
        sm.create_and_move_into_new_scope(self.name, self)
        super().generate_top_level_scopes(sm)

        # Run top level scope logic for the annotations.
        for a in self.annotations:
            a.generate_top_level_scopes(sm)

        # Create a new symbol for the class.
        sym = self._generate_symbols(sm)

        # Generate the generic parameters and attributes of the class.
        for p in self.generic_parameter_group.parameters:
            p.generate_top_level_scopes(sm)
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

        for g in self._cls_sym.type.generic_parameter_group.get_optional_params():
            x = sm.current_scope.get_symbol(g.default.without_generics())
            if x.is_generic: continue
            g.default.analyse_semantics(sm, type_scope=x.scope.parent_module)
            g.default = x.scope.get_symbol(g.default).fq_name

        for g in self._cls_sym.name.generic_argument_group.get_type_args():
            x = sm.current_scope.get_symbol(g.value.without_generics())
            if x.is_generic: continue
            g.value.analyse_semantics(sm, type_scope=x.scope.parent_module)
            g.value = x.scope.get_symbol(g.value).fq_name

        self.body.qualify_types(sm)
        sm.move_out_of_current_scope()

    def load_super_scopes(self, sm: ScopeManager, **kwargs) -> None:
        # Skip the class scope (no sup-scope work to do).
        sm.move_to_next_scope()
        self.body.load_super_scopes(sm)
        sm.move_out_of_current_scope()

    def pre_analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # Skip the class scope (no sup-scope work to do).
        sm.move_to_next_scope()
        self.body.pre_analyse_semantics(sm, **kwargs)
        sm.move_out_of_current_scope()

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # Move into the class scope.
        if "no_scope" not in kwargs:
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
        if "no_scope" not in kwargs:
            sm.move_out_of_current_scope()

    def generate_llvm_declarations(self, sm: ScopeManager, llvm_module: llvm.Module, **kwargs) -> Any:
        # Move into the class scope.
        sm.move_to_next_scope()
        cls_symbol = sm.current_scope.type_symbol

        # Create the class type in the LLVM module (no implementation).
        llvm_type_name = str(cls_symbol.fq_name)
        llvm_type = llvm_module.context.get_identified_type(llvm_type_name)
        cls_symbol.llvm_info = LlvmSymbolInfo(llvm_type=llvm_type, llvm_module=llvm_module)

        # Move out of the class scope.
        sm.move_out_of_current_scope()

    def generate_llvm_definitions(self, sm: ScopeManager, llvm_module: llvm.Module = None, builder: llvm.IRBuilder = None, block: llvm.Block = None, **kwargs) -> Any:
        # Move into the class scope.
        sm.move_to_next_scope()
        cls_symbol = sm.current_scope.type_symbol

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
        sm.move_out_of_current_scope()


__all__ = [
    "ClassPrototypeAst"]
