from __future__ import annotations
from typing import Dict, Optional, TYPE_CHECKING

from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    import SPPCompiler.SemanticAnalysis as Asts
    from SPPCompiler.SemanticAnalysis.Scoping.Symbols import Symbol


class SymbolTable:
    _table: Dict[Asts.IdentifierAst | Asts.GenericIdentifierAst, Symbol]

    def __init__(self, table: Optional[Dict[Asts.IdentifierAst | Asts.GenericIdentifierAst, Symbol]] = None):
        self._table = table or {}

    def add(self, symbol: Symbol) -> None:
        # Add a symbol to the table.
        self._table[symbol.name] = symbol

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

    def all(self) -> Seq[Symbol]:
        # Get all symbols in the table.
        return Seq([*self._table.values()])

    def __json__(self) -> Dict:
        # Dump the SymbolTable as a JSON object.
        return {"symbols": self.all().list()}

    def __copy__(self) -> SymbolTable:
        # Copy the symbol table.
        return SymbolTable(self._table.copy())


__all__ = ["SymbolTable"]
