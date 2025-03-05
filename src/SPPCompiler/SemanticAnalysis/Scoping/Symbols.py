from __future__ import annotations

import copy, json
from dataclasses import dataclass, field
from typing import Dict, Optional, TYPE_CHECKING

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.SemanticAnalysis.Meta.AstMemory import MemoryInfo
from SPPCompiler.SemanticAnalysis.Mixins.VisibilityEnabled import AstVisibility
from SPPCompiler.CodeGen.LlvmSymbolInfo import LlvmSymbolInfo

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope


@dataclass(kw_only=True)
class NamespaceSymbol:
    name: Asts.IdentifierAst
    scope: Optional[Scope] = field(default=None)

    def __post_init__(self) -> None:
        # Ensure the name is an IdentifierAst.
        from SPPCompiler.SemanticAnalysis import IdentifierAst
        assert isinstance(self.name, IdentifierAst)

    def __json__(self) -> Dict:
        # Dump the NamespaceSymbol as a JSON object.
        return {"what": "ns", "name": self.name}

    def __str__(self) -> str:
        # Dump the NamespaceSymbol as a JSON string.
        return json.dumps(self)

    def __deepcopy__(self, memodict=None):
        # Copy the name into a new AST, but link the scope.
        return NamespaceSymbol(name=copy.deepcopy(self.name), scope=self.scope)


@dataclass(kw_only=True)
class VariableSymbol:
    name: Asts.IdentifierAst
    type: Asts.TypeAst
    is_mutable: bool = field(default=False)
    is_generic: bool = field(default=False)
    memory_info: MemoryInfo = field(default_factory=MemoryInfo)
    visibility: AstVisibility = field(default=AstVisibility.Public)

    def __post_init__(self) -> None:
        # Ensure the name is an IdentifierAst, and the type is a TypeAst.
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst
        assert isinstance(self.name, IdentifierAst)
        assert isinstance(self.type, TypeAst)

    def __json__(self) -> Dict:
        # Dump the VariableSymbol as a JSON object.
        return {"what": "var", "name": self.name, "type": self.type}

    def __hash__(self) -> int:
        return hash(self.name)

    def __str__(self) -> str:
        # Dump the VariableSymbol as a JSON string.
        return json.dumps(self)

    def __deepcopy__(self, memodict=None):
        # Copy the all the attributes of the VariableSymbol.
        return VariableSymbol(
            name=copy.deepcopy(self.name), type=copy.deepcopy(self.type), is_mutable=self.is_mutable,
            memory_info=copy.copy(self.memory_info), visibility=self.visibility)


@dataclass(kw_only=True)
class TypeSymbol:
    name: Asts.GenericIdentifierAst
    type: Optional[Asts.ClassPrototypeAst]
    scope: Optional[Scope] = field(default=None)
    is_generic: bool = field(default=False)
    is_copyable: bool = field(default=False)
    is_abstract: bool = field(default=False)
    visibility: AstVisibility = field(default=AstVisibility.Private)
    llvm_info: LlvmSymbolInfo = field(default_factory=LlvmSymbolInfo)

    def __post_init__(self) -> None:
        # Ensure the name is a GenericIdentifierAst, and the type is a ClassPrototypeAst or None.
        from SPPCompiler.SemanticAnalysis import GenericIdentifierAst, ClassPrototypeAst
        assert isinstance(self.name, GenericIdentifierAst)
        assert isinstance(self.type, ClassPrototypeAst) or self.type is None

        # Link the type symbol to the associated scope.
        if self.scope and not self.is_generic and not self.name.value == "Self":
            self.scope._type_symbol = self

    def __json__(self) -> Dict:
        # Dump the TypeSymbol as a JSON object.
        return {"what": "type", "name": self.name, "type": self.type, "scope": self.scope.name if self.scope else ""}

    def __str__(self) -> str:
        # Dump the TypeSymbol as a JSON string.
        return json.dumps(self)

    def __deepcopy__(self, memodict=None):
        # Copy all the attributes of the TypeSymbol, but link the scope.
        return TypeSymbol(
            name=copy.deepcopy(self.name), type=copy.deepcopy(self.type), scope=self.scope, is_generic=self.is_generic,
            is_copyable=self.is_copyable, is_abstract=self.is_abstract, visibility=self.visibility)

    @property
    def fq_name(self) -> Asts.TypeAst:
        fq_name = Asts.TypeSingleAst.from_generic_identifier(self.name)
        if self.is_generic:
            return fq_name
        if isinstance(self, AliasSymbol):
            return fq_name
        if self.name.value[0] == "$":
            return fq_name

        scope = self.scope.parent_module
        while scope.parent:
            if isinstance(scope.name, Asts.IdentifierAst):
                fq_name = fq_name.prepend_namespace_part(scope.name)
            else:
                raise NotImplementedError("Nested types are not supported yet.")
            scope = scope.parent

        return fq_name


@dataclass(kw_only=True)
class AliasSymbol(TypeSymbol):
    old_type: Asts.TypeAst = field(default=None)

    def __json__(self) -> Dict:
        # Dump the AliasSymbol as a JSON object.
        return super().__json__() | {"old_type": self.old_type}

    def __deepcopy__(self, memodict=None):
        # Copy all the attributes of the AliasSymbol, but link the old scope.
        return AliasSymbol(
            name=copy.deepcopy(self.name), type=copy.deepcopy(self.type), scope=self.scope, is_generic=self.is_generic,
            is_copyable=self.is_copyable, is_abstract=self.is_abstract, visibility=self.visibility,
            old_type=copy.deepcopy(self.old_type))


type Symbol = NamespaceSymbol | VariableSymbol | TypeSymbol | AliasSymbol

__all__ = [
    "Symbol",
    "NamespaceSymbol",
    "VariableSymbol",
    "TypeSymbol",
    "AliasSymbol"]
