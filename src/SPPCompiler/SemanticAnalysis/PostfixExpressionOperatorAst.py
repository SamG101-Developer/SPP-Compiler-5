from typing import Union

from SPPCompiler.SemanticAnalysis.PostfixExpressionOperatorEarlyReturnAst import PostfixExpressionOperatorEarlyReturnAst
from SPPCompiler.SemanticAnalysis.PostfixExpressionOperatorFunctionCallAst import PostfixExpressionOperatorFunctionCallAst
from SPPCompiler.SemanticAnalysis.PostfixExpressionOperatorMemberAccessAst import PostfixExpressionOperatorMemberAccessAst
from SPPCompiler.SemanticAnalysis.PostfixExpressionOperatorNotKeywordAst import PostfixExpressionOperatorNotKeywordAst

type PostfixExpressionOperatorAst = Union[
    PostfixExpressionOperatorEarlyReturnAst,
    PostfixExpressionOperatorFunctionCallAst,
    PostfixExpressionOperatorMemberAccessAst,
    PostfixExpressionOperatorNotKeywordAst]

__all__ = ["PostfixExpressionOperatorAst"]
