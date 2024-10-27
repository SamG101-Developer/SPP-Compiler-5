from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ClassPrototypeAst import ClassPrototypeAst
    from SPPCompiler.SemanticAnalysis.ASTs.ClassAttributeAst import ClassAttributeAst
    from SPPCompiler.SemanticAnalysis.ASTs.FunctionPrototypeAst import FunctionPrototypeAst
    from SPPCompiler.SemanticAnalysis.ASTs.GlobalConstantAst import GlobalConstantAst
    from SPPCompiler.SemanticAnalysis.ASTs.ModulePrototypeAst import ModulePrototypeAst
    from SPPCompiler.SemanticAnalysis.ASTs.SupPrototypeFunctionsAst import SupPrototypeFunctionsAst
    from SPPCompiler.SemanticAnalysis.ASTs.UseStatementAst import UseStatementAst

type PreProcessingContext = Optional[Union[
    ClassPrototypeAst,
    ClassAttributeAst,
    FunctionPrototypeAst,
    GlobalConstantAst,
    ModulePrototypeAst,
    SupPrototypeFunctionsAst,
    UseStatementAst]]


@dataclass
class Stage1_PreProcessor(ABC):
    _ctx: PreProcessingContext = field(default=None, kw_only=True, repr=False)

    @abstractmethod
    def pre_process(self, context: PreProcessingContext) -> None:
        self._ctx = context


__all__ = ["Stage1_PreProcessor", "PreProcessingContext"]
