from __future__ import annotations

from typing import Union

from SPPCompiler.SemanticAnalysis import Asts

PostfixExpressionOperatorAst = Union[
    Asts.PostfixExpressionOperatorEarlyReturnAst,
    Asts.PostfixExpressionOperatorFunctionCallAst,
    Asts.PostfixExpressionOperatorMemberAccessAst,
    Asts.PostfixExpressionOperatorNotKeywordAst]

__all__ = [
    "PostfixExpressionOperatorAst"]
