from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING
import functools

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Meta.AstParameterNameExtraction import AstParameterNameExtraction
from SPPCompiler.SemanticAnalysis.MultiStage.Stage4_SemanticAnalyser import Stage4_SemanticAnalyser
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ConventionAst import ConventionAst
    from SPPCompiler.SemanticAnalysis.ASTs.IdentifierAst import IdentifierAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class FunctionParameterSelfAst(Ast, AstParameterNameExtraction, Stage4_SemanticAnalyser):
    tok_mut: Optional[TokenAst]
    convention: ConventionAst
    name: IdentifierAst
    type: TypeAst = field(default=None, init=False)
    _variant: str = field(init=False, default="Self", repr=False)

    def __post_init__(self) -> None:
        # Import the necessary classes to create default instances.
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes

        # Create defaults.
        self.type = CommonTypes.Self(self.pos)

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
        ...


__all__ = ["FunctionParameterSelfAst"]
