from __future__ import annotations

from dataclasses import dataclass, field
from typing import Self, Optional, Dict, Tuple, Iterator, TYPE_CHECKING

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstTypeUtils import AstTypeUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypesPrecompiled
from SPPCompiler.Utils.FastDeepcopy import fast_deepcopy
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope


@dataclass(slots=True)
class TypeUnaryExpressionAst(Asts.Ast, Asts.Mixins.AbstractTypeAst, Asts.Mixins.TypeInferrable):
    op: Asts.TypeUnaryOperatorAst = field(default=None)
    rhs: Asts.TypeAst = field(default=None)

    def __eq__(self, other: TypeUnaryExpressionAst) -> bool:
        return other.__class__ is TypeUnaryExpressionAst and type(self.op) is type(other.op) and self.op == other.op and self.rhs == other.rhs

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
    def pos_end(self) -> int:
        return self.rhs.pos_end

    def convert(self) -> Asts.TypeAst:
        return self

    def fq_type_parts(self) -> Seq[Asts.IdentifierAst | Asts.GenericIdentifierAst | Asts.TokenAst]:
        if self.op.__class__ is Asts.TypeUnaryOperatorNamespaceAst:
            return self.op.fq_type_parts() + self.rhs.fq_type_parts()
        return self.rhs.fq_type_parts()

    def analyse_semantics(self, sm: ScopeManager, type_scope: Optional[Scope] = None, generic_infer_source: Optional[Dict] = None, generic_infer_target: Optional[Dict] = None, **kwargs) -> None:
        if isinstance(self.op, Asts.TypeUnaryOperatorNamespaceAst):
            temp_manager = ScopeManager(sm.global_scope, type_scope or sm.current_scope)
            type_scope = AstTypeUtils.get_namespaced_scope_with_error(temp_manager, [self.op.name])
        self.rhs.analyse_semantics(sm, type_scope=type_scope, generic_infer_source=generic_infer_source, generic_infer_target=generic_infer_target, **kwargs)

    def without_generics(self) -> Self:
        return TypeUnaryExpressionAst(self.pos, self.op, self.rhs.without_generics())

    def substituted_generics(self, generic_arguments: Seq[Asts.GenericArgumentAst]) -> Asts.TypeAst:
        x = self.rhs.substituted_generics(generic_arguments)
        if isinstance(x, Asts.TypeUnaryExpressionAst) and isinstance(x.op, Asts.TypeUnaryOperatorBorrowAst):
            return x
        return TypeUnaryExpressionAst(self.pos, self.op, x)

    def get_corresponding_generic(self, that: Asts.TypeAst, generic_name: Asts.TypeSingleAst) -> Optional[Asts.TypeAst]:
        return self.rhs.get_corresponding_generic(that, generic_name)

    def contains_generic(self, generic_type: Asts.TypeSingleAst) -> bool:
        return self.rhs.contains_generic(generic_type)

    def symbolic_eq(self, that: Asts.TypeAst, self_scope: Scope, that_scope: Scope, check_variant: bool = True, debug: bool = False) -> bool:
        self_symbol = self_scope.get_symbol(self)

        if check_variant and self_symbol.fq_name.type_parts()[0].generic_argument_group.arguments and self_symbol.fq_name.without_generics().symbolic_eq(CommonTypesPrecompiled.EMPTY_VARIANT, self_scope, that_scope, check_variant=False):
            composite_types = self_symbol.name.generic_argument_group.arguments[0].value.type_parts()[0].generic_argument_group.arguments
            if any(t.value.symbolic_eq(that, self_scope, that_scope, debug=debug) for t in composite_types):
                return True

        # Convention mismatch (except for allowing "&mut" to coerce into "&")
        if type(self.get_convention()) is not type(that.get_convention()) and not (isinstance(self.get_convention(), Asts.ConventionRefAst) and isinstance(that.get_convention(), Asts.ConventionMutAst)):
            return False

        # Conventions are compatible, remove them and move in a layer.
        elif (that.__class__ is Asts.TypeUnaryExpressionAst) and (that.op.__class__ is Asts.TypeUnaryOperatorBorrowAst):
            that = that.rhs

        # Adjust the scope of this type.
        if self.op.__class__ is Asts.TypeUnaryOperatorNamespaceAst:
            self_scope = self_scope.get_namespace_symbol(self.op.name).scope

        # Test the inner layer of types against each other.
        return self.rhs.symbolic_eq(that, self_scope, that_scope, check_variant, debug)

    def split_to_scope_and_type(self, scope: Scope) -> Tuple[Scope, Asts.TypeSingleAst]:
        if isinstance(self.op, Asts.TypeUnaryOperatorNamespaceAst):
            scope = scope.get_namespace_symbol(self.op.name).scope
        return self.rhs.split_to_scope_and_type(scope)

    def get_convention(self) -> Optional[Asts.ConventionAst]:
        return self.op.convention if isinstance(self.op, Asts.TypeUnaryOperatorBorrowAst) else None

    def without_conventions(self) -> Asts.TypeAst:
        # If the type is a unary type expression with a borrow operator, then return the rhs of the expression.
        if isinstance(self.op, Asts.TypeUnaryOperatorBorrowAst):
            return self.rhs.without_conventions()

        # Otherwise, return the type as is.
        return self

    def infer_type(self, sm: ScopeManager, type_scope: Optional[Scope] = None, **kwargs) -> Asts.TypeAst:
        type_scope  = type_scope or sm.current_scope
        type_symbol = type_scope.get_symbol(self)
        return type_symbol.fq_name.with_convention(self.get_convention())


__all__ = ["TypeUnaryExpressionAst"]
