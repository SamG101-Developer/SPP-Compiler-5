from typing import Union

import SPPCompiler.SemanticAnalysis as Asts

type PatternVariantAst = Union[
    Asts.PatternVariantElseAst,
    Asts.PatternVariantExpressionAst,
    Asts.PatternVariantLiteralAst,
    Asts.PatternVariantDestructureTupleAst,
    Asts.PatternVariantDestructureArrayAst,
    Asts.PatternVariantDestructureObjectAst,
    Asts.PatternVariantSingleIdentifierAst]

type PatternGroupDestructureAst = Union[
    Asts.PatternVariantDestructureTupleAst,
    Asts.PatternVariantDestructureArrayAst,
    Asts.PatternVariantDestructureObjectAst]

type PatternVariantNestedForDestructureArrayAst = Union[
    Asts.PatternVariantDestructureArrayAst,
    Asts.PatternVariantDestructureTupleAst,
    Asts.PatternVariantDestructureObjectAst,
    Asts.PatternVariantDestructureSkipNArgumentsAst,
    Asts.PatternVariantDestructureSkip1ArgumentAst,
    Asts.PatternVariantExpressionAst,
    Asts.PatternVariantLiteralAst,
    Asts.PatternVariantSingleIdentifierAst]

type PatternVariantNestedForDestructureTupleAst = Union[
    Asts.PatternVariantDestructureArrayAst,
    Asts.PatternVariantDestructureTupleAst,
    Asts.PatternVariantDestructureObjectAst,
    Asts.PatternVariantDestructureSkipNArgumentsAst,
    Asts.PatternVariantDestructureSkip1ArgumentAst,
    Asts.PatternVariantExpressionAst,
    Asts.PatternVariantLiteralAst,
    Asts.PatternVariantSingleIdentifierAst]

type PatternVariantNestedForDestructureObjectAst = Union[
    Asts.PatternVariantAttributeBindingAst,
    Asts.PatternVariantDestructureSkipNArgumentsAst,
    Asts.PatternVariantSingleIdentifierAst]

type PatternVariantNestedForAttributeBindingAst = Union[
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
