from __future__ import annotations

from typing import Union

from SPPCompiler.SemanticAnalysis import Asts

PostfixExpressionOperatorAst = Union[
    Asts.PostfixExpressionOperatorEarlyReturnAst,
    Asts.PostfixExpressionOperatorFunctionCallAst,
    Asts.PostfixExpressionOperatorIndexAst,
    Asts.PostfixExpressionOperatorMemberAccessAst,
    Asts.PostfixExpressionOperatorNotKeywordAst,
    Asts.PostfixExpressionOperatorResumeCoroutineAst]

__all__ = [
    "PostfixExpressionOperatorAst"]
