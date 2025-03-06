from typing import Union

import SPPCompiler.SemanticAnalysis as Asts

PatternVariantAst = Union[
    Asts.PatternVariantElseAst,
    Asts.PatternVariantElseCaseAst,
    Asts.PatternVariantExpressionAst,
    Asts.PatternVariantLiteralAst,
    Asts.PatternVariantDestructureTupleAst,
    Asts.PatternVariantDestructureArrayAst,
    Asts.PatternVariantDestructureObjectAst,
    Asts.PatternVariantSingleIdentifierAst]

PatternGroupDestructureAst = Union[
    Asts.PatternVariantDestructureTupleAst,
    Asts.PatternVariantDestructureArrayAst,
    Asts.PatternVariantDestructureObjectAst]

PatternVariantNestedForDestructureArrayAst = Union[
    Asts.PatternVariantDestructureArrayAst,
    Asts.PatternVariantDestructureTupleAst,
    Asts.PatternVariantDestructureObjectAst,
    Asts.PatternVariantDestructureSkip1ArgumentAst,
    Asts.PatternVariantDestructureSkipNArgumentsAst,
    Asts.PatternVariantLiteralAst,
    Asts.PatternVariantSingleIdentifierAst]

PatternVariantNestedForDestructureTupleAst = Union[
    Asts.PatternVariantDestructureArrayAst,
    Asts.PatternVariantDestructureTupleAst,
    Asts.PatternVariantDestructureObjectAst,
    Asts.PatternVariantDestructureSkip1ArgumentAst,
    Asts.PatternVariantDestructureSkipNArgumentsAst,
    Asts.PatternVariantLiteralAst,
    Asts.PatternVariantSingleIdentifierAst]

PatternVariantNestedForDestructureObjectAst = Union[
    Asts.PatternVariantAttributeBindingAst,
    Asts.PatternVariantDestructureSkipNArgumentsAst,
    Asts.PatternVariantSingleIdentifierAst]

PatternVariantNestedForAttributeBindingAst = Union[
    Asts.PatternVariantDestructureArrayAst,
    Asts.PatternVariantDestructureTupleAst,
    Asts.PatternVariantDestructureObjectAst,
    Asts.PatternVariantLiteralAst]

__all__ = [
    "PatternVariantAst",
    "PatternGroupDestructureAst",
    "PatternVariantNestedForDestructureTupleAst",
    "PatternVariantNestedForDestructureArrayAst",
    "PatternVariantNestedForDestructureObjectAst",
    "PatternVariantNestedForAttributeBindingAst"]
