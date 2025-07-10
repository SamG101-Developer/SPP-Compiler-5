from typing import List, Tuple

from type_intersections import Intersection

from SPPCompiler.SemanticAnalysis import Asts


class AstOrderingUtils:
    """!
    The ASTOrdering class contains utility function pertaining to the ordering of arguments and parameters in ASTs.
    Because ordering checks are required in multiple places, they are consolidated here.
    """

    PARAM_ORDERING = ["Self", "Required", "Optional", "Variadic"]
    ARGUMENT_ORDERING = ["Unnamed", "Named"]

    @staticmethod
    def order(ordering: List[str], current: list[Asts.Mixins.OrderableAst]) -> list[Tuple[str, Intersection[Asts.Ast, Asts.Mixins.OrderableAst]]]:
        """!
        Order the arguments in the AST by the ordering defined in the "ordering" parameter. This re-arranges ASTs in the
        sequence by sorting the values by their "_variant" attribute, which is one of the _ARGUMENT_ORDERING or
        _PARAM_ORDERING values. The order of the arguments in their respective groups is preserved.

        @param ordering The ordering to use for the ASTs.
        @param current The current ASTs in the sequence.
        @return A new, ordered sequence of ASTs. The ASTs themselves are not copied, but a new sequence is created.
        """

        current = [(c._variant, c) for c in current]
        ordered = sorted(current, key=lambda x: ordering.index(x[0]))
        return [o for c, o in zip(current, ordered) if c != o]

    @staticmethod
    def order_args(current: list[Asts.Mixins.OrderableAst]) -> list[Tuple[str, Asts.Ast]]:
        """!
        Order the arguments in the AST by the ordering defined in _ARGUMENT_ORDERING. This ensures that unnamed
        arguments come first, and are followed by the named arguments. The order of the arguments in their respective
        groups is preserved. This function is used to ensure the ordering of function call arguments, and generic
        arguments used in a range of places.

        @param current The current arguments in the AST.
        @return A new, ordered sequence of arguments.
        """

        # Call the order function with the argument ordering.
        return AstOrderingUtils.order(AstOrderingUtils.ARGUMENT_ORDERING, current)

    @staticmethod
    def order_params(current: list[Asts.Mixins.OrderableAst]) -> list[Tuple[str, Asts.Ast]]:
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
        return AstOrderingUtils.order(AstOrderingUtils.PARAM_ORDERING, current)


__all__ = [
    "AstOrderingUtils"]
