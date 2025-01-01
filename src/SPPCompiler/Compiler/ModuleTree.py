from __future__ import annotations
from dataclasses import dataclass, field
from glob import glob
from typing import Iterable, Optional, TYPE_CHECKING
import os

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

    def __init__(self, path: str) -> None:
        # Get all the spp module files from the src path.
        self._src_path = os.path.join(path, "src")
        self._vcs_path = os.path.join(path, "vcs")

        # Get all the modules from the src and vcs paths.
        src_modules = Seq(glob(self._src_path + "/**/*.spp", recursive=True)).map(Module)
        vcs_modules = Seq(glob(self._vcs_path + "/**/*.spp", recursive=True)).map(Module)

        # Merge the source and version control system modules.
        self._modules = src_modules + vcs_modules
        for m in self._modules:
            setattr(m, "path", m.path.replace(os.getcwd(), "", 1))

    def __iter__(self) -> Iterable[Module]:
        # Iterate over the modules.
        return iter(self._modules)

    @property
    def modules(self) -> Seq[Module]:
        # Return the source and version control system modules.
        return self._modules


__all__ = ["ModuleTree"]
