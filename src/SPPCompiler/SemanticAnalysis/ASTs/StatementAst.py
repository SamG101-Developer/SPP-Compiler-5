from typing import Union

import SPPCompiler.SemanticAnalysis as Asts

StatementAst = Union[
    Asts.AssignmentStatementAst,
    Asts.ExpressionAst,
    Asts.LetStatementAst,
    Asts.LoopControlFlowStatementAst,
    Asts.PinStatementAst,
    Asts.RelStatementAst,
    Asts.RetStatementAst,
    Asts.UseStatementAst]

__all__ = ["StatementAst"]
