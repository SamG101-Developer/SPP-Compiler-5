from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstTypeUtils import AstTypeUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Scoping.Symbols import TypeSymbol
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import AstPrinter, ast_printer_method
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors
from SPPCompiler.Utils.FastDeepcopy import fast_deepcopy
from SPPCompiler.Utils.FunctionCache import FunctionCache

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope


@dataclass(slots=True, repr=False)
class TypePostfixExpressionAst(Asts.Ast, Asts.Mixins.AbstractTypeAst, Asts.Mixins.TypeInferrable):
    lhs: Asts.TypeAst = field(default=None)
    op: Asts.TypePostfixOperatorAst = field(default=None)

    def __deepcopy__(self, memodict=None) -> TypePostfixExpressionAst:
        # Create a deep copy of the AST.
        return TypePostfixExpressionAst(pos=self.pos, lhs=fast_deepcopy(self.lhs), op=fast_deepcopy(self.op))

    def __hash__(self) -> int:
        return hash((self.lhs, self.op))

    def __json__(self) -> str:
        return f"{self.lhs}{self.op}"

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        return f"{self.lhs}{self.op}"

    @property
    def pos_end(self) -> int:
        return self.op.pos_end

    def convert(self) -> Asts.TypeAst:
        if type(self.op) is Asts.TypePostfixOperatorOptionalTypeAst:
            return CommonTypes.Opt(self.pos, self.lhs.convert())
        return self

    def is_never_type(self) -> bool:
        return False

    @property
    def fq_type_parts(self) -> list[Asts.IdentifierAst | Asts.TypeIdentifierAst | Asts.TokenAst]:
        return CommonTypes.Opt(self.pos, self.lhs).fq_type_parts if type(self.op) is Asts.TypePostfixOperatorOptionalTypeAst else self.lhs.fq_type_parts + self.op.fq_type_parts

    @FunctionCache.cache_property
    def namespace_parts(self) -> list[Asts.IdentifierAst]:
        return self.lhs.namespace_parts + self.op.name.namespace_parts

    @FunctionCache.cache_property
    def type_parts(self) -> list[Asts.TypeIdentifierAst | Asts.TokenAst]:
        return self.lhs.type_parts + self.op.name.type_parts

    @property
    def without_convention(self) -> Optional[Asts.TypeAst]:
        return self

    @property
    def convention(self) -> Optional[Asts.ConventionAst]:
        return None

    @FunctionCache.cache_property
    def without_generics(self) -> Optional[Asts.TypeAst]:
        return Asts.TypePostfixExpressionAst(pos=self.pos, lhs=self.lhs, op=Asts.TypePostfixOperatorNestedTypeAst(pos=self.pos, name=self.op.name.without_generics))

    def substituted_generics(self, generic_arguments: list[Asts.GenericArgumentAst]) -> Asts.TypeAst:
        return Asts.TypePostfixExpressionAst(pos=self.pos, lhs=self.lhs.substituted_generics(generic_arguments), op=Asts.TypePostfixOperatorNestedTypeAst(pos=self.pos, name=self.op.name.substituted_generics(generic_arguments)))

    def match_generic(self, that: Asts.TypeAst, generic_name: Asts.TypeIdentifierAst) -> Optional[Asts.TypeAst]:
        if str(that) == str(generic_name): return self
        return self.op.name.match_generic(that, generic_name)

    def contains_generic(self, generic_type: Asts.TypeIdentifierAst) -> bool:
        return self.op.name.contains_generic(generic_type)

    def get_symbol(self, scope: Scope) -> TypeSymbol:
        self_scope = scope.get_symbol(self.lhs.infer_type(ScopeManager(scope, scope))).scope
        return self_scope.get_symbol(self.op.name)

    def analyse_semantics(self, sm: ScopeManager, type_scope: Optional[Scope] = None, generic_infer_source: Optional[dict] = None, generic_infer_target: Optional[dict] = None, **kwargs) -> None:
        self.lhs.analyse_semantics(sm, type_scope=type_scope, generic_infer_source=generic_infer_source, generic_infer_target=generic_infer_target, **kwargs)
        lhs_type = self.lhs.infer_type(sm, **kwargs)
        lhs_type_symbol = sm.current_scope.get_symbol(lhs_type)
        lhs_type_scope = lhs_type_symbol.scope

        # Check there is only 1 target field on the type at the highest level.
        if type(self.op) is Asts.TypePostfixOperatorNestedTypeAst and lhs_type_scope:
            sss = []
            for scope in [lhs_type_scope] + lhs_type_scope.sup_scopes:
                sss.append((scope, scope._symbol_table.get(self.op.name)))
            depths = [(lhs_type_scope.depth_difference(s[0]), s) for s in sss if s[1] is not None]
            closest = [s[1] for s in depths if s[0] == min(depths, key=lambda x: x[0])[0]]
            if len(closest) > 1:
                raise SemanticErrors.AmbiguousMemberAccessError().add(
                    self.op.name, closest[0][1].name, closest[1][1].name).scopes(
                    sm.current_scope, closest[0][0], closest[1][0])

        self.op.name.analyse_semantics(sm, type_scope=lhs_type_scope, generic_infer_source=generic_infer_source, generic_infer_target=generic_infer_target, **kwargs)

    def infer_type(self, sm: ScopeManager, **kwargs) -> Asts.TypeAst:
        self.lhs.analyse_semantics(sm, **kwargs)
        lhs_type = self.lhs.infer_type(sm, **kwargs)
        lhs_type_symbol = sm.current_scope.get_symbol(lhs_type)
        lhs_type_scope = lhs_type_symbol.scope

        part = AstTypeUtils.get_type_part_symbol_with_error(lhs_type_scope, sm, self.op.name, ignore_alias=True).fq_name
        symbol = lhs_type_scope.get_symbol(part)
        return symbol.fq_name


__all__ = [
    "TypePostfixExpressionAst"]
