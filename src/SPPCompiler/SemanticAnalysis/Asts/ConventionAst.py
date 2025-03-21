from __future__ import annotations

from typing import Union

from SPPCompiler.SemanticAnalysis import Asts

ConventionAst = Union[
    Asts.ConventionMovAst,
    Asts.ConventionMutAst,
    Asts.ConventionRefAst]

__all__ = [
    "ConventionAst"]
