from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstMemoryUtils import AstMemoryUtils
from SPPCompiler.SemanticAnalysis.AstUtils.AstTypeUtils import AstTypeUtils
from SPPCompiler.SemanticAnalysis.Asts.Mixins.VisibilityEnabledAst import Visibility
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Scoping.Symbols import VariableSymbol
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors


@dataclass(slots=True, repr=False)
class GenericCompParameterOptionalAst(Asts.Ast, Asts.Mixins.OrderableAst):
    kw_cmp: Asts.TokenAst = field(default=None)
    name: Asts.TypeAst = field(default=None)
    tok_colon: Asts.TokenAst = field(default=None)
    type: Asts.TypeAst = field(default=None)
    tok_assign: Asts.TokenAst = field(default=None)
    default: Asts.ExpressionAst = field(default=None)

    def __post_init__(self) -> None:
        self.kw_cmp = self.kw_cmp or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.KwCmp)
        self.tok_colon = self.tok_colon or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkColon)
        self.tok_assign = self.tok_assign or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkAssign)
        self._variant = "Optional"

    def __eq__(self, other: GenericCompParameterOptionalAst) -> bool:
        return type(other) is GenericCompParameterOptionalAst and self.name == other.name

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.kw_cmp.print(printer) + " ",
            self.name.print(printer),
            self.tok_colon.print(printer) + " ",
            self.type.print(printer) + " ",
            self.tok_assign.print(printer) + " ",
            self.default.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.default.pos_end

    def generate_top_level_scopes(self, sm: ScopeManager) -> None:
        # Ensure the type does not have a convention.
        if c := self.type.convention:
            raise SemanticErrors.InvalidConventionLocationError().add(
                c, self.type, "comp generic parameter type").scopes(sm.current_scope)

        # Create a variable symbol for this constant in the current scope (class / function).
        symbol = VariableSymbol(
            name=Asts.IdentifierAst.from_type(self.name),
            type=self.type, visibility=Visibility.Public, is_generic=True)
        symbol.memory_info.ast_pins.append(self.name)
        symbol.memory_info.ast_comptime_const = self
        symbol.memory_info.initialized_by(self)
        sm.current_scope.add_symbol(symbol)

    def qualify_types(self, sm: ScopeManager, **kwargs) -> None:
        self.type.analyse_semantics(sm, **kwargs)
        self.type = sm.current_scope.get_symbol(self.type).fq_name

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # Analyse the type of the default expression.
        self.type.analyse_semantics(sm, **kwargs)
        self.default.analyse_semantics(sm, **kwargs)

        # Make sure the default expression is of the correct type.
        default_type = self.default.infer_type(sm, **kwargs)
        target_type = self.type
        if not AstTypeUtils.symbolic_eq(target_type, default_type, sm.current_scope, sm.current_scope):
            raise SemanticErrors.TypeMismatchError().add(
                self.name, target_type, self.default, default_type).scopes(sm.current_scope)

        # Create the variable for the const parameter.
        var = Asts.LocalVariableSingleIdentifierAst(pos=self.name.pos, name=Asts.IdentifierAst.from_type(self.name))
        ast = Asts.LetStatementUninitializedAst(pos=self.pos, assign_to=var, type=self.type)
        ast.analyse_semantics(sm, explicit_type=self.type, **kwargs)

        # Mark the symbol as initialized.
        symbol = sm.current_scope.get_symbol(Asts.IdentifierAst.from_type(self.name))
        symbol.memory_info.initialized_by(self)

    def check_memory(self, sm: ScopeManager, **kwargs) -> None:
        """
        Check the memory integrity of the default. Comptime constants don't have nested checks as they are a subset of
        possible expressions, and none of these values have deeper ASTs that would require extra analysis.

        :param sm: The scope manager.
        :param kwargs: Additional keyword arguments.
        """

        AstMemoryUtils.enforce_memory_integrity(
            self.default, self.default, sm, check_move=True, check_partial_move=True, check_move_from_borrowed_ctx=True,
            check_pins=True, check_pins_linked=True, mark_moves=True, **kwargs)


__all__ = [
    "GenericCompParameterOptionalAst"]
