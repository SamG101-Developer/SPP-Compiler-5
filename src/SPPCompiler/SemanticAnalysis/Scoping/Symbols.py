from __future__ import annotations

import copy
import json
from dataclasses import dataclass, field
from typing import Dict, Optional, TYPE_CHECKING

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstMemoryUtils import MemoryInfo
from SPPCompiler.SemanticAnalysis.Asts.Mixins.VisibilityEnabledAst import Visibility
from SPPCompiler.Utils.FastDeepcopy import fast_deepcopy

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope


@dataclass(slots=True, kw_only=True)
class BaseSymbol:
    ...


@dataclass(slots=True, kw_only=True)
class NamespaceSymbol(BaseSymbol):
    name: Asts.IdentifierAst
    scope: Optional[Scope] = field(default=None)

    def __json__(self) -> Dict:
        # Dump the NamespaceSymbol as a JSON object.
        return {"what": "ns", "name": self.name, "scope": self.scope.name if self.scope else None}

    def __hash__(self) -> int:
        return hash(self.name)

    def __str__(self) -> str:
        # Dump the NamespaceSymbol as a JSON string.
        return json.dumps(self)

    def __eq__(self, other: NamespaceSymbol) -> bool:
        # Check if two NamespaceSymbols are equal.
        return self is other

    def __deepcopy__(self, memodict=None):
        # Copy the name into a new AST, but link the scope.
        return NamespaceSymbol(name=fast_deepcopy(self.name), scope=self.scope)


@dataclass(slots=True, kw_only=True)
class VariableSymbol(BaseSymbol):
    name: Asts.IdentifierAst
    type: Asts.TypeAst
    is_mutable: bool = field(default=False)
    is_generic: bool = field(default=False)
    memory_info: MemoryInfo = field(default_factory=MemoryInfo)
    visibility: Visibility = field(default=Visibility.Public)

    def __json__(self) -> Dict:
        # Dump the VariableSymbol as a JSON object.
        return {"what": "var", "name": self.name, "type": self.type}

    def __hash__(self) -> int:
        return hash(self.name)

    def __str__(self) -> str:
        # Dump the VariableSymbol as a JSON string.
        return json.dumps(self)

    def __eq__(self, other: VariableSymbol) -> bool:
        # Check if two VariableSymbols are equal.
        return self is other

    def __deepcopy__(self, memodict=None):
        # Copy the all the attributes of the VariableSymbol.
        return VariableSymbol(
            name=fast_deepcopy(self.name), type=fast_deepcopy(self.type), is_mutable=self.is_mutable,
            memory_info=copy.copy(self.memory_info), visibility=self.visibility)


@dataclass(slots=True, kw_only=True)
class TypeSymbol(BaseSymbol):
    name: Asts.GenericIdentifierAst
    type: Optional[Asts.ClassPrototypeAst]
    scope: Optional[Scope] = field(default=None)
    is_generic: bool = field(default=False)
    is_copyable: bool = field(default=False)
    visibility: Visibility = field(default=Visibility.Private)
    convention: Optional[Asts.ConventionAst] = field(default=None)
    generic_impl: TypeSymbol = field(default=None, repr=False)

    scope_defined_in: Optional[Scope] = field(default=None)

    def __post_init__(self) -> None:
        # Link the type symbol to the associated scope.
        if self.scope and not self.is_generic and not self.name.value == "Self":
            self.scope._type_symbol = self
        self.generic_impl = self

    def __json__(self) -> Dict:
        # Dump the TypeSymbol as a JSON object.
        return {
            "what": "type", "name": str(self.name), "type": str(self.type), "scope": str(self.scope.name) if self.scope else "",
            "parent": str(self.scope.parent.name) if self.scope and self.scope.parent else "", "id": id(self)}

    def __hash__(self) -> int:
        return hash(self.name)

    def __str__(self) -> str:
        # Dump the TypeSymbol as a JSON string.
        return json.dumps(self)

    def __eq__(self, other: TypeSymbol) -> bool:
        # Check if two TypeSymbols are equal.
        return self is other

    def __deepcopy__(self, memodict=None):
        # Copy all the attributes of the TypeSymbol, but link the scope.
        if self.is_generic:
            return TypeSymbol(
                name=fast_deepcopy(self.name), type=self.type, scope=self.scope, is_generic=self.is_generic,
                is_copyable=self.is_copyable, visibility=self.visibility, convention=self.convention,
                generic_impl=self.generic_impl, scope_defined_in=self.scope_defined_in)
        else:
            return self

    @property
    def fq_name(self) -> Asts.TypeAst:
        fq_name = Asts.TypeSingleAst.from_generic_identifier(self.name)

        if self.is_generic:
            return fq_name

        if type(self) is AliasSymbol:
            return fq_name

        if self.name.value[0] == "$":
            return fq_name

        if self.name.value == "Self":
            return self.scope.type_symbol.fq_name

        scope = self.scope.parent_module
        while scope.parent:
            fq_name = Asts.TypeUnaryExpressionAst(pos=fq_name.pos, op=Asts.TypeUnaryOperatorNamespaceAst(pos=scope.name.pos, name=scope.name), rhs=fq_name)
            scope = scope.parent
        return fq_name.with_convention(self.convention)


@dataclass(slots=True, kw_only=True)
class AliasSymbol(TypeSymbol):
    old_sym: TypeSymbol = field(default=None)

    def __json__(self) -> Dict:
        # Dump the AliasSymbol as a JSON object.
        return {
            "what": "alias", "name": self.name, "type": self.type, "scope": self.scope.name if self.scope else "",
            "parent": self.scope.parent.name if self.scope and self.scope.parent else "", "old_sym": self.old_sym,
            "id": id(self)}

    def __hash__(self) -> int:
        return hash(self.name)

    def __str__(self) -> str:
        # Dump the AliasSymbol as a JSON string.
        return json.dumps(self)

    def __eq__(self, other: AliasSymbol) -> bool:
        # Check if two AliasSymbols are equal.
        return self is other

    def __deepcopy__(self, memodict=None):
        # Copy all the attributes of the AliasSymbol, but link the old scope. No conventions on aliases.
        return AliasSymbol(
            name=fast_deepcopy(self.name), type=self.type, scope=self.scope, is_generic=self.is_generic,
            is_copyable=self.is_copyable, visibility=self.visibility, generic_impl=self.generic_impl,
            scope_defined_in=self.scope_defined_in, old_sym=fast_deepcopy(self.old_sym))


type Symbol = NamespaceSymbol | VariableSymbol | TypeSymbol | AliasSymbol


__all__ = [
    "Symbol",
    "AliasSymbol",
    "NamespaceSymbol",
    "VariableSymbol",
    "TypeSymbol"]
