from typing import Union

from SPPCompiler.SemanticAnalysis.ASTs.GenericIdentifierAst import GenericIdentifierAst
from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst

TypePartAst = Union[
    GenericIdentifierAst,
    TokenAst]

__all__ = ["TypePartAst"]
