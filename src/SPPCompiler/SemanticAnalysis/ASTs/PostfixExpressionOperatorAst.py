from typing import Union

import SPPCompiler.SemanticAnalysis as Asts

PostfixExpressionOperatorAst = Union[
    Asts.PostfixExpressionOperatorEarlyReturnAst,
    Asts.PostfixExpressionOperatorFunctionCallAst,
    Asts.PostfixExpressionOperatorMemberAccessAst,
    Asts.PostfixExpressionOperatorNotKeywordAst,
    Asts.PostfixExpressionOperatorStepKeywordAst
]

__all__ = ["PostfixExpressionOperatorAst"]
