from typing import Union

from SPPCompiler.SemanticAnalysis.LocalVariableDestructureObjectAst import LocalVariableDestructureObjectAst
from SPPCompiler.SemanticAnalysis.LocalVariableSingleIdentifierAst import LocalVariableSingleIdentifierAst
from SPPCompiler.SemanticAnalysis.LocalVariableDestructureTupleAst import LocalVariableDestructureTupleAst
from SPPCompiler.SemanticAnalysis.LocalVariableAttributeBindingAst import LocalVariableAttributeBindingAst
from SPPCompiler.SemanticAnalysis.LocalVariableDestructureSkip1ArgumentAst import LocalVariableDestructureSkip1ArgumentAst
from SPPCompiler.SemanticAnalysis.LocalVariableDestructureSkipNArgumentsAst import LocalVariableDestructureSkipNArgumentsAst

type LocalVariableAst = Union[
    LocalVariableDestructureTupleAst,
    LocalVariableDestructureObjectAst,
    LocalVariableSingleIdentifierAst]

type LocalVariableNestedForDestructureObjectAst = Union[
    LocalVariableAttributeBindingAst,
    LocalVariableDestructureSkipNArgumentsAst,
    LocalVariableSingleIdentifierAst]

type LocalVariableNestedForDestructureTupleAst = Union[
    LocalVariableDestructureObjectAst,
    LocalVariableDestructureSkip1ArgumentAst,
    LocalVariableDestructureSkipNArgumentsAst,
    LocalVariableDestructureTupleAst,
    LocalVariableSingleIdentifierAst]

type LocalVariableNestedForAttributeBindingAst = Union[
    LocalVariableDestructureTupleAst,
    LocalVariableDestructureObjectAst,
    LocalVariableSingleIdentifierAst]

__all__ = [
    "LocalVariableAst",
    "LocalVariableNestedForDestructureObjectAst",
    "LocalVariableNestedForDestructureTupleAst",
    "LocalVariableNestedForAttributeBindingAst"]
