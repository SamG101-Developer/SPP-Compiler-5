from typing import Union

from SPPCompiler.SemanticAnalysis.GenericIdentifierAst import GenericIdentifierAst
from SPPCompiler.SemanticAnalysis.TokenAst import TokenAst

TypePartAst = Union[
    GenericIdentifierAst,
    TokenAst]

__all__ = ["TypePartAst"]
