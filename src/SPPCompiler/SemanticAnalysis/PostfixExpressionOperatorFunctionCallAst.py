from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.FunctionCallArgumentGroupAst import FunctionCallArgumentGroupAst
    from SPPCompiler.SemanticAnalysis.FunctionPrototypeAst import FunctionPrototypeAst
    from SPPCompiler.SemanticAnalysis.GenericArgumentGroupAst import GenericArgumentGroupAst
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst


@dataclass
class PostfixExpressionOperatorFunctionCallAst(Ast):
    generic_argument_group: GenericArgumentGroupAst
    function_argument_group: FunctionCallArgumentGroupAst
    fold_token: Optional[TokenAst]

    _overload: Optional[Tuple[FunctionPrototypeAst, FunctionCallArgumentGroupAst, Scope]] = field(default=None, init=False, repr=False)
    _is_async: Optional[Ast] = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        from SPPCompiler.SemanticAnalysis import FunctionCallArgumentGroupAst, GenericArgumentGroupAst
        self.generic_argument_group = self.generic_argument_group or GenericArgumentGroupAst.default()
        self.function_argument_group = self.function_argument_group or FunctionCallArgumentGroupAst.default()


__all__ = ["PostfixExpressionOperatorFunctionCallAst"]
