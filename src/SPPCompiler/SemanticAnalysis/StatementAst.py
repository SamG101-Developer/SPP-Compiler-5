from typing import Union

from SPPCompiler.SemanticAnalysis.AssignmentStatementAst import AssignmentStatementAst
from SPPCompiler.SemanticAnalysis.ExpressionAst import ExpressionAst
from SPPCompiler.SemanticAnalysis.LetStatementAst import LetStatementAst
from SPPCompiler.SemanticAnalysis.LoopControlFlowStatementAst import LoopControlFlowStatementAst
from SPPCompiler.SemanticAnalysis.PinStatementAst import PinStatementAst
from SPPCompiler.SemanticAnalysis.RelStatementAst import RelStatementAst
from SPPCompiler.SemanticAnalysis.RetStatementAst import RetStatementAst
from SPPCompiler.SemanticAnalysis.UseStatementAst import UseStatementAst

StatementAst = Union[
    AssignmentStatementAst,
    ExpressionAst,
    LetStatementAst,
    LoopControlFlowStatementAst,
    PinStatementAst,
    RelStatementAst,
    RetStatementAst,
    UseStatementAst]

__all__ = ["StatementAst"]
