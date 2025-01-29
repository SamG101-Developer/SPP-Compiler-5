from typing import Union

import SPPCompiler.SemanticAnalysis as Asts

type LocalVariableAst = Union[
    Asts.LocalVariableDestructureArrayAst,
    Asts.LocalVariableDestructureTupleAst,
    Asts.LocalVariableDestructureObjectAst,
    Asts.LocalVariableSingleIdentifierAst]

type LocalVariableNestedForDestructureArrayAst = Union[
    Asts.LocalVariableDestructureArrayAst,
    Asts.LocalVariableDestructureTupleAst,
    Asts.LocalVariableDestructureObjectAst,
    Asts.LocalVariableDestructureSkip1ArgumentAst,
    Asts.LocalVariableDestructureSkipNArgumentsAst,
    Asts.LocalVariableSingleIdentifierAst]

type LocalVariableNestedForDestructureTupleAst = Union[
    Asts.LocalVariableDestructureArrayAst,
    Asts.LocalVariableDestructureTupleAst,
    Asts.LocalVariableDestructureObjectAst,
    Asts.LocalVariableDestructureSkip1ArgumentAst,
    Asts.LocalVariableDestructureSkipNArgumentsAst,
    Asts.LocalVariableSingleIdentifierAst]

type LocalVariableNestedForDestructureObjectAst = Union[
    Asts.LocalVariableAttributeBindingAst,
    Asts.LocalVariableDestructureSkipNArgumentsAst,
    Asts.LocalVariableSingleIdentifierAst]

type LocalVariableNestedForAttributeBindingAst = Union[
    Asts.LocalVariableDestructureArrayAst,
    Asts.LocalVariableDestructureTupleAst,
    Asts.LocalVariableDestructureObjectAst]

__all__ = [
    "LocalVariableAst",
    "LocalVariableNestedForDestructureArrayAst",
    "LocalVariableNestedForDestructureTupleAst",
    "LocalVariableNestedForDestructureObjectAst",
    "LocalVariableNestedForAttributeBindingAst"]
