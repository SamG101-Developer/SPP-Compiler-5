from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstMemoryUtils import AstMemoryUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.CodeInjection import CodeInjection
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypes, CommonTypesPrecompiled
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors
from SPPCompiler.SyntacticAnalysis.Parser import SppParser
from SPPCompiler.Utils.Sequence import Seq


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
        # Todo: using type.type_parts()[0]... => what if the type superimposes the generic type?
        #  Get the "iterable_type" from the list of superimposed types.

        # The ".." TokenAst, or TypeAst, cannot be used as an expression for the value.
        if isinstance(self.iterable, (Asts.TokenAst, Asts.TypeAst)):
            raise SemanticErrors.ExpressionTypeInvalidError().add(self.iterable).scopes(sm.current_scope)

        # Analyse the iterable.
        self.iterable.analyse_semantics(sm, **kwargs)
        AstMemoryUtils.enforce_memory_integrity(self.iterable, self.iterable, sm, update_memory_info=False)

        # Check the iterable is a generator type.
        iterable_type = self.iterable.infer_type(sm, **kwargs)
        sup_types = sm.current_scope.get_symbol(iterable_type).scope.sup_types
        sup_types.append(sm.current_scope.get_symbol(iterable_type).fq_name)
        if not sup_types.any(lambda t: t.without_generics().symbolic_eq(CommonTypesPrecompiled.EMPTY_GENERATOR, sm.current_scope)):
            raise SemanticErrors.ExpressionNotGeneratorError().add(
                self.iterable, iterable_type, "loop").scopes(sm.current_scope)

        # Set the iterable type to the superimposed generator type.
        for sup_type in sup_types + Seq([iterable_type]):
            if sup_type.without_generics().symbolic_eq(CommonTypesPrecompiled.EMPTY_GENERATOR, sm.current_scope):
                iterable_type = sup_type
                break

        # Create a "let" statement to introduce the loop variable into the scope.
        gen_type = iterable_type.type_parts()[0].generic_argument_group["Yield"].value
        let_ast = CodeInjection.inject_code(
            f"let {self.variable}: {gen_type}", SppParser.parse_let_statement_uninitialized,
            pos_adjust=self.variable.pos)
        let_ast.analyse_semantics(sm, **kwargs)

        # Set the memory information of the symbol based on the type of iteration.
        symbols = self.variable.extract_names.map(lambda n: sm.current_scope.get_symbol(n))
        yield_type = iterable_type.type_parts()[0].generic_argument_group["Yield"].value
        for symbol in symbols:
            symbol.memory_info.ast_borrowed = self if type(yield_type.get_convention()) in [Asts.ConventionMutAst, Asts.ConventionRefAst] else None
            symbol.memory_info.is_borrow_mut = type(yield_type.get_convention()) is Asts.ConventionMutAst is not None
            symbol.memory_info.is_borrow_ref = type(yield_type.get_convention()) is Asts.ConventionRefAst is not None
            symbol.memory_info.initialized_by(self)


__all__ = [
    "LoopConditionIterableAst"]
