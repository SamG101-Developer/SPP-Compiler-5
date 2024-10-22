from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.StatementAst import StatementAst
    from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.LoopExpressionConditionAst import LoopExpressionConditionAst
    from SPPCompiler.SemanticAnalysis.WhileElseExpressionAst import WhileElseExpressionAst
    from SPPCompiler.SemanticAnalysis.InnerScopeAst import InnerScopeAst


@dataclass
class LoopExpressionAst(Ast):
    tok_loop: TokenAst
    condition: LoopExpressionConditionAst
    body: InnerScopeAst[StatementAst]
    else_block: Optional[WhileElseExpressionAst]

    _loop_type_info: dict = field(default_factory=dict, init=False, repr=False)
    _loop_type_index: int = field(default=0, init=False, repr=False)


__all__ = ["LoopExpressionAst"]
