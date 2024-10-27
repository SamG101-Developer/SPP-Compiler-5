from typing import Union

from SPPCompiler.SemanticAnalysis.ASTs.ClassAttributeAst import ClassAttributeAst

type ClassMemberAst = Union[ClassAttributeAst]

__all__ = ["ClassMemberAst"]
