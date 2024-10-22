from dataclasses import dataclass

from SPPCompiler.SemanticAnalysis import FunctionPrototypeAst


@dataclass
class CoroutinePrototypeAst(FunctionPrototypeAst):
    ...


__all__ = ["CoroutinePrototypeAst"]
