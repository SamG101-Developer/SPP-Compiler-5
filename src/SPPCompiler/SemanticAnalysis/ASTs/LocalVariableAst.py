from typing import Union

from SPPCompiler.SemanticAnalysis.ASTs.LocalVariableAttributeBindingAst import LocalVariableAttributeBindingAst
from SPPCompiler.SemanticAnalysis.ASTs.LocalVariableDestructureArrayAst import LocalVariableDestructureArrayAst
from SPPCompiler.SemanticAnalysis.ASTs.LocalVariableDestructureObjectAst import LocalVariableDestructureObjectAst
from SPPCompiler.SemanticAnalysis.ASTs.LocalVariableDestructureTupleAst import LocalVariableDestructureTupleAst
from SPPCompiler.SemanticAnalysis.ASTs.LocalVariableSingleIdentifierAst import LocalVariableSingleIdentifierAst
from SPPCompiler.SemanticAnalysis.ASTs.LocalVariableDestructureSkip1ArgumentAst import LocalVariableDestructureSkip1ArgumentAst
from SPPCompiler.SemanticAnalysis.ASTs.LocalVariableDestructureSkipNArgumentsAst import LocalVariableDestructureSkipNArgumentsAst

type LocalVariableAst = Union[
    LocalVariableDestructureArrayAst,
    LocalVariableDestructureTupleAst,
    LocalVariableDestructureObjectAst,
    LocalVariableSingleIdentifierAst]

type LocalVariableNestedForDestructureArrayAst = Union[
    LocalVariableDestructureArrayAst,
    LocalVariableDestructureTupleAst,
    LocalVariableDestructureObjectAst,
    LocalVariableDestructureSkip1ArgumentAst,
    LocalVariableDestructureSkipNArgumentsAst,
    LocalVariableSingleIdentifierAst]

type LocalVariableNestedForDestructureTupleAst = Union[
    LocalVariableDestructureArrayAst,
    LocalVariableDestructureTupleAst,
    LocalVariableDestructureObjectAst,
    LocalVariableDestructureSkip1ArgumentAst,
    LocalVariableDestructureSkipNArgumentsAst,
    LocalVariableSingleIdentifierAst]

type LocalVariableNestedForDestructureObjectAst = Union[
    LocalVariableAttributeBindingAst,
    LocalVariableDestructureSkipNArgumentsAst,
    LocalVariableSingleIdentifierAst]

type LocalVariableNestedForAttributeBindingAst = Union[
    LocalVariableDestructureArrayAst,
    LocalVariableDestructureTupleAst,
    LocalVariableDestructureObjectAst]

__all__ = [
    "LocalVariableAst",
    "LocalVariableNestedForDestructureArrayAst",
    "LocalVariableNestedForDestructureTupleAst",
    "LocalVariableNestedForDestructureObjectAst",
    "LocalVariableNestedForAttributeBindingAst"]
