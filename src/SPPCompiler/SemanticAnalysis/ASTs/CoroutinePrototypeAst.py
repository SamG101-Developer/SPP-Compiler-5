from dataclasses import dataclass

from SPPCompiler.SemanticAnalysis.ASTs.FunctionPrototypeAst import FunctionPrototypeAst


@dataclass
class CoroutinePrototypeAst(FunctionPrototypeAst):
    ...


__all__ = ["CoroutinePrototypeAst"]
