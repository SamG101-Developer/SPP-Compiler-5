from typing import Union

import SPPCompiler.SemanticAnalysis as Asts

type ConventionAst = Union[
    Asts.ConventionMovAst,
    Asts.ConventionMutAst,
    Asts.ConventionRefAst]

__all__ = ["ConventionAst"]
