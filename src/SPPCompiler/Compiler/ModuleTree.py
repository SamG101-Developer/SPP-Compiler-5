from __future__ import annotations

import os
from dataclasses import dataclass, field
from glob import glob
from typing import Iterable, List, Optional

from SPPCompiler.LexicalAnalysis.TokenType import RawToken
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.Utils.ErrorFormatter import ErrorFormatter
from SPPCompiler.Utils.Sequence import Seq


@dataclass(slots=True)
class Module:
    """
    A Module represents a file of code, and associated information for convenience, such as the token stream, which is
    the lexed output for this module.

    Another key attribute is the error_formatter, which is used to format errors for this module, by using the local
    token stream. This allows cross module context for errors.
    """

    path: str
    code: str = field(default="")
    token_stream: List[RawToken] = field(default_factory=Seq)
    module_ast: Optional[Asts.ModulePrototypeAst] = field(default=None)
    error_formatter: Optional[ErrorFormatter] = field(default=None)


class ModuleTree:
    """
    The ModuleTree holds a list of modules from the local "src" and "vcs" directories. This tree is then used by the
    compiler to iterate through and process each module.
    """

    _root: str
    _src_path: str
    _vcs_path: str
    _ffi_path: str
    _modules: Seq[Module]

    def __init__(self, path: str) -> None:
        # Get all the spp module files from the src path.
        self._root = path
        self._src_path = os.path.join(path, "src")
        self._vcs_path = os.path.join(path, "vcs")
        self._ffi_path = os.path.join(path, "ffi")

        # Get all the modules from the src and vcs paths. Todo: cross platform filepaths.
        src_modules = [Module(f) for f in glob(self._src_path + "/**/*.spp", recursive=True)]
        vcs_modules = [Module(f) for f in glob(self._vcs_path + "/**/*.spp", recursive=True)]
        ffi_modules = [Module(f) for f in glob(self._ffi_path + "/**/*.spp", recursive=True)]

        # Remove vcs main.spp files (keep src main.spp though).
        for m in vcs_modules.copy():
            inner_path = m.path.replace(self._vcs_path + os.sep, "", 1)
            inner_path = os.sep.join(inner_path.split(os.sep)[1:])
            if inner_path == os.path.join("src", "main.spp") or inner_path.startswith("ffi" + os.sep):
                vcs_modules.remove(m)

        # Merge the source and version control system modules.
        self._modules = src_modules + vcs_modules + ffi_modules
        for m in self._modules:
            m.path = m.path.replace(os.getcwd(), "", 1)

    def __iter__(self) -> Iterable[Module]:
        """
        Iterate through the module tree by iterating through the list of modules.

        :return: An iterator for the modules in the module tree.
        """

        # Iterate over the modules.
        return iter(self._modules)

    @property
    def modules(self) -> Seq[Module]:
        """
        Get the list of modules in the module tree.

        :return: The list of modules.
        """

        # Return the source and version control system modules.
        return self._modules


__all__ = ["ModuleTree"]
