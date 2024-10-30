from typing import List
import operator

from SPPCompiler.Utils.Sequence import Seq
from SPPCompiler.SemanticAnalysis.Mixins.Ordered import Ordered
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast

_PARAM_ORDERING = ["Self", "Required", "Optional", "Variadic"]
_ARGUMENT_ORDERING = ["Unnamed", "Named"]


class AstOrdering:
    @staticmethod
    def order(ordering: List[str], current: Seq[Ordered]) -> Seq[Ast]:
        current = current.map_attr("_variant").zip(current)
        ordered = current.sort(key=lambda x: ordering.index(x[0]))
        return current.ordered_difference(ordered).map(operator.itemgetter(1))

    @staticmethod
    def order_args(current: Seq[Ordered]) -> Seq[Ast]:
        return AstOrdering.order(_ARGUMENT_ORDERING, current)

    @staticmethod
    def order_params(current: Seq[Ordered]) -> Seq[Ast]:
        return AstOrdering.order(_PARAM_ORDERING, current)


__all__ = ["AstOrdering"]
