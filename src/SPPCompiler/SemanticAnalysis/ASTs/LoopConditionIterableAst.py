from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
import std

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstMutation import AstMutation
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable, InferredType
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages
from SPPCompiler.SyntacticAnalysis.Parser import SppParser
import SPPCompiler.SemanticAnalysis as Asts

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


# Todo:
#  - [1] Relax iterable type to superimpose a GenXXX type, rather than exactly match it
#  - [1] Does the generator have to be owned? pins would ensure memory safety
#  - [2] Change the '== "GenXXX"' to symbolic_eq (requires [1])


@dataclass
class LoopConditionIterableAst(Ast, TypeInferrable, CompilerStages):
    variable: Asts.LocalVariableAst = field(default=None)
    in_keyword: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.KwIn))
    iterable: Asts.ExpressionAst = field(default=None)

    def __post_init__(self) -> None:
        assert self.variable
        assert self.iterable

    @ast_printer_method
    @std.override_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.variable.print(printer),
            self.in_keyword.print(printer),
            self.iterable.print(printer)]
        return "".join(string)

    @std.override_method
    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredType:
        # Infer the type from the iterable.
        return self.iterable.infer_type(scope_manager, **kwargs)

    @std.override_method
    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes

        # The ".." TokenAst, or TypeAst, cannot be used as an expression for the value.
        if isinstance(self.iterable, (Asts.TokenAst, Asts.TypeAst)):
            raise SemanticErrors.ExpressionTypeInvalidError().add(self.iterable)

        code = f"{self.iterable}.step() is std::Some(val as {self.variable})"
        loop_condition_ast = AstMutation.inject_code(code, SppParser.parse_loop_expression_condition_boolean)
        loop_condition_ast.analyse_semantics(scope_manager, **kwargs)

        # # Analyse the iterable.
        # self.iterable.analyse_semantics(scope_manager, **kwargs)
        # AstMemoryHandler.enforce_memory_integrity(self.iterable, self.iterable, scope_manager, update_memory_info=False)
        #
        # # Check the iterable is a generator type.
        # iterable_type = self.iterable.infer_type(scope_manager, **kwargs)
        # allowed_types = Seq([CommonTypes.GenMov(), CommonTypes.GenMut(), CommonTypes.GenRef()]).map(TypeAst.without_generics).map(InferredType.from_type)
        # if not allowed_types.any(lambda t: t.symbolic_eq(iterable_type.without_generics(), scope_manager.current_scope)):
        #     raise SemanticErrors.LoopIterableInvalidTypeError().add(self.iterable, iterable_type.type)
        #
        # # Create a "let" statement to introduce the loop variable into the scope.
        # gen_type = iterable_type.type.types[-1].generic_argument_group["Gen"].value
        # let_ast = AstMutation.inject_code(f"let {self.variable}: {gen_type}", Parser.parse_let_statement_uninitialized)
        # let_ast.analyse_semantics(scope_manager, **kwargs)
        #
        # # Set the memory information of the symbol based on the type of iteration.
        # symbols = self.variable.extract_names.map(lambda n: scope_manager.current_scope.get_symbol(n))
        # for symbol in symbols:
        #     symbol.memory_info.ast_borrowed = self if iterable_type.type.types[-1].value in ["GenMut", "GenRef"] else None
        #     symbol.memory_info.is_borrow_mut = iterable_type.type.types[-1].value == "GenMut"
        #     symbol.memory_info.is_borrow_ref = iterable_type.type.types[-1].value == "GenRef"
        #     symbol.memory_info.initialized_by(self)


__all__ = ["LoopConditionIterableAst"]
