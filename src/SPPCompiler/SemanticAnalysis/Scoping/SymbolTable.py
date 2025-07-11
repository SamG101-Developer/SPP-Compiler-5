from __future__ import annotations

from typing import Dict, Iterator, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis import Asts
    from SPPCompiler.SemanticAnalysis.Scoping.Symbols import Symbol


class SymbolTable:
    _table: Dict[Asts.IdentifierAst | Asts.TypeIdentifierAst, Symbol]

    def __init__(self, table: Optional[Dict[Asts.IdentifierAst | Asts.TypeIdentifierAst, Symbol]] = None):
        self._table = table or {}

    def add(self, symbol: Symbol) -> None:
        # Add a symbol to the table.
        self._table[symbol.name] = symbol

    def rem(self, symbol_name: Asts.IdentifierAst) -> None:
        # Remove a symbol from the table by symbol name.
        del self._table[symbol_name]

    def get(self, name: Asts.IdentifierAst | Asts.TypeIdentifierAst, default=None) -> Symbol:
        # Get a symbol from the table.
        return self._table.get(name, default)

    def set(self, name: Asts.IdentifierAst | Asts.TypeIdentifierAst, symbol: Symbol) -> None:
        # Set a symbol in the table.
        self._table[name] = symbol

    def has(self, name: Asts.IdentifierAst | Asts.TypeIdentifierAst) -> bool:
        # Check if a symbol is in the table.
        return name in self._table

    def all(self) -> Iterator[Symbol]:
        # Get all symbols in the table.
        for v in self._table.values():
            yield v

    def __json__(self) -> Dict:
        # Dump the SymbolTable as a JSON object.
        return {"symbols": [*self.all()]}

    def __copy__(self) -> SymbolTable:
        # Copy the symbol table.
        return SymbolTable(self._table.copy())


__all__ = [
    "SymbolTable"]
