from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstMemoryUtils import AstMemoryUtils
from SPPCompiler.SemanticAnalysis.AstUtils.AstTypeUtils import AstTypeUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors


# Todo:
#  - [1] Does the generator have to be owned? pins would ensure memory safety
#  - [3] Maintain the borrow from the iterator - x in y.iter_mut() => cant borrow from y inside the loop


@dataclass(slots=True)
class LoopConditionIterableAst(Asts.Ast, Asts.Mixins.TypeInferrable):
    variable: Asts.LocalVariableAst = field(default=None)
    in_keyword: Asts.TokenAst = field(default=None)
    iterable: Asts.ExpressionAst = field(default=None)

    def __post_init__(self) -> None:
        self.in_keyword = self.in_keyword or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.KwIn)
        assert self.variable is not None and self.iterable is not None

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

    def infer_type(self, sm: ScopeManager, **kwargs) -> Asts.TypeAst:
        # Infer the type from the iterable.
        return self.iterable.infer_type(sm, **kwargs)

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # Todo: iteration should be optional values? how this work with conventions?

        # The ".." TokenAst, or TypeAst, cannot be used as an expression for the value.
        if isinstance(self.iterable, (Asts.TokenAst, Asts.TypeAst)):
            raise SemanticErrors.ExpressionTypeInvalidError().add(self.iterable).scopes(sm.current_scope)

        # Analyse the iterable.
        self.iterable.analyse_semantics(sm, **kwargs)
        AstMemoryUtils.enforce_memory_integrity(self.iterable, self.iterable, sm, update_memory_info=False)

        # Get the generator and yielded type from the iterable.
        iterable_type = self.iterable.infer_type(sm, **kwargs)
        gen_type, yield_type = AstTypeUtils.get_generator_and_yielded_type(iterable_type, sm, self.iterable, "loop condition")

        # Create a "let" statement to introduce the loop variable into the scope.
        let_ast = Asts.LetStatementUninitializedAst(pos=self.variable.pos, assign_to=self.variable, type=yield_type)
        let_ast.analyse_semantics(sm, **kwargs)

        # Set the memory information of the symbol based on the type of iteration.
        symbols = self.variable.extract_names.map(lambda n: sm.current_scope.get_symbol(n))
        for symbol in symbols:
            symbol.memory_info.ast_borrowed = self if type(yield_type.get_convention()) in [Asts.ConventionMutAst, Asts.ConventionRefAst] else None
            symbol.memory_info.is_borrow_mut = type(yield_type.get_convention()) is Asts.ConventionMutAst is not None
            symbol.memory_info.is_borrow_ref = type(yield_type.get_convention()) is Asts.ConventionRefAst is not None
            symbol.memory_info.initialized_by(self)


__all__ = [
    "LoopConditionIterableAst"]
