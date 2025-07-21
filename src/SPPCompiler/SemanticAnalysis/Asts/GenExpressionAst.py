from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstMemoryUtils import AstMemoryUtils
from SPPCompiler.SemanticAnalysis.AstUtils.AstTypeUtils import AstTypeUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import AstPrinter, ast_printer_method
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypes, CommonTypesPrecompiled
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors


# Todo: test in lambdas
# Todo: test "cor || { ... }"


@dataclass(slots=True)
class GenExpressionAst(Asts.Ast, Asts.Mixins.TypeInferrable):
    kw_gen: Asts.TokenAst = field(default=None)
    convention: Optional[Asts.ConventionAst] = field(default=None)
    expr: Optional[Asts.ExpressionAst] = field(default=None)

    _func_ret_type: Optional[Asts.TypeAst] = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        self.kw_gen = self.kw_gen or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.KwGen)

    def __hash__(self) -> int:
        return id(self)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.kw_gen.print(printer) + " ",
            self.convention.print(printer) if self.convention else "",
            self.expr.print(printer) if self.expr else ""]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.expr.pos_end if self.expr else self.kw_gen.pos_end

    def infer_type(self, sm: ScopeManager, **kwargs) -> Asts.TypeAst:
        # The inferred type of a gen expression is the type of the value being sent back into the coroutine.
        generator_type = self._func_ret_type
        send_type = generator_type.type_parts[0].generic_argument_group["Send"].value
        return send_type

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # The ".." TokenAst, or TypeAst, cannot be used as an expression for the value.
        if isinstance(self.expr, (Asts.TokenAst, Asts.TypeAst)):
            raise SemanticErrors.ExpressionTypeInvalidError().add(
                self.expr).scopes(sm.current_scope)

        # Check the enclosing function is a coroutine and not a subroutine.
        function_flavour = kwargs["function_type"]
        if function_flavour.token_type != SppTokenType.KwCor:
            raise SemanticErrors.FunctionSubroutineContainsGenExpressionError().add(function_flavour, self.kw_gen).scopes(sm.current_scope)

        # Analyse the expression if it exists, and determine the type of the expression.
        if self.expr:

            # Handle the return type inference that may be required.
            if type(self.expr) is Asts.PostfixExpressionAst and type(self.expr.op) is Asts.PostfixExpressionOperatorFunctionCallAst:
                gen_type, yield_type, *_ = AstTypeUtils.get_generator_and_yielded_type(kwargs["function_ret_type"][0], sm, kwargs["function_ret_type"][0], "coroutine")
                kwargs |= {"inferred_return_type": yield_type}

            # Analyse the expression and infer its type.
            self.expr.analyse_semantics(sm, **kwargs)
            expression_type = self.expr.infer_type(sm, **kwargs).with_convention(self.convention)
        else:
            # No value means the Void type is the expression type.
            expression_type = CommonTypesPrecompiled.VOID

        if kwargs["function_ret_type"]:
            # If the function return type has been given (function, method) then get and store it.
            self._func_ret_type = kwargs["function_ret_type"][0]
        else:
            # If there is no function return type, then this is the first return statement for a lambda, so store the type.
            self._func_ret_type = CommonTypes.Gen(self.expr.pos, expression_type, CommonTypesPrecompiled.VOID)
            self._func_ret_type.analyse_semantics(sm, **kwargs)
            kwargs["function_ret_type"].append(self._func_ret_type)
            kwargs["function_scope"] = sm.current_scope

        # Determine the yield type of the enclosing function.
        gen_type, yield_type, is_once, is_optional, is_fallible, error_type = AstTypeUtils.get_generator_and_yielded_type(
            kwargs["function_ret_type"][0], sm, kwargs["function_ret_type"][0], "coroutine")

        # Check the expression type matches the expected type.
        direct_match = AstTypeUtils.symbolic_eq(yield_type, expression_type, kwargs["function_scope"], sm.current_scope)
        optional_match = is_optional and AstTypeUtils.symbolic_eq(CommonTypesPrecompiled.VOID, expression_type, kwargs["function_scope"], sm.current_scope)
        fallible_match = is_fallible and AstTypeUtils.symbolic_eq(error_type, expression_type, kwargs["function_scope"], sm.current_scope)

        if not (direct_match or optional_match or fallible_match):
            raise SemanticErrors.YieldedTypeMismatchError().add(
                yield_type, yield_type, expression_type, expression_type, is_optional, is_fallible, error_type).scopes(sm.current_scope)

    def check_memory(self, sm: ScopeManager, **kwargs) -> None:
        """
        Check the memory integrity of the expression. Can't use the FunctionCallArgumentGroupAst here because whilst
        some of the borrow checking is the same, there is way more in the function call that is too restrictive for a
        gen expression.
        :param sm: The scope manager.
        :param kwargs: Additional keyword arguments.
        """

        if self.expr:
            # Get the outermost part of the yield as a symbol. If the yield is non-symbolic, then there is no need
            # to track borrows to it, as it is a temporary value.
            sym = sm.current_scope.get_variable_symbol_outermost_part(self.expr)
            if not sym: return

            # Ensure the argument isn't moved or partially moved (applies to all conventions). For non-symbolic
            # arguments, nested checking is done via the argument itself.
            self.expr.check_memory(sm, **kwargs)
            AstMemoryUtils.enforce_memory_integrity(
                self.expr, self.kw_gen, sm, check_move=True, check_partial_move=True,
                check_move_from_borrowed_ctx=False, check_pins=False, check_pins_linked=False, mark_moves=False,
                **kwargs)

            if self.convention is None:
                # Don't bother rechecking the moves or partial moves, but ensure that attributes aren't being moved off
                # of a borrowed value and that pins are maintained. Mark the move or partial move of the argument.
                AstMemoryUtils.enforce_memory_integrity(
                    self.expr, self.expr, sm, check_move=False, check_partial_move=False,
                    check_move_from_borrowed_ctx=True, check_pins=True, check_pins_linked=False, mark_moves=True,
                    **kwargs)

            elif type(self.convention) is Asts.ConventionMutAst:
                # Check the argument's value is mutable.
                if not sym.is_mutable:
                    raise SemanticErrors.MutabilityInvalidMutationError().add(
                        self.expr, self.convention, sym.memory_info.ast_initialization).scopes(sm.current_scope)

            elif type(self.convention) is Asts.ConventionRefAst:
                ...


__all__ = [
    "GenExpressionAst"]
