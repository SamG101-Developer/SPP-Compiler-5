from __future__ import annotations
from dataclasses import dataclass, field
from glob import glob
from typing import Iterable, Optional, TYPE_CHECKING

from SPPCompiler.Utils.ErrorFormatter import ErrorFormatter
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.LexicalAnalysis.TokenType import TokenType
    from SPPCompiler.SemanticAnalysis.ASTs.ModulePrototypeAst import ModulePrototypeAst


@dataclass
class Module:
    path: str
    code: str = field(default="")
    token_stream: Seq[TokenType] = field(default_factory=Seq)
    module_ast: Optional[ModulePrototypeAst] = field(default=None)
    error_formatter: Optional[ErrorFormatter] = field(default=None)


class ModuleTree:
    _src_path: str
    _modules: Seq[Module]

    def __init__(self, src_path: str, standalone: bool = False) -> None:
        # Get all the spp module files from the src path
        self._src_path = src_path
        if not standalone:
            self._modules = Seq(glob(self._src_path + "/**/*.spp", recursive=True)).map(Module)
        else:
            self._modules = Seq([Module(src_path)])

    def __iter__(self) -> Iterable[Module]:
        # Iterate over the modules
        return iter(self._modules)

    @property
    def modules(self) -> Seq[Module]:
        return self._modules

    # Todo: VCS imports


__all__ = ["ModuleTree"]
