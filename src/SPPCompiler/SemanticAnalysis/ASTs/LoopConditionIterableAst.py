from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstMemory import AstMemoryHandler
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable, InferredType
from SPPCompiler.SemanticAnalysis.MultiStage.Stage4_SemanticAnalyser import Stage4_SemanticAnalyser
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.ASTs.LocalVariableAst import LocalVariableAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class LoopConditionIterableAst(Ast, TypeInferrable, Stage4_SemanticAnalyser):
    variable: LocalVariableAst
    in_keyword: TokenAst
    iterable: ExpressionAst

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.variable.print(printer),
            self.in_keyword.print(printer),
            self.iterable.print(printer)]
        return "".join(string)

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredType:
        # Infer the type from the iterable.
        return self.iterable.infer_type(scope_manager, **kwargs)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        from SPPCompiler.SemanticAnalysis import TokenAst, TypeAst
        from SPPCompiler.SemanticAnalysis.Meta.AstErrors import AstErrors
        from SPPCompiler.SemanticAnalysis.Meta.AstMutation import AstMutation
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
        from SPPCompiler.SyntacticAnalysis.Parser import Parser

        # The ".." TokenAst, or TypeAst, cannot be used as an expression for the value.
        if isinstance(self.iterable, (TokenAst, TypeAst)):
            raise AstErrors.INVALID_EXPRESSION(self.iterable)

        # Analyse the iterable.
        self.iterable.analyse_semantics(scope_manager, **kwargs)
        AstMemoryHandler.enforce_memory_integrity(self.iterable, self.iterable, scope_manager, update_memory_info=False)

        # Check the iterable is a generator type.
        # Todo: Check the type superimposes a Gen type rather that is a Gen type.
        # Todo: Generator has to be owned? If so, change to InferredType checks.
        allowed_types = Seq([CommonTypes.GenMov(), CommonTypes.GenMut(), CommonTypes.GenRef()]).map(TypeAst.without_generics).map(InferredType.from_type)
        iterable_type = self.iterable.infer_type(scope_manager, **kwargs)
        if not allowed_types.any(lambda t: t.symbolic_eq(iterable_type, scope_manager.current_scope)):
            raise AstErrors.INVALID_ITERABLE_TYPE(self.iterable, iterable_type)

        # Create a "let" statement to introduce the loop variable into the scope.
        gen_type = iterable_type.types[-1].generic_argument_group["Gen"].value
        let_ast = AstMutation.inject_code(f"let {self.variable}: {gen_type}", Parser.parse_let_statement_uninitialized)
        let_ast.analyse_semantics(scope_manager, **kwargs)

        # Set the memory information of the symbol based on the type of iteration.
        symbols = self.variable.extract_names.map(lambda n: scope_manager.current_scope.get_symbol(n))
        for symbol in symbols:
            symbol.memory_info.ast_borrowed = self if iterable_type.types[-1].value in ["GenMut", "GenRef"] else None
            symbol.memory_info.is_borrow_mut = iterable_type.types[-1].value == "GenMut"
            symbol.memory_info.is_borrow_ref = iterable_type.types[-1].value == "GenRef"
            symbol.memory_info.initialized_by(self)


__all__ = ["LoopConditionIterableAst"]
