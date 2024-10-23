from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.IdentifierAst import IdentifierAst


@dataclass
class ObjectInitializerArgumentUnnamedAst(Ast):
    name: IdentifierAst


__all__ = ["ObjectInitializerArgumentUnnamedAst"]
