from __future__ import annotations

from dataclasses import dataclass, field

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstMemory import AstMemoryHandler
from SPPCompiler.SemanticAnalysis.Meta.AstMutation import AstMutation
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SyntacticAnalysis.Parser import SppParser


# Todo:
#  - [1] Does the generator have to be owned? pins would ensure memory safety
#  - [3] Maintain the borrow from the iterator - x in y.iter_mut() => cant borrow from y inside the loop


@dataclass
class LoopConditionIterableAst(Ast, TypeInferrable):
    variable: Asts.LocalVariableAst = field(default=None)
    in_keyword: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.KwIn))
    iterable: Asts.ExpressionAst = field(default=None)

    def __post_init__(self) -> None:
        assert self.variable
        assert self.iterable

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.variable.print(printer),
            self.in_keyword.print(printer),
            self.iterable.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.iterable.pos_end

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> Asts.TypeAst:
        # Infer the type from the iterable.
        return self.iterable.infer_type(scope_manager, **kwargs)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # Todo: iteration should be optional values? how this work with conventions?
        # Todo: using type.type_parts()[0]... => what if the type superimposes the generic type?
        #  Get the "iterable_type" from the list of superimposed types.

        # The ".." TokenAst, or TypeAst, cannot be used as an expression for the value.
        if isinstance(self.iterable, (Asts.TokenAst, Asts.TypeAst)):
            raise SemanticErrors.ExpressionTypeInvalidError().add(self.iterable).scopes(scope_manager.current_scope)

        # Analyse the iterable.
        self.iterable.analyse_semantics(scope_manager, **kwargs)
        AstMemoryHandler.enforce_memory_integrity(self.iterable, self.iterable, scope_manager, update_memory_info=False)

        # Check the iterable is a generator type.
        iterable_type = self.iterable.infer_type(scope_manager, **kwargs)
        superimposed_types = scope_manager.current_scope.get_symbol(iterable_type).scope.sup_types.map(lambda t: t.without_generics())
        superimposed_types.append(scope_manager.current_scope.get_symbol(iterable_type).fq_name.without_generics())
        if not superimposed_types.any(lambda t: t.without_generics().symbolic_eq(CommonTypes.Gen().without_generics(), scope_manager.current_scope)):
            raise SemanticErrors.ExpressionNotGeneratorError().add(self.iterable, iterable_type, "loop").scopes(scope_manager.current_scope)

        # Create a "let" statement to introduce the loop variable into the scope.
        gen_type = iterable_type.type_parts()[0].generic_argument_group["Yield"].value
        let_ast = AstMutation.inject_code(
            f"let {self.variable}: {gen_type}", SppParser.parse_let_statement_uninitialized,
            pos_adjust=self.variable.pos)
        let_ast.analyse_semantics(scope_manager, **kwargs)

        # Set the memory information of the symbol based on the type of iteration.
        symbols = self.variable.extract_names.map(lambda n: scope_manager.current_scope.get_symbol(n))
        for symbol in symbols:
            symbol.memory_info.ast_borrowed = self if iterable_type.type_parts()[0].value in ["GenMut", "GenRef"] else None
            symbol.memory_info.is_borrow_mut = iterable_type.type_parts()[0].value == "GenMut"
            symbol.memory_info.is_borrow_ref = iterable_type.type_parts()[0].value == "GenRef"
            symbol.memory_info.initialized_by(self)


__all__ = ["LoopConditionIterableAst"]
