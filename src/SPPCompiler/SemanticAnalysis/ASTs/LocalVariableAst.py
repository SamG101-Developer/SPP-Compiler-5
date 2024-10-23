from typing import Union

from SPPCompiler.SemanticAnalysis.ASTs.LocalVariableDestructureObjectAst import LocalVariableDestructureObjectAst
from SPPCompiler.SemanticAnalysis.ASTs.LocalVariableSingleIdentifierAst import LocalVariableSingleIdentifierAst
from SPPCompiler.SemanticAnalysis.ASTs.LocalVariableDestructureTupleAst import LocalVariableDestructureTupleAst
from SPPCompiler.SemanticAnalysis.ASTs.LocalVariableAttributeBindingAst import LocalVariableAttributeBindingAst
from SPPCompiler.SemanticAnalysis.ASTs.LocalVariableDestructureSkip1ArgumentAst import LocalVariableDestructureSkip1ArgumentAst
from SPPCompiler.SemanticAnalysis.ASTs.LocalVariableDestructureSkipNArgumentsAst import LocalVariableDestructureSkipNArgumentsAst

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
