from __future__ import annotations

from typing import Self, Optional, Tuple

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import AstPrinter
from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope
from SPPCompiler.Utils.Sequence import Seq


class TypeAbstractAst(Ast):
    def __json__(self):
        return self.print(AstPrinter())

    def prepend_namespace_part(self, part: Asts.IdentifierAst) -> Asts.TypeAst:
        return Asts.TypeUnaryExpressionAst(
            pos=self.pos, op=Asts.TypeUnaryOperatorNamespaceAst(pos=self.pos, name=part), rhs=self)

    def fq_type_parts(self) -> Seq[Asts.IdentifierAst | Asts.GenericIdentifierAst | Asts.TokenAst]:
        ...

    def type_parts(self) -> Seq[Asts.GenericIdentifierAst]:
        ...

    def namespace_parts(self) -> Seq[Asts.IdentifierAst]:
        return self.fq_type_parts().filter(lambda x: isinstance(x, Asts.IdentifierAst))

    def without_generics(self) -> Self:
        ...

    def sub_generics(self, generic_arguments: Seq[Asts.GenericArgumentAst]) -> Self:
        ...

    def get_generic(self, generic_name: Asts.TypeSingleAst) -> Optional[Asts.TypeAst]:
        ...

    def contains_generic(self, generic_name: Asts.TypeSingleAst) -> bool:
        ...

    def symbolic_eq(self, that: Asts.TypeAst, self_scope: Scope, that_scope: Optional[Scope] = None, check_variant: bool = True) -> bool:
        ...

    def split_to_scope_and_type(self, scope: Scope) -> Tuple[Scope, Asts.TypeSingleAst]:
        ...


__all__ = ["TypeAbstractAst"]
