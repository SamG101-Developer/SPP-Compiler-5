from typing import Union

from SPPCompiler.SemanticAnalysis.ASTs.PatternVariantDestructureArrayAst import PatternVariantDestructureArrayAst
from SPPCompiler.SemanticAnalysis.ASTs.PatternVariantElseAst import PatternVariantElseAst
from SPPCompiler.SemanticAnalysis.ASTs.PatternVariantLiteralAst import PatternVariantLiteralAst
from SPPCompiler.SemanticAnalysis.ASTs.PatternVariantAttributeBindingAst import PatternVariantAttributeBindingAst
from SPPCompiler.SemanticAnalysis.ASTs.PatternVariantDestructureObjectAst import PatternVariantDestructureObjectAst
from SPPCompiler.SemanticAnalysis.ASTs.PatternVariantDestructureTupleAst import PatternVariantDestructureTupleAst
from SPPCompiler.SemanticAnalysis.ASTs.PatternVariantDestructureSkip1ArgumentAst import PatternVariantDestructureSkip1ArgumentAst
from SPPCompiler.SemanticAnalysis.ASTs.PatternVariantDestructureSkipNArgumentsAst import PatternVariantDestructureSkipNArgumentsAst
from SPPCompiler.SemanticAnalysis.ASTs.PatternVariantSingleIdentifierAst import PatternVariantSingleIdentifierAst
from SPPCompiler.SemanticAnalysis.ASTs.PatternVariantExpressionAst import PatternVariantExpressionAst

type PatternVariantAst = Union[
    PatternVariantElseAst,
    PatternVariantExpressionAst,
    PatternVariantLiteralAst,
    PatternVariantDestructureTupleAst,
    PatternVariantDestructureArrayAst,
    PatternVariantDestructureObjectAst,
    PatternVariantSingleIdentifierAst]

type PatternGroupDestructureAst = Union[
    PatternVariantDestructureTupleAst,
    PatternVariantDestructureArrayAst,
    PatternVariantDestructureObjectAst]

type PatternVariantNestedForDestructureArrayAst = Union[
    PatternVariantDestructureArrayAst,
    PatternVariantDestructureTupleAst,
    PatternVariantDestructureObjectAst,
    PatternVariantDestructureSkipNArgumentsAst,
    PatternVariantDestructureSkip1ArgumentAst,
    PatternVariantExpressionAst,
    PatternVariantLiteralAst,
    PatternVariantSingleIdentifierAst]

type PatternVariantNestedForDestructureTupleAst = Union[
    PatternVariantDestructureArrayAst,
    PatternVariantDestructureTupleAst,
    PatternVariantDestructureObjectAst,
    PatternVariantDestructureSkipNArgumentsAst,
    PatternVariantDestructureSkip1ArgumentAst,
    PatternVariantExpressionAst,
    PatternVariantLiteralAst,
    PatternVariantSingleIdentifierAst]

type PatternVariantNestedForDestructureObjectAst = Union[
    PatternVariantAttributeBindingAst,
    PatternVariantDestructureSkipNArgumentsAst,
    PatternVariantSingleIdentifierAst]

type PatternVariantNestedForAttributeBindingAst = Union[
    PatternVariantDestructureArrayAst,
    PatternVariantDestructureTupleAst,
    PatternVariantDestructureObjectAst,
    PatternVariantLiteralAst]

__all__ = [
    "PatternVariantAst",
    "PatternGroupDestructureAst",
    "PatternVariantNestedForDestructureTupleAst",
    "PatternVariantNestedForDestructureArrayAst",
    "PatternVariantNestedForDestructureObjectAst",
    "PatternVariantNestedForAttributeBindingAst"]
