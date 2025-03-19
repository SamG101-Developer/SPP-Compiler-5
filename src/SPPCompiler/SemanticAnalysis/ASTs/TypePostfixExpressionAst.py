from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Dict

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import AstPrinter, ast_printer_method
from SPPCompiler.SemanticAnalysis.Meta.AstTypeManagement import AstTypeManagement
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable
from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class TypePostfixExpressionAst(Asts.TypeAbstractAst, TypeInferrable):
    lhs: Asts.TypeAst = field(default=None)
    op: Asts.TypePostfixOperatorAst = field(default=None)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        return f"{self.lhs}{self.op}"

    @property
    def pos_end(self) -> int:
        return self.op.pos_end

    def convert(self) -> Asts.TypeAst:
        if isinstance(self.op, Asts.TypePostfixOperatorOptionalTypeAst):
            return CommonTypes.Opt(self.lhs.convert())
        return self

    def fq_type_parts(self) -> Seq[Asts.IdentifierAst | Asts.GenericIdentifierAst | Asts.TokenAst]:
        if isinstance(self.op, Asts.TypePostfixOperatorOptionalTypeAst):
            return CommonTypes.Opt(self.lhs).fq_type_parts()
        return self.lhs.fq_type_parts() + self.op.fq_type_parts()

    def type_parts(self) -> Seq[Asts.GenericIdentifierAst]:
        if isinstance(self.op, Asts.TypePostfixOperatorOptionalTypeAst):
            return CommonTypes.Opt(self.lhs).type_parts()
        return self.lhs.type_parts() + self.op.type_parts()

    def get_convention(self) -> Optional[Asts.ConventionAst]:
        return self.lhs.get_convention()

    def analyse_semantics(self, scope_manager: ScopeManager, type_scope: Optional[Scope] = None, generic_infer_source: Optional[Dict] = None, generic_infer_target: Optional[Dict] = None, **kwargs) -> None:
        self.lhs.analyse_semantics(scope_manager, type_scope=type_scope, generic_infer_source=generic_infer_source, generic_infer_target=generic_infer_target, **kwargs)
        lhs_type = self.lhs.infer_type(scope_manager, **kwargs)
        lhs_type_symbol = scope_manager.current_scope.get_symbol(lhs_type)
        lhs_type_scope = lhs_type_symbol.scope

        match self.op:
            case Asts.TypePostfixOperatorNestedTypeAst():
                self.op.name.analyse_semantics(scope_manager, type_scope=lhs_type_scope, generic_infer_source=generic_infer_source, generic_infer_target=generic_infer_target, **kwargs)

            case Asts.TypePostfixOperatorIndexedTypeAst():
                AstTypeManagement.get_nth_type_of_indexable_type(int(self.op.index.token_data), lhs_type, lhs_type_scope)

            case _:
                raise Exception("Invalid type postfix operator")

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> Asts.TypeAst:
        self.lhs.analyse_semantics(scope_manager, **kwargs)
        lhs_type = self.lhs.infer_type(scope_manager, **kwargs)
        lhs_type_symbol = scope_manager.current_scope.get_symbol(lhs_type)
        lhs_type_scope = lhs_type_symbol.scope

        match self.op:
            case Asts.TypePostfixOperatorNestedTypeAst():
                part = AstTypeManagement.get_type_part_symbol_with_error(lhs_type_scope, scope_manager, self.op.name.name, ignore_alias=True).fq_name
                symbol = lhs_type_scope.get_symbol(part)
                return symbol.fq_name

            case Asts.TypePostfixOperatorIndexedTypeAst():
                return AstTypeManagement.get_nth_type_of_indexable_type(int(self.op.index.token_data), lhs_type, lhs_type_scope)

            case _:
                raise Exception("Invalid type postfix operator")


__all__ = ["TypePostfixExpressionAst"]
