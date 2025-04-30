from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class OrderableAst:
    """!
    An OrderableAst is an AST that should be ordered inside its associated group. For example, all parameter and
    argument ASTs are OrderableAsts, because in a function parameter grop, required parameters should precede optional
    parameters, and in a function call, unnamed arguments should precede named arguments.

    The variant the AST represents is stored in the "_variant" attribute, which is used to order the ASTs in the group.
    """

    _variant: str = field(init=False, repr=False)


__all__ = [
    "OrderableAst"]
