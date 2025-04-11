from __future__ import annotations

from typing import Union

from SPPCompiler.SemanticAnalysis import Asts

StatementAst = Union[
    Asts.AssignmentStatementAst,
    Asts.ExpressionAst,
    Asts.LetStatementAst,
    Asts.LoopControlFlowStatementAst,
    Asts.RetStatementAst,
    Asts.UseStatementAst]

__all__ = [
    "StatementAst"]
