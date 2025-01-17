from typing import Union

from SPPCompiler.SemanticAnalysis.ASTs.PostfixExpressionOperatorEarlyReturnAst import PostfixExpressionOperatorEarlyReturnAst
from SPPCompiler.SemanticAnalysis.ASTs.PostfixExpressionOperatorFunctionCallAst import PostfixExpressionOperatorFunctionCallAst
from SPPCompiler.SemanticAnalysis.ASTs.PostfixExpressionOperatorMemberAccessAst import PostfixExpressionOperatorMemberAccessAst
from SPPCompiler.SemanticAnalysis.ASTs.PostfixExpressionOperatorNotKeywordAst import PostfixExpressionOperatorNotKeywordAst

type PostfixExpressionOperatorAst = Union[
    PostfixExpressionOperatorEarlyReturnAst,
    PostfixExpressionOperatorFunctionCallAst,
    PostfixExpressionOperatorMemberAccessAst,
    PostfixExpressionOperatorNotKeywordAst]

__all__ = ["PostfixExpressionOperatorAst"]
