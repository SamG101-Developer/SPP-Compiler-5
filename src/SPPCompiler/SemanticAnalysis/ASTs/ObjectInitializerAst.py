from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ObjectInitializerArgumentGroupAst import ObjectInitializerArgumentGroupAst
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst


@dataclass
class ObjectInitializerAst(Ast):
    type: TypeAst
    object_argument_group: ObjectInitializerArgumentGroupAst


__all__ = ["ObjectInitializerAst"]
