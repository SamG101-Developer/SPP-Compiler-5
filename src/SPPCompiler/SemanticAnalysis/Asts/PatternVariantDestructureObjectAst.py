from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstTypeUtils import AstTypeUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Scoping.Symbols import VariableSymbol
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import AstPrinter, ast_printer_method
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors
from SPPCompiler.Utils.FastDeepcopy import fast_deepcopy
from SPPCompiler.Utils.Sequence import SequenceUtils


@dataclass(slots=True, repr=False)
class PatternVariantDestructureObjectAst(Asts.Ast, Asts.Mixins.AbstractPatternVariantAst):
    class_type: Asts.TypeAst = field(default=None)
    tok_l: Asts.TokenAst = field(default=None)
    elems: list[Asts.PatternVariantNestedForDestructureObjectAst] = field(default_factory=list)
    tok_r: Asts.TokenAst = field(default=None)

    _new_ast: Asts.LetStatementInitializedAst = field(default=None, init=False)

    def __post_init__(self) -> None:
        self.tok_l = self.tok_l or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkLeftParenthesis)
        self.tok_r = self.tok_r or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkRightParenthesis)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.class_type.print(printer),
            self.tok_l.print(printer),
            SequenceUtils.print(printer, self.elems, sep=", "),
            self.tok_r.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.tok_r.pos_end

    def convert_to_variable(self, **kwargs) -> Asts.LocalVariableDestructureObjectAst:
        # Convert the object destructuring into a local variable object destructuring.
        elems = [e.convert_to_variable(**kwargs) for e in self.elems if isinstance(e, Asts.PatternVariantNestedForDestructureObjectAst)]
        variable = Asts.LocalVariableDestructureObjectAst(self.pos, self.class_type, self.tok_l, elems, self.tok_r)
        variable._from_pattern = True
        return variable

    def analyse_semantics(self, sm: ScopeManager, cond: Asts.ExpressionAst = None, **kwargs) -> None:
        self.class_type.analyse_semantics(sm, **kwargs)
        self.class_type = sm.current_scope.get_symbol(self.class_type).fq_name

        # Get the symbol for the condition, if it exists.
        cond_sym = sm.current_scope.get_symbol(cond, sym_type=VariableSymbol)

        # Dummy let statement, to hold the condition if it is non-symbolic.
        if cond_sym is None:
            cond_type = cond.infer_type(sm, **kwargs)

            # Create a variable and let statement ast for the condition.
            var_ast = Asts.LocalVariableSingleIdentifierAst(pos=cond.pos, name=Asts.IdentifierAst(self.pos, f"$_{id(self)}"))
            let_ast = Asts.LetStatementUninitializedAst(pos=cond.pos, assign_to=var_ast, type=cond_type)
            let_ast.analyse_semantics(sm, explicit_type=cond_type, **kwargs)

            # Set the memory information of the symbol based on the type of iteration.
            cond = var_ast.name
            cond_sym = sm.current_scope.get_symbol(cond)
            cond_sym.memory_info.initialized_by(self)

        # Flow type the condition symbol if necessary.
        is_cond_type_variant = AstTypeUtils.is_type_variant(cond_sym.type, sm.current_scope)

        if is_cond_type_variant:
            if not AstTypeUtils.symbolic_eq(cond_sym.type, self.class_type, sm.current_scope, sm.current_scope):
                raise SemanticErrors.TypeMismatchError().add(
                    cond, cond_sym.type, self.class_type, self.class_type).scopes(sm.current_scope)

            flow_symbol = fast_deepcopy(cond_sym)
            flow_symbol.type = self.class_type
            sm.current_scope.add_symbol(flow_symbol)

        # Create the new variables from the pattern in the patterns scope.
        variable = self.convert_to_variable(**kwargs)
        self._new_ast = Asts.LetStatementInitializedAst(pos=variable.pos, assign_to=variable, value=cond)
        self._new_ast.analyse_semantics(sm, **kwargs)

    def check_memory(self, sm: ScopeManager, **kwargs) -> None:
        self._new_ast.check_memory(sm, **kwargs)


__all__ = [
    "PatternVariantDestructureObjectAst"]
