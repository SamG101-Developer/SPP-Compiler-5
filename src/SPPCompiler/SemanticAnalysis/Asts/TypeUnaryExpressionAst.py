from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterator, Optional, TYPE_CHECKING

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstTypeUtils import AstTypeUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Scoping.Symbols import TypeSymbol
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import AstPrinter, ast_printer_method
from SPPCompiler.Utils.FastDeepcopy import fast_deepcopy
from SPPCompiler.Utils.FunctionCache import FunctionCache

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope


@dataclass(slots=True)
class TypeUnaryExpressionAst(Asts.Ast, Asts.Mixins.AbstractTypeAst, Asts.Mixins.TypeInferrable):
    op: Asts.TypeUnaryOperatorAst = field(default=None)
    rhs: Asts.TypeAst = field(default=None)

    def __eq__(self, other: TypeUnaryExpressionAst) -> bool:
        return type(other) is TypeUnaryExpressionAst and type(self.op) is type(other.op) and self.op == other.op and self.rhs == other.rhs

    def __hash__(self) -> int:
        return hash((self.op, self.rhs))

    def __iter__(self) -> Iterator[Asts.GenericIdentifierAst]:
        yield from self.rhs

    def __deepcopy__(self, memodict=None) -> TypeUnaryExpressionAst:
        # Create a deep copy of the AST.
        return TypeUnaryExpressionAst(pos=self.pos, op=self.op, rhs=fast_deepcopy(self.rhs))

    def __json__(self) -> str:
        return str(self.op) + self.rhs.__json__()

    def __str__(self) -> str:
        return f"{self.op}{self.rhs}"

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        return f"{self.op.print(printer)}{self.rhs.print(printer)}"

    @property
    def fq_type_parts(self) -> list[Asts.IdentifierAst | Asts.GenericIdentifierAst | Asts.TokenAst]:
        return self.op.fq_type_parts + self.rhs.fq_type_parts if type(self.op) is Asts.TypeUnaryOperatorNamespaceAst else self.rhs.fq_type_parts

    @FunctionCache.cache_property
    def without_generics(self) -> Optional[Asts.TypeAst]:
        return TypeUnaryExpressionAst(self.pos, self.op, self.rhs.without_generics)

    @property
    def without_conventions(self) -> Optional[Asts.TypeAst]:
        return self if type(self.op) is Asts.TypeUnaryOperatorNamespaceAst else self.rhs.without_conventions

    @property
    def convention(self) -> Optional[Asts.TypeAst]:
        return self.op.convention if isinstance(self.op, Asts.TypeUnaryOperatorBorrowAst) else None

    @property
    def pos_end(self) -> int:
        return self.rhs.pos_end

    def convert(self) -> Asts.TypeAst:
        return self

    def qualify_types(self, sm: ScopeManager, **kwargs) -> None:
        self.rhs.qualify_types(sm, **kwargs)

    def analyse_semantics(self, sm: ScopeManager, type_scope: Optional[Scope] = None, generic_infer_source: Optional[dict] = None, generic_infer_target: Optional[dict] = None, **kwargs) -> None:
        if isinstance(self.op, Asts.TypeUnaryOperatorNamespaceAst):
            temp_manager = ScopeManager(sm.global_scope, type_scope or sm.current_scope)
            type_scope = AstTypeUtils.get_namespaced_scope_with_error(temp_manager, [self.op.name])
        self.rhs.analyse_semantics(sm, type_scope=type_scope, generic_infer_source=generic_infer_source, generic_infer_target=generic_infer_target, **kwargs)

    def substituted_generics(self, generic_arguments: list[Asts.GenericArgumentAst]) -> Asts.TypeAst:
        x = self.rhs.substituted_generics(generic_arguments)
        if isinstance(x, Asts.TypeUnaryExpressionAst) and isinstance(x.op, Asts.TypeUnaryOperatorBorrowAst):
            return x
        return TypeUnaryExpressionAst(self.pos, self.op, x)

    def get_corresponding_generic(self, that: Asts.TypeAst, generic_name: Asts.TypeSingleAst) -> Optional[Asts.TypeAst]:
        return self.rhs.get_corresponding_generic(that, generic_name)

    def contains_generic(self, generic_type: Asts.TypeSingleAst) -> bool:
        return self.rhs.contains_generic(generic_type)

    def get_symbol(self, scope: Scope) -> TypeSymbol:
        if isinstance(self.op, Asts.TypeUnaryOperatorNamespaceAst):
            scope = scope.get_namespace_symbol(self.op.name).scope
        return self.rhs.get_symbol(scope)

    def infer_type(self, sm: ScopeManager, type_scope: Optional[Scope] = None, **kwargs) -> Asts.TypeAst:
        type_scope  = type_scope or sm.current_scope
        type_symbol = type_scope.get_symbol(self)
        return type_symbol.fq_name.with_convention(self.convention)


__all__ = ["TypeUnaryExpressionAst"]
