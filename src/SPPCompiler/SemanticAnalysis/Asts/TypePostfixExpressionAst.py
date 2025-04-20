from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Dict, TYPE_CHECKING, Self, Tuple

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import AstPrinter, ast_printer_method
from SPPCompiler.SemanticAnalysis.AstUtils.AstTypeUtils import AstTypeUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope


@dataclass
class TypePostfixExpressionAst(Asts.Ast, Asts.Mixins.AbstractTypeAst, Asts.Mixins.TypeInferrable):
    lhs: Asts.TypeAst = field(default=None)
    op: Asts.TypePostfixOperatorAst = field(default=None)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        return f"{self.lhs}{self.op}"

    @property
    def pos_end(self) -> int:
        return self.op.pos_end

    def analyse_semantics(self, sm: ScopeManager, type_scope: Optional[Scope] = None, generic_infer_source: Optional[Dict] = None, generic_infer_target: Optional[Dict] = None, **kwargs) -> None:
        self.lhs.analyse_semantics(sm, type_scope=type_scope, generic_infer_source=generic_infer_source, generic_infer_target=generic_infer_target, **kwargs)
        lhs_type = self.lhs.infer_type(sm, **kwargs)
        lhs_type_symbol = sm.current_scope.get_symbol(lhs_type)
        lhs_type_scope = lhs_type_symbol.scope

        self.op.name.analyse_semantics(sm, type_scope=lhs_type_scope, generic_infer_source=generic_infer_source, generic_infer_target=generic_infer_target, **kwargs)

    def convert(self) -> Asts.TypeAst:
        if isinstance(self.op, Asts.TypePostfixOperatorOptionalTypeAst):
            return CommonTypes.Opt(self.pos, self.lhs.convert())
        return self

    def type_parts(self) -> Seq[Asts.GenericIdentifierAst]:
        if isinstance(self.op, Asts.TypePostfixOperatorOptionalTypeAst):
            return CommonTypes.Opt(self.pos, self.lhs).type_parts()
        return self.lhs.type_parts() + self.op.type_parts()

    def fq_type_parts(self) -> Seq[Asts.IdentifierAst | Asts.GenericIdentifierAst | Asts.TokenAst]:
        if isinstance(self.op, Asts.TypePostfixOperatorOptionalTypeAst):
            return CommonTypes.Opt(self.pos, self.lhs).fq_type_parts()
        return self.lhs.fq_type_parts() + self.op.fq_type_parts()

    def without_generics(self) -> Self:
        return Asts.TypePostfixExpressionAst(pos=self.pos, lhs=self.lhs, op=Asts.TypePostfixOperatorNestedTypeAst(pos=self.pos, name=self.op.name.without_generics()))

    def sub_generics(self, generic_arguments: Seq[Asts.GenericArgumentAst]) -> Asts.TypeAst:
        return Asts.TypePostfixExpressionAst(pos=self.pos, lhs=self.lhs.sub_generics(generic_arguments), op=Asts.TypePostfixOperatorNestedTypeAst(pos=self.pos, name=self.op.name.sub_generics(generic_arguments)))

    def get_generic(self, generic_name: Asts.TypeSingleAst) -> Optional[Asts.TypeAst]:
        return self.op.name.get_generic(generic_name)

    def get_generic_parameter_for_argument(self, argument: Asts.TypeAst) -> Optional[Asts.TypeAst]:
        return self.op.name.get_generic_parameter_for_argument(argument)

    def contains_generic(self, generic_name: Asts.TypeSingleAst) -> bool:
        return self.op.name.contains_generic(generic_name)

    def symbolic_eq(
            self, that: Asts.TypeAst, self_scope: Scope, that_scope: Optional[Scope] = None, check_variant: bool = True,
            debug: bool = False) -> bool:
        self_scope = self_scope.get_symbol(self.lhs.infer_type(ScopeManager(self_scope, self_scope))).scope
        return self.lhs.symbolic_eq(that, self_scope, that_scope, check_variant, debug)

    def split_to_scope_and_type(self, scope: Scope) -> Tuple[Scope, Asts.TypeSingleAst]:
        raise NotImplementedError()

    def get_convention(self) -> Optional[Asts.ConventionAst]:
        return None

    def without_conventions(self) -> Asts.TypeAst:
        return self

    def infer_type(self, sm: ScopeManager, **kwargs) -> Asts.TypeAst:
        self.lhs.analyse_semantics(sm, **kwargs)
        lhs_type = self.lhs.infer_type(sm, **kwargs)
        lhs_type_symbol = sm.current_scope.get_symbol(lhs_type)
        lhs_type_scope = lhs_type_symbol.scope

        part = AstTypeUtils.get_type_part_symbol_with_error(lhs_type_scope, sm, self.op.name.name, ignore_alias=True).fq_name
        symbol = lhs_type_scope.get_symbol(part)
        return symbol.fq_name


__all__ = [
    "TypePostfixExpressionAst"]
