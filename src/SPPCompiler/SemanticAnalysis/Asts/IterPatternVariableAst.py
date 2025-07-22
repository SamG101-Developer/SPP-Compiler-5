from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import AstPrinter, ast_printer_method


@dataclass(slots=True, repr=False)
class IterPatternVariableAst(Asts.Ast, Asts.Mixins.AbstractPatternVariantAst):
    """
    Represents an iteration pattern that matches a yielded value, represented by "<identifier>". This is for when any
    generator yields a normal value.
    """

    variable: Asts.LocalVariableAst = field(default=None)
    """The local variable that the yielded value is bound to."""

    _new_ast: Asts.LetStatementInitializedAst = field(default=None, init=False)
    """The AST node that this pattern is transformed into, to create its variable."""

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        return self.variable.print(printer)

    def __str__(self) -> str:
        return str(self.variable)

    @property
    def pos_end(self) -> int:
        return self.variable.pos_end

    def convert_to_variable(self, **kwargs) -> Asts.LocalVariableAst:
        return self.variable

    def analyse_semantics(self, sm: ScopeManager, cond: Asts.ExpressionAst = None, **kwargs) -> None:
        # Create a dummy type with the same type as the variable's type, to initialize it. This has to be done, to use
        # the "Yield" type, as "cond" is the "Generated" type.
        var_type = cond.infer_type(sm, **kwargs).type_parts[-1].generic_argument_group["Yield"].value

        # Create a new AST node that initializes the variable with the dummy value.
        self._new_ast = Asts.LetStatementInitializedAst(self.pos, explicit_type=var_type, assign_to=self.variable, value=Asts.ObjectInitializerAst(pos=self.pos, class_type=var_type))
        self._new_ast.analyse_semantics(sm, **kwargs)

        # If the "Yield" type is a borrow, set the borrow flags in the memory info of the variable.
        conv = var_type.convention
        for name in self.variable.extract_names:
            sym = sm.current_scope.get_symbol(name)
            sym.memory_info.initialized_by(self.variable)

            # Apply the borrow to the symbol.
            sym.memory_info.ast_borrowed = conv
            sym.memory_info.is_borrow_mut = isinstance(conv, Asts.ConventionMutAst)
            sym.memory_info.is_borrow_ref = isinstance(conv, Asts.ConventionRefAst)

            # Apply the borrow to the type.
            sym.type = sym.type.with_convention(conv)

    def check_memory(self, sm: ScopeManager, **kwargs) -> None:
        self._new_ast.check_memory(sm, **kwargs)


__all__ = ["IterPatternVariableAst"]
