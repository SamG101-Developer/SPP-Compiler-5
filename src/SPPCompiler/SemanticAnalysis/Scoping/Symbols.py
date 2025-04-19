from __future__ import annotations

import copy
import json
from dataclasses import dataclass, field
from typing import Dict, Optional, TYPE_CHECKING, Callable

import json_fix

from SPPCompiler.CodeGen.LlvmSymbolInfo import LlvmSymbolInfo
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstMemoryUtils import MemoryInfo
from SPPCompiler.SemanticAnalysis.Asts.Mixins.VisibilityEnabledAst import Visibility

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope


@dataclass(kw_only=True)
class NamespaceSymbol:
    name: Asts.IdentifierAst
    scope: Optional[Scope] = field(default=None)

    def __post_init__(self) -> None:
        # Ensure the name is an IdentifierAst.
        assert isinstance(self.name, Asts.IdentifierAst)

    def __json__(self) -> Dict:
        # Dump the NamespaceSymbol as a JSON object.
        return {"what": "ns", "name": self.name, "scope": self.scope.name if self.scope else None}

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
    visibility: Visibility = field(default=Visibility.Public)

    def __post_init__(self) -> None:
        # Ensure the name is an IdentifierAst, and the type is a TypeAst.
        assert isinstance(self.name, Asts.IdentifierAst)
        assert isinstance(self.type, Asts.TypeAst)

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
    visibility: Visibility = field(default=Visibility.Private)
    llvm_info: LlvmSymbolInfo = field(default_factory=LlvmSymbolInfo)
    convention: Optional[Asts.ConventionAst] = field(default=None)

    scope_defined_in: Optional[Scope] = field(default=None)

    def __post_init__(self) -> None:
        # Ensure the name is a GenericIdentifierAst, and the type is a ClassPrototypeAst or None.
        assert isinstance(self.name, Asts.GenericIdentifierAst)
        assert isinstance(self.type, Asts.ClassPrototypeAst) or self.type is None

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
            is_copyable=self.is_copyable, visibility=self.visibility, convention=self.convention,
            scope_defined_in=self.scope_defined_in)

    @property
    def fq_name(self) -> Asts.TypeAst:
        fq_name = Asts.TypeSingleAst.from_generic_identifier(self.name)
        if self.type:
            fq_name = fq_name.sub_generics(
                Asts.GenericArgumentGroupAst.from_parameter_group(
                    self.type.generic_parameter_group.parameters, use_default=True).arguments)

        if self.is_generic:
            return fq_name

        if isinstance(self, AliasSymbol):
            return fq_name

        if self.name.value[0] == "$":
            return fq_name

        scope = self.scope.parent_module
        while scope.parent:
            if isinstance(scope.name, Asts.IdentifierAst):
                fq_name = Asts.TypeUnaryExpressionAst(pos=fq_name.pos, op=Asts.TypeUnaryOperatorNamespaceAst(pos=scope.name.pos, name=scope.name), rhs=fq_name)
            else:
                raise NotImplementedError("Nested types are not supported yet.")
            scope = scope.parent

        return fq_name.with_convention(self.convention)


@dataclass(kw_only=True)
class AliasSymbol(TypeSymbol):
    old_sym: TypeSymbol = field(default=None)

    def __json__(self) -> Dict:
        # Dump the AliasSymbol as a JSON object.
        return super().__json__() | {"old_sym": self.old_sym}

    def __deepcopy__(self, memodict=None):
        # Copy all the attributes of the AliasSymbol, but link the old scope.
        return AliasSymbol(
            name=copy.deepcopy(self.name), type=copy.deepcopy(self.type), scope=self.scope, is_generic=self.is_generic,
            is_copyable=self.is_copyable, visibility=self.visibility, old_sym=copy.deepcopy(self.old_sym))


type Symbol = AliasSymbol | NamespaceSymbol | VariableSymbol | TypeSymbol

__all__ = [
    "Symbol",
    "AliasSymbol",
    "NamespaceSymbol",
    "VariableSymbol",
    "TypeSymbol"]
