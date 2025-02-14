from __future__ import annotations

from dataclasses import dataclass, field
from typing import Self, Optional, Dict, Tuple

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable, InferredTypeInfo
from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class TypeUnaryExpressionAst(Asts.TypeAbstractAst, TypeInferrable):
    op: Asts.TypeUnaryOperatorAst = field(default=None)
    rhs: Asts.TypeAst = field(default=None)

    def __eq__(self, other: TypeUnaryExpressionAst) -> bool:
        return isinstance(other, TypeUnaryExpressionAst) and self.op == other.op and self.rhs == other.rhs

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        return f"{self.op}{self.rhs}"

    def fq_type_parts(self) -> Seq[Asts.IdentifierAst | Asts.GenericIdentifierAst | Asts.TokenAst]:
        if isinstance(self.op, Asts.TypeUnaryOperatorNamespaceAst):
            return self.op.fq_type_parts() + self.rhs.fq_type_parts()
        return self.rhs.fq_type_parts()

    def type_parts(self) -> Seq[Asts.GenericIdentifierAst]:
        return self.rhs.type_parts()

    def analyse_semantics(self, scope_manager: ScopeManager, type_scope: Optional[Scope] = None, generic_infer_source: Optional[Dict] = None, generic_infer_target: Optional[Dict] = None, **kwargs) -> None:
        if isinstance(self.op, Asts.TypeUnaryOperatorNamespaceAst):
            type_scope = (type_scope or scope_manager.current_scope).get_symbol(self.op.name).scope
        self.rhs.analyse_semantics(scope_manager, type_scope=type_scope, generic_infer_source=generic_infer_source, generic_infer_target=generic_infer_target, **kwargs)

    def sub_generics(self, generic_arguments: Seq[Asts.GenericArgumentAst]) -> Self:
        self.rhs = self.rhs.sub_generics(generic_arguments)
        return self

    def symbolic_eq(self, that: Asts.TypeAst, self_scope: Scope, that_scope: Optional[Scope] = None) -> bool:
        if isinstance(self.op, Asts.TypeUnaryOperatorNamespaceAst):
            self_scope = self_scope.get_symbol(self.op.name).scope
        return self.rhs.symbolic_eq(that, self_scope, that_scope)

    def without_generics(self) -> Self:
        return TypeUnaryExpressionAst(self.pos, self.op, self.rhs.without_generics())

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredTypeInfo:
        return InferredTypeInfo(self)

    def split_to_scope_and_type(self, scope: Scope) -> Tuple[Scope, Asts.TypeSingleAst]:
        if isinstance(self.op, Asts.TypeUnaryOperatorNamespaceAst):
            scope = scope.get_symbol(self.op.name).scope
        return self.rhs.split_to_scope_and_type(scope)


__all__ = ["TypeUnaryExpressionAst"]
