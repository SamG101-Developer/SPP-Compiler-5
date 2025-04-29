from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.Utils.Sequence import Seq


@dataclass(slots=True)
class FunctionParameterRequiredAst(Asts.Ast, Asts.Mixins.OrderableAst, Asts.Mixins.VariableLikeAst):
    variable: Asts.LocalVariableAst = field(default=None)
    tok_colon: Asts.TokenAst = field(default=None)
    type: Asts.TypeAst = field(default=None)

    def __post_init__(self) -> None:
        self.tok_colon = self.tok_colon or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkColon)
        self.variable = self.variable or Asts.LocalVariableSingleIdentifierAst(pos=self.pos, name=Asts.IdentifierAst(pos=self.pos, value=f"$l{id(self)}"))
        self._variant = "Required"

    def __eq__(self, other: FunctionParameterRequiredAst) -> bool:
        # Check both ASTs are the same type and have the same variable.
        return isinstance(other, FunctionParameterRequiredAst) and self.variable == other.variable

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.variable.print(printer),
            self.tok_colon.print(printer) + " ",
            self.type.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.type.pos_end

    @property
    def extract_names(self) -> Seq[Asts.IdentifierAst]:
        return self.variable.extract_names

    @property
    def extract_name(self) -> Asts.IdentifierAst:
        return self.variable.extract_name

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # Analyse the type.
        self.type.analyse_semantics(sm, **kwargs)

        # Create the variable for the parameter.
        ast = Asts.LetStatementUninitializedAst(pos=self.variable.pos, assign_to=self.variable, type=self.type)
        ast.analyse_semantics(sm, **kwargs)

        # Mark the symbol as initialized.
        convention = self.type.get_convention()
        for name in self.variable.extract_names:
            symbol = sm.current_scope.get_symbol(name)
            symbol.memory_info.ast_borrowed = convention
            symbol.memory_info.is_borrow_mut = isinstance(convention, Asts.ConventionMutAst)
            symbol.memory_info.is_borrow_ref = isinstance(convention, Asts.ConventionRefAst)
            symbol.memory_info.initialized_by(self)


__all__ = [
    "FunctionParameterRequiredAst"]
