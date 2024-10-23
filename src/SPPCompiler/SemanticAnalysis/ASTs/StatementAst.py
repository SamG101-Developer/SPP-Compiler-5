from typing import Union

from SPPCompiler.SemanticAnalysis.ASTs.AssignmentStatementAst import AssignmentStatementAst
from SPPCompiler.SemanticAnalysis.ASTs.ExpressionAst import ExpressionAst
from SPPCompiler.SemanticAnalysis.ASTs.LetStatementAst import LetStatementAst
from SPPCompiler.SemanticAnalysis.ASTs.LoopControlFlowStatementAst import LoopControlFlowStatementAst
from SPPCompiler.SemanticAnalysis.ASTs.PinStatementAst import PinStatementAst
from SPPCompiler.SemanticAnalysis.ASTs.RelStatementAst import RelStatementAst
from SPPCompiler.SemanticAnalysis.ASTs.RetStatementAst import RetStatementAst
from SPPCompiler.SemanticAnalysis.ASTs.UseStatementAst import UseStatementAst

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
