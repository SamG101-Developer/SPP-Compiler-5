from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING
import copy, itertools

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable, InferredType
from SPPCompiler.SemanticAnalysis.Mixins.VisibilityEnabled import AstVisibility, VisibilityEnabled
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages, PreProcessingContext
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.AnnotationAst import AnnotationAst
    from SPPCompiler.SemanticAnalysis.ASTs.IdentifierAst import IdentifierAst
    from SPPCompiler.SemanticAnalysis.ASTs.GenericParameterGroupAst import GenericParameterGroupAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


# Todo:
#  - this class is a major nasty
#  - it can be in the module/sup scope (all stages normally), or in a runtime block (all stages at once)


@dataclass
class UseStatementAst(Ast, VisibilityEnabled, TypeInferrable, CompilerStages):
    annotations: Seq[AnnotationAst]
    tok_use: TokenAst
    new_type: TypeAst
    generic_parameter_group: GenericParameterGroupAst
    tok_assign: TokenAst
    old_type: TypeAst

    _generated: bool = field(default=False, init=False, repr=False)

    def __post_init__(self) -> None:
        # Import the necessary classes to create default instances.
        from SPPCompiler.SemanticAnalysis import GenericParameterGroupAst, TypeAst

        # Convert the annotations into a sequence, the name to a TypeAst, and create defaults.
        self.annotations = Seq(self.annotations)
        self.new_type = TypeAst.from_identifier(self.new_type)
        self.generic_parameter_group = self.generic_parameter_group or GenericParameterGroupAst.default()

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

    @staticmethod
    def from_types(new_type: IdentifierAst, generic_parameter_group: Optional[GenericParameterGroupAst], old_type: TypeAst) -> UseStatementAst:
        from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
        from SPPCompiler.SemanticAnalysis import TokenAst
        return UseStatementAst(-1, Seq(), TokenAst.default(SppTokenType.KwUse), new_type, generic_parameter_group, TokenAst.default(SppTokenType.TkAssign), old_type)

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredType:
        # All statements are inferred as "void".
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
        void_type = CommonTypes.Void(self.pos)
        return InferredType.from_type(void_type)

    def pre_process(self, context: PreProcessingContext) -> None:
        for a in self.annotations:
            a.pre_process(self)
        super().pre_process(context)

    def generate_symbols(self, scope_manager: ScopeManager, visibility: AstVisibility = None) -> None:
        from SPPCompiler.SemanticAnalysis.Meta.AstMutation import AstMutation
        from SPPCompiler.SemanticAnalysis.Scoping.Symbols import TypeSymbol
        from SPPCompiler.SyntacticAnalysis.Parser import SppParser

        # Create a class ast for the aliased type, and generate it.
        cls_ast = AstMutation.inject_code(f"cls {self.new_type} {{}}", SppParser.parse_class_prototype)
        cls_ast.generic_parameter_group = copy.copy(self.generic_parameter_group)
        cls_ast._is_alias = True
        cls_ast._visibility = (visibility, None)
        cls_ast.generate_symbols(scope_manager)

        # Create a scope for the alias' generics, so analysing can be done with the generics, without them leaking.
        scope_manager.create_and_move_into_new_scope(f"<type-alias:{self.new_type}:{self.pos}>", self)
        for generic_parameter in self.generic_parameter_group.parameters:
            type_symbol = TypeSymbol(name=generic_parameter.name.types[-1], type=None, is_generic=True)
            scope_manager.current_scope.add_symbol(type_symbol)
        scope_manager.move_out_of_current_scope()

        # Mark this AST as generated, so it is not generated in the analysis phase.
        self._generated = True

    def alias_types(self, scope_manager: ScopeManager, **kwargs) -> None:
        from SPPCompiler.SemanticAnalysis.Meta.AstMutation import AstMutation
        from SPPCompiler.SyntacticAnalysis.Parser import SppParser

        # Skip the class scope and move into the type-alias scope (generic access)
        scope_manager.move_to_next_scope()
        scope_manager.move_to_next_scope()

        # Ensure the validity of the old type.
        self.old_type.analyse_semantics(scope_manager)
        old_type_symbol = scope_manager.current_scope.get_symbol(self.old_type)

        # Create a sup ast to allow the attribute and method access.
        sup_ast = AstMutation.inject_code(f"sup {self.new_type} ext {self.old_type} {{}}", SppParser.parse_sup_prototype_inheritance)
        sup_ast.generic_parameter_group = copy.copy(self.generic_parameter_group)  # Todo: is this required?
        sup_ast.generate_symbols(scope_manager)

        # Register the old type against the new alias symbol.
        alias_symbol = scope_manager.current_scope.get_symbol(self.new_type)
        alias_symbol.old_type = old_type_symbol.fq_name

        # Move out of the type-alias scopes.
        scope_manager.move_out_of_current_scope()

    def load_sup_scopes(self, scope_manager: ScopeManager) -> None:
        # Skip through the class, type-alias and superimposition scopes.
        scope_manager.move_to_next_scope()
        scope_manager.move_to_next_scope()
        scope_manager.move_to_next_scope()
        scope_manager.move_out_of_current_scope()
        scope_manager.move_out_of_current_scope()

    def inject_sup_scopes(self, scope_manager: ScopeManager) -> None:
        # Skip through the class, type-alias and superimposition scopes.
        scope_manager.move_to_next_scope()
        scope_manager.move_to_next_scope()
        scope_manager.move_to_next_scope()
        scope_manager.move_out_of_current_scope()
        scope_manager.move_out_of_current_scope()

    def alias_types_regeneration(self, scope_manager: ScopeManager) -> None:
        # Skip through the class, type-alias and superimposition scopes.
        scope_manager.move_to_next_scope()
        scope_manager.move_to_next_scope()

        # Ensure the validity of the old type.
        self.old_type.analyse_semantics(scope_manager)

        scope_manager.move_to_next_scope()
        scope_manager.move_out_of_current_scope()
        scope_manager.move_out_of_current_scope()

    def regenerate_generic_types(self, scope_manager: ScopeManager) -> None:
        # Skip through the class, type-alias and superimposition scopes.
        scope_manager.move_to_next_scope()
        scope_manager.move_to_next_scope()
        scope_manager.move_to_next_scope()
        scope_manager.move_out_of_current_scope()
        scope_manager.move_out_of_current_scope()

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
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
            self.generate_symbols(scope_manager)

            scope_manager.reset(current_scope, new_iterator)
            scope_manager._iterator, new_iterator = itertools.tee(scope_manager._iterator)
            self.alias_types(scope_manager)

            scope_manager.reset(current_scope, new_iterator)
            scope_manager._iterator, new_iterator = itertools.tee(scope_manager._iterator)
            self.load_sup_scopes(scope_manager)

            scope_manager.reset(current_scope, new_iterator)
            self.inject_sup_scopes(scope_manager)


__all__ = ["UseStatementAst"]
