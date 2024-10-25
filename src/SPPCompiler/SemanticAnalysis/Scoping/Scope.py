from __future__ import annotations
from typing import Any, Optional

from SPPCompiler.Utils.Sequence import Seq


class Scope:
    _name: Any
    _parent: Optional[Scope]
    _children: Seq[Scope]
