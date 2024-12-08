from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
import copy

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.VisibilityEnabled import VisibilityEnabled
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages, PreProcessingContext
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.AnnotationAst import AnnotationAst
    from SPPCompiler.SemanticAnalysis.ASTs.ClassImplementationAst import ClassImplementationAst
    from SPPCompiler.SemanticAnalysis.ASTs.GenericParameterGroupAst import GenericParameterGroupAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst
    from SPPCompiler.SemanticAnalysis.ASTs.WhereBlockAst import WhereBlockAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class ClassPrototypeAst(Ast, VisibilityEnabled, CompilerStages):
    annotations: Seq[AnnotationAst]
    tok_cls: TokenAst
    name: TypeAst
    generic_parameter_group: GenericParameterGroupAst
    where_block: WhereBlockAst
    body: ClassImplementationAst

    _is_alias: bool = field(default=False, init=False, repr=False)

    def __post_init__(self) -> None:
        # Import the necessary classes to create default instances.
        from SPPCompiler.SemanticAnalysis import GenericParameterGroupAst
        from SPPCompiler.SemanticAnalysis import TypeAst, WhereBlockAst

        # Convert the annotations into a sequence, the name to a TypeAst, and create other defaults.
        self.annotations = Seq(self.annotations)
        self.name = TypeAst.from_identifier(self.name)
        self.generic_parameter_group = self.generic_parameter_group or GenericParameterGroupAst.default()
        self.where_block = self.where_block or WhereBlockAst.default()
        self.body = self.body or ClassImplementationAst.default()

    def __json__(self) -> str:
        return f"{self.name}{self.generic_parameter_group}"

    def __deepcopy__(self, memodict={}):
        from SPPCompiler.SemanticAnalysis import IdentifierAst
        return ClassPrototypeAst(
            self.pos, copy.deepcopy(self.annotations), copy.deepcopy(self.tok_cls), IdentifierAst.from_type(self.name),
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
        self.annotations.for_each(lambda a: a.pre_process(self))
        self.body.pre_process(self)

    def generate_symbols(self, scope_manager: ScopeManager, is_alias: bool = False) -> None:
        # Create a new scope for the class.
        scope_manager.create_and_move_into_new_scope(self.name, self)
        super().generate_symbols(scope_manager)

        # Create a new symbol for the class.
        self._generate_symbols(scope_manager)

        # Generate the generic parameters and attributes of the class.
        self.generic_parameter_group.parameters.for_each(lambda p: p.generate_symbols(scope_manager))
        self.body.generate_symbols(scope_manager)

        # Move out of the type scope.
        scope_manager.move_out_of_current_scope()

    def alias_types(self, scope_manager: ScopeManager, **kwargs) -> None:
        # Skip the class scope (no sup-scope work to do).
        scope_manager.move_to_next_scope()
        self.body.alias_types(scope_manager)
        scope_manager.move_out_of_current_scope()

    def load_sup_scopes(self, scope_manager: ScopeManager) -> None:
        # Skip the class scope (no sup-scope work to do).
        scope_manager.move_to_next_scope()
        self.body.load_sup_scopes(scope_manager)
        scope_manager.move_out_of_current_scope()

    def inject_sup_scopes(self, scope_manager: ScopeManager) -> None:
        # Skip the class scope (no sup-scope work to do).
        scope_manager.move_to_next_scope()
        self.body.inject_sup_scopes(scope_manager)
        scope_manager.move_out_of_current_scope()

    def alias_types_regeneration(self, scope_manager: ScopeManager) -> None:
        # Skip the class scope (no sup-scope work to do).
        scope_manager.move_to_next_scope()
        self.body.alias_types(scope_manager)
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

        # Move out of the class scope.
        scope_manager.move_out_of_current_scope()


__all__ = ["ClassPrototypeAst"]
