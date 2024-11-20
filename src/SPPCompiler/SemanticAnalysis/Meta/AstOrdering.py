from typing import List, Tuple

from SPPCompiler.Utils.Sequence import Seq
from SPPCompiler.SemanticAnalysis.Mixins.Ordered import Ordered
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

_PARAM_ORDERING = ["Self", "Required", "Optional", "Variadic"]
_ARGUMENT_ORDERING = ["Unnamed", "Named"]


class AstOrdering:
    @staticmethod
    def order(ordering: List[str], current: Seq[Ordered]) -> Seq[Tuple[str, Ast]]:
        current = current.map_attr("_variant").zip(current)
        ordered = current.sort(key=lambda x: ordering.index(x[0]))
        return current.ordered_difference(ordered)

    @staticmethod
    def order_args(current: Seq[Ordered]) -> Seq[Tuple[str, Ast]]:
        return AstOrdering.order(_ARGUMENT_ORDERING, current)

    @staticmethod
    def order_params(current: Seq[Ordered]) -> Seq[Tuple[str, Ast]]:
        return AstOrdering.order(_PARAM_ORDERING, current)


__all__ = ["AstOrdering"]
