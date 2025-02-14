from __future__ import annotations

from dataclasses import dataclass, field

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import AstPrinter, ast_printer_method
from SPPCompiler.SemanticAnalysis.Meta.AstTypeManagement import AstTypeManagement
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable, InferredTypeInfo
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class TypePostfixExpressionAst(Asts.TypeAbstractAst, TypeInferrable):
    lhs: Asts.TypeAst = field(default=None)
    op: Asts.TypePostfixOperatorAst = field(default=None)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        return f"{self.lhs}{self.op}"

    def fq_type_parts(self) -> Seq[Asts.IdentifierAst | Asts.GenericIdentifierAst | Asts.TokenAst]:
        if isinstance(self.op, Asts.TypePostfixOperatorOptionalTypeAst):
            return CommonTypes.Opt(self.lhs).fq_type_parts()
        return self.lhs.fq_type_parts() + self.op.fq_type_parts()

    def type_parts(self) -> Seq[Asts.GenericIdentifierAst]:
        if isinstance(self.op, Asts.TypePostfixOperatorOptionalTypeAst):
            return CommonTypes.Opt(self.lhs).type_parts()
        return self.lhs.type_parts() + self.op.type_parts()

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        self.lhs.analyse_semantics(scope_manager, **kwargs)
        lhs_type = self.lhs.infer_type(scope_manager, **kwargs).type
        lhs_type_symbol = scope_manager.current_scope.get_symbol(lhs_type)
        lhs_type_scope = scope_manager.get_namespaced_scope(self.lhs.namespace_parts())

        match self.op:
            case Asts.TypePostfixOperatorNestedTypeAst():
                AstTypeManagement.get_type_part_symbol_with_error(lhs_type_scope, self.op.name.name, ignore_alias=True)

            case Asts.TypePostfixOperatorIndexedTypeAst():
                AstTypeManagement.get_nth_type_of_indexable_type(int(self.op.index.token.token_metadata), lhs_type, lhs_type_scope)

            case Asts.TypePostfixOperatorOptionalTypeAst():
                optional_type = CommonTypes.Opt(lhs_type.infer_type(scope_manager, **kwargs).type)
                optional_type.analyse_semantics(scope_manager, **kwargs)

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredTypeInfo:
        self.lhs.analyse_semantics(scope_manager, **kwargs)
        lhs_type = self.lhs.infer_type(scope_manager, **kwargs).type
        lhs_type_symbol = scope_manager.current_scope.get_symbol(lhs_type)
        lhs_type_scope = scope_manager.get_namespaced_scope(self.lhs.namespace_parts())

        match self.op:
            case Asts.TypePostfixOperatorNestedTypeAst():
                return InferredTypeInfo(AstTypeManagement.get_type_part_symbol_with_error(lhs_type_scope, self.op.name.name, ignore_alias=True).fq_name)

            case Asts.TypePostfixOperatorIndexedTypeAst():
                return InferredTypeInfo(AstTypeManagement.get_nth_type_of_indexable_type(int(self.op.index.token.token_metadata), lhs_type, lhs_type_scope))

            case Asts.TypePostfixOperatorOptionalTypeAst():
                return InferredTypeInfo(CommonTypes.Opt(lhs_type.infer_type(scope_manager, **kwargs).type))

            case _:
                raise Exception("Invalid type postfix operator")


__all__ = ["TypePostfixExpressionAst"]
