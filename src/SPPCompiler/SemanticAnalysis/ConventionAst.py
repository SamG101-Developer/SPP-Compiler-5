from typing import Union

from SPPCompiler.SemanticAnalysis.ConventionMovAst import ConventionMovAst
from SPPCompiler.SemanticAnalysis.ConventionMutAst import ConventionMutAst
from SPPCompiler.SemanticAnalysis.ConventionRefAst import ConventionRefAst

type ConventionAst = Union[
    ConventionMovAst,
    ConventionMutAst,
    ConventionRefAst]

__all__ = ["ConventionAst"]
