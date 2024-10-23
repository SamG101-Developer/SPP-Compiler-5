from typing import Union

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
