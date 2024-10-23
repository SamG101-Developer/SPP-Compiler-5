from dataclasses import dataclass

from SPPCompiler.SemanticAnalysis import FunctionPrototypeAst


@dataclass
class SubroutinePrototypeAst(FunctionPrototypeAst):
    ...


__all__ = ["SubroutinePrototypeAst"]
