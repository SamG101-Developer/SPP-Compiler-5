from __future__ import annotations

from collections import defaultdict
from typing import Dict, Optional, TYPE_CHECKING, Callable, List

from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis import Asts
    from SPPCompiler.SemanticAnalysis.Scoping.Symbols import Symbol


class SymbolTable:
    _table: Dict[Asts.IdentifierAst | Asts.GenericIdentifierAst, Symbol]
    _deferment_queue: defaultdict[str, List[Callable]]

    def __init__(self, table: Optional[Dict[Asts.IdentifierAst | Asts.GenericIdentifierAst, Symbol]] = None):
        self._table = table or {}
        self._deferment_queue = defaultdict(list)

    def add(self, symbol: Symbol) -> None:
        # Add a symbol to the table.
        self._table[symbol.name] = symbol

        # Apply any post-symbol creation steps to the symbol.
        if symbol.name.value in self._deferment_queue:
            for callback in self._deferment_queue[symbol.name.value]:
                callback(symbol)
            del self._deferment_queue[symbol.name.value]

    def rem(self, symbol_name: Asts.IdentifierAst) -> None:
        # Remove a symbol from the table by symbol name.
        del self._table[symbol_name]

    def get(self, name: Asts.IdentifierAst | Asts.GenericIdentifierAst, default=None) -> Symbol:
        # Get a symbol from the table.
        return self._table.get(name, default)

    def set(self, name: Asts.IdentifierAst | Asts.GenericIdentifierAst, symbol: Symbol) -> None:
        # Set a symbol in the table.
        self._table[name] = symbol

    def has(self, name: Asts.IdentifierAst | Asts.GenericIdentifierAst) -> bool:
        # Check if a symbol is in the table.
        return name in self._table

    def all(self, match_type: type = None) -> Seq[Symbol]:
        # Get all symbols in the table.
        if match_type is not None:
            return Seq([symbol for name, symbol in self._table.items() if isinstance(name, match_type)])
        return Seq([*self._table.values()])

    def add_deferred_callback(self, symbol_name: Asts.IdentifierAst | Asts.GenericIdentifierAst, callback: Callable) -> None:
        # Add a deferred callback.
        self._deferment_queue[symbol_name.value].append(callback)

    def __json__(self) -> Dict:
        # Dump the SymbolTable as a JSON object.
        return {"symbols": self.all()}

    def __copy__(self) -> SymbolTable:
        # Copy the symbol table.
        return SymbolTable(self._table.copy())


__all__ = [
    "SymbolTable"]
