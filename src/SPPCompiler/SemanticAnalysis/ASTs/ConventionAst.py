from typing import Union

from SPPCompiler.SemanticAnalysis.ASTs.ConventionMovAst import ConventionMovAst
from SPPCompiler.SemanticAnalysis.ASTs.ConventionMutAst import ConventionMutAst
from SPPCompiler.SemanticAnalysis.ASTs.ConventionRefAst import ConventionRefAst

type ConventionAst = Union[
    ConventionMovAst,
    ConventionMutAst,
    ConventionRefAst]

__all__ = ["ConventionAst"]
