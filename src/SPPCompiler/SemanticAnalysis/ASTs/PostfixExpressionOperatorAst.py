from typing import Union

import SPPCompiler.SemanticAnalysis as Asts

type PostfixExpressionOperatorAst = Union[
    Asts.PostfixExpressionOperatorEarlyReturnAst,
    Asts.PostfixExpressionOperatorFunctionCallAst,
    Asts.PostfixExpressionOperatorMemberAccessAst,
    Asts.PostfixExpressionOperatorNotKeywordAst,
    Asts.PostfixExpressionOperatorStepKeywordAst
]

__all__ = ["PostfixExpressionOperatorAst"]
