from typing import List, Tuple

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Mixins.Ordered import Ordered
from SPPCompiler.Utils.Sequence import Seq

_PARAM_ORDERING = ["Self", "Required", "Optional", "Variadic"]
_ARGUMENT_ORDERING = ["Unnamed", "Named"]


class AstOrdering:
    """!
    The ASTOrdering class contains utility function pertaining to the ordering of arguments and parameters in ASTs.
    Because ordering checks are required in multiple places, they are consolidated here.
    """

    @staticmethod
    def order(ordering: List[str], current: Seq[Ordered]) -> Seq[Tuple[str, Ast]]:
        """!
        Order the arguments in the AST by the ordering defined in the "ordering" parameter. This re-arranges ASTs in the
        sequence by sorting the values by their "_variant" attribute, which is one of the _ARGUMENT_ORDERING or
        _PARAM_ORDERING values. The order of the arguments in their respective groups is preserved.

        @param ordering The ordering to use for the ASTs.
        @param current The current ASTs in the sequence.
        @return A new, ordered sequence of ASTs. The ASTs themselves are not copied, but a new sequence is created.
        """
        current = current.map_attr("_variant").zip(current)
        ordered = current.sort(key=lambda x: ordering.index(x[0]))
        return current.ordered_difference(ordered)

    @staticmethod
    def order_args(current: Seq[Ordered]) -> Seq[Tuple[str, Ast]]:
        """!
        Order the arguments in the AST by the ordering defined in _ARGUMENT_ORDERING. This ensures that unnamed
        arguments come first, and are followed by the named arguments. The order of the arguments in their respective
        groups is preserved. This function is used to ensure the ordering of function call arguments, and generic
        arguments used in a range of places.

        @param current The current arguments in the AST.
        @return A new, ordered sequence of arguments.

        """

        # Call the order function with the argument ordering.
        return AstOrdering.order(_ARGUMENT_ORDERING, current)

    @staticmethod
    def order_params(current: Seq[Ordered]) -> Seq[Tuple[str, Ast]]:
        """
        Order the parameters in the AST by the ordering defined in _PARAM_ORDERING. This ensures that the parameters
        are ordered by their type, with the self parameter first, followed by the required parameters, then the optional
        parameters, and finally the variadic parameters. The order of the parameters in their respective groups is
        preserved. This function is used to ensure the ordering of function parameters, and generic parameters used in
        a range of places.

        @param current The current parameters in the AST.
        @return A new, ordered sequence of parameters.
        """

        # Call the order function with the parameter ordering.
        return AstOrdering.order(_PARAM_ORDERING, current)


__all__ = ["AstOrdering"]
