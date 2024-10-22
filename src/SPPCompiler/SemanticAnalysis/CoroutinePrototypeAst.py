from dataclasses import dataclass

from SPPCompiler.SemanticAnalysis.FunctionPrototypeAst import FunctionPrototypeAst


@dataclass
class CoroutinePrototypeAst(FunctionPrototypeAst):
    ...


__all__ = ["CoroutinePrototypeAst"]
