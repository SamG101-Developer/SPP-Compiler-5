from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypes


@dataclass(slots=True)
class LambdaExpressionAst(Asts.Ast, Asts.Mixins.TypeInferrable):
    """
    The LambdaExpressionAst is an anonymous function that can be used as a value. It is a first-class function in the
    language. It can capture variables from its surrounding context and can be passed as an argument to other functions.
    Taken from Rust, the "|" character is used to denote the start and end of the lambda expression.
    """

    kw_cor: Optional[Asts.TokenAst] = field(default=None)
    """The "cor" keyword can be used to mark a lambda as a coroutine."""

    pc_group: Asts.LambdaExpressionParameterAndCaptureGroupAst = field(default=None)
    """The capture and parameter group of the lambda expression."""

    body: Asts.ExpressionAst = field(default=None)
    """The body of the lambda expression."""

    _ret_type: Asts.TypeAst = field(default=None)
    """The return type of the lambda expression. Inferred from the body."""

    def __post_init__(self) -> None:
        self.pc_group = self.pc_group or Asts.LambdaExpressionParameterAndCaptureGroupAst()

    def __hash__(self) -> int:
        return id(self)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        return "".join([
            self.kw_cor.print(printer) if self.kw_cor else "",
            self.pc_group.print(printer),
            self.body.print(printer)
        ])

    @property
    def pos_end(self) -> int:
        return self.body.pos_end

    def infer_type(self, sm: ScopeManager, **kwargs) -> Asts.TypeAst:
        """
        Use the captures to determine the type of this lambda. If there is a "move" capture for example, the lambda can
        only be called once, and therefore must be a "FunMov" type.

        :param sm: The scope manager.
        :param kwargs: Additional keyword arguments.
        :return: The type of this lambda.
        """

        captures = self.pc_group.captures

        # If there are no captures, return a "FunRef" type.
        if len(self.pc_group.captures) <= 0:
            param_types = [p.type for p in self.pc_group.params]
            ty = CommonTypes.FunRef(self.pos, CommonTypes.Tup(self.pos, param_types), self._ret_type)

        # If there are any "move" captures, return a "FunMov" type.
        elif any(c.convention is None for c in captures):
            param_types = [p.type for p in self.pc_group.params]
            ty = CommonTypes.FunMov(self.pos, CommonTypes.Tup(self.pos, param_types), self._ret_type)

        # If there are any "&mut" captures, return a "FunMut" type.
        elif any(type(c.convention) is Asts.ConventionMutAst for c in captures):
            param_types = [p.type for p in self.pc_group.params]
            ty = CommonTypes.FunMut(self.pos, CommonTypes.Tup(self.pos, param_types), self._ret_type)

        # Otherwise, all captures are "&", so return a "FunRef" type.
        else:
            param_types = [p.type for p in self.pc_group.params]
            ty = CommonTypes.FunRef(self.pos, CommonTypes.Tup(self.pos, param_types), self._ret_type)

        # Analyse the type and return it.
        ty.analyse_semantics(sm, **kwargs)
        return ty

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        """
        Analyse the parameters/captures group, and the lambda expression's body. Then set the return type of this lambda
        to the return type of the body. The scope of the lambda is exclusive to the lambda, so the parent scope is set
        as the module scope, preventing symbol search in the scope the lambda was defined in. However, it isn't set as a
        child scope to the module scope, so it doesn't mess up scope iteration at the top level.

        :param sm: The scope manager.
        :param kwargs: Additional keyword arguments.
        """

        parent_scope = sm.current_scope

        # Perform memory checks on the captures against the symbols from the outermost scope.
        caps = Asts.FunctionCallArgumentGroupAst(arguments=self.pc_group.captures)
        caps.pre_analyse_semantics(sm, **kwargs)
        caps.analyse_semantics(sm, **kwargs)

        # New scope for the parameters.
        sm.create_and_move_into_new_scope(f"<lambda-outer:{self.pos}>")
        self.pc_group.analyse_semantics(sm, **kwargs)
        kwargs["function_scope"] = sm.current_scope

        # Once the captures have been analysed, prevent access to the parent scope.
        sm.current_scope.parent = sm.current_scope.parent_module

        # New scope for the body.
        sm.create_and_move_into_new_scope(f"<lambda-inner:{self.pos}>")

        # Analyse the body of the lambda expression.
        kwargs["function_type"] = self.kw_cor or Asts.TokenAst.raw(token_type=SppTokenType.KwFun)
        kwargs["function_ret_type"] = []
        self.body.analyse_semantics(sm, **kwargs)
        final_body_type = self.body.infer_type(sm, **kwargs)
        self._ret_type = kwargs["function_ret_type"][0] if kwargs["function_ret_type"] else final_body_type

        # Move out of the inner and outer lambda scopes.
        sm._current_scope = parent_scope

        # Pin the lambda symbol if it is assigned to a variable and has borrowed captures.
        if "assignment" in kwargs and (borrowed_captures := [c for c in self.pc_group.captures if c.convention is not None]):
            for borrow in borrowed_captures:
                parent_scope._symbol_table.add_deferred_callback(kwargs["assignment"][0], lambda sym: sym.memory_info.ast_pinned.append(borrow.value))

        # Pin any values that have been borrowed as captures as borrows.
        for cap in self.pc_group.captures:
            if cap.convention is not None:
                cap_sym = sm.current_scope.get_symbol(cap.value)
                cap_sym.memory_info.ast_pinned.append(cap)
