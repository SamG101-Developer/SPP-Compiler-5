from typing import Union

import SPPCompiler.SemanticAnalysis as Asts

LocalVariableAst = Union[
    Asts.LocalVariableDestructureArrayAst,
    Asts.LocalVariableDestructureTupleAst,
    Asts.LocalVariableDestructureObjectAst,
    Asts.LocalVariableSingleIdentifierAst]

LocalVariableNestedForDestructureArrayAst = Union[
    Asts.LocalVariableDestructureArrayAst,
    Asts.LocalVariableDestructureTupleAst,
    Asts.LocalVariableDestructureObjectAst,
    Asts.LocalVariableDestructureSkip1ArgumentAst,
    Asts.LocalVariableDestructureSkipNArgumentsAst,
    Asts.LocalVariableSingleIdentifierAst]

LocalVariableNestedForDestructureTupleAst = Union[
    Asts.LocalVariableDestructureArrayAst,
    Asts.LocalVariableDestructureTupleAst,
    Asts.LocalVariableDestructureObjectAst,
    Asts.LocalVariableDestructureSkip1ArgumentAst,
    Asts.LocalVariableDestructureSkipNArgumentsAst,
    Asts.LocalVariableSingleIdentifierAst]

LocalVariableNestedForDestructureObjectAst = Union[
    Asts.LocalVariableAttributeBindingAst,
    Asts.LocalVariableDestructureSkipNArgumentsAst,
    Asts.LocalVariableSingleIdentifierAst]

LocalVariableNestedForAttributeBindingAst = Union[
    Asts.LocalVariableDestructureArrayAst,
    Asts.LocalVariableDestructureTupleAst,
    Asts.LocalVariableDestructureObjectAst,
    Asts.LocalVariableSingleIdentifierAst]

__all__ = [
    "LocalVariableAst",
    "LocalVariableNestedForDestructureArrayAst",
    "LocalVariableNestedForDestructureTupleAst",
    "LocalVariableNestedForDestructureObjectAst",
    "LocalVariableNestedForAttributeBindingAst"]
