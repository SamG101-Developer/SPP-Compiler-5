from typing import Union

from SPPCompiler.SemanticAnalysis.PatternVariantElseAst import PatternVariantElseAst
from SPPCompiler.SemanticAnalysis.PatternVariantLiteralAst import PatternVariantLiteralAst
from SPPCompiler.SemanticAnalysis.PatternVariantAttributeBindingAst import PatternVariantAttributeBindingAst
from SPPCompiler.SemanticAnalysis.PatternVariantDestructureObjectAst import PatternVariantDestructureObjectAst
from SPPCompiler.SemanticAnalysis.PatternVariantDestructureTupleAst import PatternVariantDestructureTupleAst
from SPPCompiler.SemanticAnalysis.PatternVariantDestructureSkip1ArgumentAst import PatternVariantDestructureSkip1ArgumentAst
from SPPCompiler.SemanticAnalysis.PatternVariantDestructureSkipNArgumentsAst import PatternVariantDestructureSkipNArgumentsAst
from SPPCompiler.SemanticAnalysis.PatternVariantSingleIdentifierAst import PatternVariantSingleIdentifierAst
from SPPCompiler.SemanticAnalysis.PatternVariantExpressionAst import PatternVariantExpressionAst

type PatternVariantAst = Union[
    PatternVariantElseAst,
    PatternVariantExpressionAst,
    PatternVariantLiteralAst,
    PatternVariantDestructureObjectAst,
    PatternVariantDestructureTupleAst,
    PatternVariantSingleIdentifierAst]

type PatternGroupDestructureAst = Union[
    PatternVariantDestructureObjectAst,
    PatternVariantDestructureTupleAst]

type PatternVariantNestedForDestructureObjectAst = Union[
    PatternVariantAttributeBindingAst,
    PatternVariantDestructureSkipNArgumentsAst,
    PatternVariantSingleIdentifierAst]

type PatternVariantNestedForDestructureTupleAst = Union[
    PatternVariantDestructureTupleAst,
    PatternVariantDestructureObjectAst,
    PatternVariantDestructureSkipNArgumentsAst,
    PatternVariantDestructureSkip1ArgumentAst,
    PatternVariantExpressionAst,
    PatternVariantLiteralAst,
    PatternVariantSingleIdentifierAst,]

type PatternVariantNestedForAttributeBindingAst = Union[
    PatternVariantDestructureTupleAst,
    PatternVariantDestructureObjectAst,
    PatternVariantExpressionAst,
    PatternVariantLiteralAst,
    PatternVariantSingleIdentifierAst]

__all__ = [
    "PatternVariantAst",
    "PatternGroupDestructureAst",
    "PatternVariantNestedForDestructureObjectAst",
    "PatternVariantNestedForDestructureTupleAst",
    "PatternVariantNestedForAttributeBindingAst"]
