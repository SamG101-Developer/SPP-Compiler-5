from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstMemoryUtils import AstMemoryUtils
from SPPCompiler.SemanticAnalysis.AstUtils.AstTypeUtils import AstTypeUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors


@dataclass(slots=True, repr=False)
class FunctionParameterOptionalAst(Asts.Ast, Asts.Mixins.OrderableAst, Asts.Mixins.VariableLikeAst):
    variable: Asts.LocalVariableAst = field(default=None)
    tok_colon: Asts.TokenAst = field(default=None)
    type: Asts.TypeAst = field(default=None)
    tok_assign: Asts.TokenAst = field(default=None)
    default: Asts.ExpressionAst = field(default=None)

    def __post_init__(self) -> None:
        self.tok_colon = self.tok_colon or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkColon)
        self.tok_assign = self.tok_assign or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkAssign)
        self._variant = "Optional"

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.variable.print(printer),
            self.tok_colon.print(printer) + " ",
            self.type.print(printer) + " ",
            self.tok_assign.print(printer) + " ",
            self.default.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.default.pos_end

    @property
    def extract_names(self) -> list[Asts.IdentifierAst]:
        return self.variable.extract_names

    @property
    def extract_name(self) -> Asts.IdentifierAst:
        return self.variable.extract_name

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # Analyse the type of the default expression.
        self.type.analyse_semantics(sm, **kwargs)
        self.type = sm.current_scope.get_symbol(self.type).fq_name.with_convention(self.type.convention)

        self.default.analyse_semantics(sm, **kwargs)

        # Make sure the default expression is of the correct type.
        default_type = self.default.infer_type(sm, **kwargs)
        if not AstTypeUtils.symbolic_eq(self.type, default_type, sm.current_scope, sm.current_scope):
            raise SemanticErrors.TypeMismatchError().add(
                self.extract_name, self.type, self.default, default_type).scopes(sm.current_scope)

        # Create the variable for the parameter.
        ast = Asts.LetStatementUninitializedAst(pos=self.variable.pos, assign_to=self.variable, type=self.type)
        ast.analyse_semantics(sm, explicit_type=self.type, **kwargs)

        # Mark the symbol as initialized.
        conv = self.type.convention
        for name in self.variable.extract_names:
            sym = sm.current_scope.get_symbol(name)
            sym.memory_info.initialized_by(self)
            sym.memory_info.ast_borrowed = conv
            sym.memory_info.is_borrow_mut = type(conv) is Asts.ConventionMutAst
            sym.memory_info.is_borrow_ref = type(conv) is Asts.ConventionRefAst

    def check_memory(self, sm: ScopeManager, **kwargs) -> None:
        """
        Check the memory integrity of the default. This is a regular expression AST, so deeper analysis may be required.
        :param sm: The scope manager.
        :param kwargs: Additional keyword arguments.
        """

        for name in self.variable.extract_names:
            sym = sm.current_scope.get_symbol(name)
            sym.memory_info.initialized_by(self)

        self.default.check_memory(sm, **kwargs)
        AstMemoryUtils.enforce_memory_integrity(
            self.default, self.default, sm, check_move=True, check_partial_move=True, check_move_from_borrowed_ctx=True,
            check_pins=True, check_pins_linked=True, mark_moves=True, **kwargs)


__all__ = [
    "FunctionParameterOptionalAst"]
