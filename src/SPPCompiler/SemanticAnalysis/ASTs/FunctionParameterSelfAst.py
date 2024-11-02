from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING
import functools

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.Ordered import Ordered
from SPPCompiler.SemanticAnalysis.Mixins.VariableNameExtraction import VariableNameExtraction
from SPPCompiler.SemanticAnalysis.MultiStage.Stage4_SemanticAnalyser import Stage4_SemanticAnalyser
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ConventionAst import ConventionAst
    from SPPCompiler.SemanticAnalysis.ASTs.IdentifierAst import IdentifierAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class FunctionParameterSelfAst(Ast, Ordered, Stage4_SemanticAnalyser):
    tok_mut: Optional[TokenAst]
    convention: ConventionAst
    name: IdentifierAst
    type: TypeAst = field(default=None, init=False)

    def __post_init__(self) -> None:
        # Import the necessary classes to create default instances.
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes

        # Create defaults.
        self.type = CommonTypes.Self(self.pos)
        self._variant = "Self"

    def __eq__(self, other: FunctionParameterSelfAst) -> bool:
        # Check both ASTs are the same type.
        return isinstance(other, FunctionParameterSelfAst)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_mut.print(printer) + " " if self.tok_mut else "",
            self.convention.print(printer),
            self.name.print(printer)]
        return "".join(string)

    @functools.cached_property
    def extract_names(self) -> Seq[IdentifierAst]:
        return Seq([self.name])

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        from SPPCompiler.SemanticAnalysis import ConventionMutAst, ConventionRefAst
        from SPPCompiler.SemanticAnalysis import LetStatementUninitializedAst, LocalVariableSingleIdentifierAst

        # Analyse the type.
        self.type.analyse_semantics(scope_manager, **kwargs)

        # Create the variable using ASTs, because "let self: ..." will be a parse error.
        ast = LetStatementUninitializedAst.from_variable_and_type(
            variable=LocalVariableSingleIdentifierAst(-1, self.tok_mut, self.name),
            type=self.type)
        ast.analyse_semantics(scope_manager, **kwargs)
        print(ast)

        # Mark the symbol as initialized.
        symbol = scope_manager.current_scope.get_symbol(self.name)
        symbol.is_mutable = self.tok_mut is not None
        symbol.memory_info.borrow_ast = self.convention
        symbol.memory_info.is_borrow_mut = isinstance(self.convention, ConventionMutAst)
        symbol.memory_info.is_borrow_ref = isinstance(self.convention, ConventionRefAst)
        symbol.memory_info.initialized_by(self)


__all__ = ["FunctionParameterSelfAst"]
