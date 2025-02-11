from __future__ import annotations

from typing import Type

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.Utils.Sequence import Seq


class CommonTypes:
    @staticmethod
    def type_variant_to_convention(type: Asts.TypeAst) -> Type[Asts.ConventionAst]:
        from SPPCompiler.SemanticAnalysis import ConventionMovAst, ConventionMutAst, ConventionRefAst

        match type.types[-1].value[-3:].lower():
            case "mov": return ConventionMovAst
            case "mut": return ConventionMutAst
            case "ref": return ConventionRefAst
            case _: raise ValueError(f"Invalid type variant: {type.types[-1].value}")

    @staticmethod
    def U8(pos: int = -1):
        return Asts.TypeAst(pos, Asts.ConventionMovAst(), Seq([Asts.IdentifierAst(pos, "std")]), Seq([Asts.GenericIdentifierAst(pos, "U8")]))

    @staticmethod
    def U16(pos: int = -1):
        return Asts.TypeAst(pos, Asts.ConventionMovAst(), Seq([Asts.IdentifierAst(pos, "std")]), Seq([Asts.GenericIdentifierAst(pos, "U16")]))

    @staticmethod
    def U32(pos: int = -1):
        return Asts.TypeAst(pos, Asts.ConventionMovAst(), Seq([Asts.IdentifierAst(pos, "std")]), Seq([Asts.GenericIdentifierAst(pos, "U32")]))

    @staticmethod
    def U64(pos: int = -1):
        return Asts.TypeAst(pos, Asts.ConventionMovAst(), Seq([Asts.IdentifierAst(pos, "std")]), Seq([Asts.GenericIdentifierAst(pos, "U64")]))

    @staticmethod
    def U128(pos: int = -1):
        return Asts.TypeAst(pos, Asts.ConventionMovAst(), Seq([Asts.IdentifierAst(pos, "std")]), Seq([Asts.GenericIdentifierAst(pos, "U128")]))

    @staticmethod
    def U256(pos: int = -1):
        return Asts.TypeAst(pos, Asts.ConventionMovAst(), Seq([Asts.IdentifierAst(pos, "std")]), Seq([Asts.GenericIdentifierAst(pos, "U256")]))

    @staticmethod
    def I8(pos: int = -1):
        return Asts.TypeAst(pos, Asts.ConventionMovAst(), Seq([Asts.IdentifierAst(pos, "std")]), Seq([Asts.GenericIdentifierAst(pos, "I8")]))

    @staticmethod
    def I16(pos: int = -1):
        return Asts.TypeAst(pos, Asts.ConventionMovAst(), Seq([Asts.IdentifierAst(pos, "std")]), Seq([Asts.GenericIdentifierAst(pos, "I16")]))

    @staticmethod
    def I32(pos: int = -1):
        return Asts.TypeAst(pos, Asts.ConventionMovAst(), Seq([Asts.IdentifierAst(pos, "std")]), Seq([Asts.GenericIdentifierAst(pos, "I32")]))

    @staticmethod
    def I64(pos: int = -1):
        return Asts.TypeAst(pos, Asts.ConventionMovAst(), Seq([Asts.IdentifierAst(pos, "std")]), Seq([Asts.GenericIdentifierAst(pos, "I64")]))

    @staticmethod
    def I128(pos: int = -1):
        return Asts.TypeAst(pos, Asts.ConventionMovAst(), Seq([Asts.IdentifierAst(pos, "std")]), Seq([Asts.GenericIdentifierAst(pos, "I128")]))

    @staticmethod
    def I256(pos: int = -1):
        return Asts.TypeAst(pos, Asts.ConventionMovAst(), Seq([Asts.IdentifierAst(pos, "std")]), Seq([Asts.GenericIdentifierAst(pos, "I256")]))

    @staticmethod
    def F8(pos: int = -1):
        return Asts.TypeAst(pos, Asts.ConventionMovAst(), Seq([Asts.IdentifierAst(pos, "std")]), Seq([Asts.GenericIdentifierAst(pos, "F8")]))

    @staticmethod
    def F16(pos: int = -1):
        return Asts.TypeAst(pos, Asts.ConventionMovAst(), Seq([Asts.IdentifierAst(pos, "std")]), Seq([Asts.GenericIdentifierAst(pos, "F16")]))

    @staticmethod
    def F32(pos: int = -1):
        return Asts.TypeAst(pos, Asts.ConventionMovAst(), Seq([Asts.IdentifierAst(pos, "std")]), Seq([Asts.GenericIdentifierAst(pos, "F32")]))

    @staticmethod
    def F64(pos: int = -1):
        return Asts.TypeAst(pos, Asts.ConventionMovAst(), Seq([Asts.IdentifierAst(pos, "std")]), Seq([Asts.GenericIdentifierAst(pos, "F64")]))

    @staticmethod
    def F128(pos: int = -1):
        return Asts.TypeAst(pos, Asts.ConventionMovAst(), Seq([Asts.IdentifierAst(pos, "std")]), Seq([Asts.GenericIdentifierAst(pos, "F128")]))

    @staticmethod
    def F256(pos: int = -1):
        return Asts.TypeAst(pos, Asts.ConventionMovAst(), Seq([Asts.IdentifierAst(pos, "std")]), Seq([Asts.GenericIdentifierAst(pos, "F256")]))

    @staticmethod
    def Self(pos: int = -1):
        return Asts.TypeAst(pos, Asts.ConventionMovAst(), Seq([]), Seq([Asts.GenericIdentifierAst(pos, "Self")]))

    @staticmethod
    def Void(pos: int = -1):
        return Asts.TypeAst(pos, Asts.ConventionMovAst(), Seq([Asts.IdentifierAst(pos, "std")]), Seq([Asts.GenericIdentifierAst(pos, "Void")]))

    @staticmethod
    def Bool(pos: int = -1):
        return Asts.TypeAst(pos, Asts.ConventionMovAst(), Seq([Asts.IdentifierAst(pos, "std")]), Seq([Asts.GenericIdentifierAst(pos, "Bool")]))

    @staticmethod
    def BigInt(pos: int = -1):
        return Asts.TypeAst(pos, Asts.ConventionMovAst(), Seq([Asts.IdentifierAst(pos, "std")]), Seq([Asts.GenericIdentifierAst(pos, "BigInt")]))

    @staticmethod
    def BigDec(pos: int = -1):
        return Asts.TypeAst(pos, Asts.ConventionMovAst(), Seq([Asts.IdentifierAst(pos, "std")]), Seq([Asts.GenericIdentifierAst(pos, "BigDec")]))

    @staticmethod
    def Str(pos: int = -1):
        return Asts.TypeAst(pos, Asts.ConventionMovAst(), Seq([Asts.IdentifierAst(pos, "std")]), Seq([Asts.GenericIdentifierAst(pos, "Str")]))

    @staticmethod
    def Rgx(pos: int = -1):
        return Asts.TypeAst(pos, Asts.ConventionMovAst(), Seq([Asts.IdentifierAst(pos, "std")]), Seq([Asts.GenericIdentifierAst(pos, "Rgx")]))

    @staticmethod
    def Copy(pos: int = -1):
        return Asts.TypeAst(pos, Asts.ConventionMovAst(), Seq([Asts.IdentifierAst(pos, "std")]), Seq([Asts.GenericIdentifierAst(pos, "Copy")]))

    @staticmethod
    def CtxRef(pos: int = -1):
        return Asts.TypeAst(pos, Asts.ConventionMovAst(), Seq([Asts.IdentifierAst(pos, "std")]), Seq([Asts.GenericIdentifierAst(pos, "CtxRef")]))

    @staticmethod
    def CtxMut(pos: int = -1):
        return Asts.TypeAst(pos, Asts.ConventionMovAst(), Seq([Asts.IdentifierAst(pos, "std")]), Seq([Asts.GenericIdentifierAst(pos, "CtxMut")]))

    @staticmethod
    def Single(inner_type=None, pos: int = -1):
        inner_type_generic = Asts.GenericTypeArgumentUnnamedAst(-1, inner_type)
        generics = Asts.GenericArgumentGroupAst(arguments=Seq([inner_type_generic]))
        return Asts.TypeAst(pos, Asts.ConventionMovAst(), Seq([Asts.IdentifierAst(pos, "std")]), Seq([Asts.GenericIdentifierAst(pos, "Box", generics)]))

    @staticmethod
    def Fut(inner_type, pos: int = -1):
        # Convert the inner type into a generic argument and load it into a group for the optional type.
        inner_type_generic = Asts.GenericTypeArgumentUnnamedAst(-1, inner_type)
        generics = Asts.GenericArgumentGroupAst(arguments=Seq([inner_type_generic]))
        return Asts.TypeAst(pos, Asts.ConventionMovAst(), Seq([Asts.IdentifierAst(pos, "std")]), Seq([Asts.GenericIdentifierAst(pos, "Fut", generics)]))

    @staticmethod
    def Arr(elem_type, size, pos: int = -1):
        # Convert the element type and size into generic arguments and load them into a group for the array type.
        elem_type_generic = Asts.GenericTypeArgumentUnnamedAst(-1, elem_type)
        size_comp_generic = Asts.GenericCompArgumentUnnamedAst(-1, size)
        generics = Asts.GenericArgumentGroupAst(arguments=Seq([elem_type_generic, size_comp_generic]))
        return Asts.TypeAst(pos, Asts.ConventionMovAst(), Seq([Asts.IdentifierAst(pos, "std")]), Seq([Asts.GenericIdentifierAst(pos, "Arr", generics)]))

    @staticmethod
    def Opt(inner_type, pos: int = -1):
        # Convert the inner type into a generic argument and load it into a group for the optional type.
        inner_type_generic = Asts.GenericTypeArgumentUnnamedAst(-1, inner_type)
        generics = Asts.GenericArgumentGroupAst(arguments=Seq([inner_type_generic]))
        return Asts.TypeAst(pos, Asts.ConventionMovAst(), Seq([Asts.IdentifierAst(pos, "std")]), Seq([Asts.GenericIdentifierAst(pos, "Opt", generics)]))

    @staticmethod
    def Tup(inner_types: Seq = None, pos: int = -1):
        # Convert the inner types into generic arguments and load them into a group for the tuple type.
        inner_type_generics = (inner_types or Seq()).map(lambda x: Asts.GenericTypeArgumentUnnamedAst(-1, x))
        generics = Asts.GenericArgumentGroupAst(arguments=inner_type_generics)
        return Asts.TypeAst(pos, Asts.ConventionMovAst(), Seq([Asts.IdentifierAst(pos, "std")]), Seq([Asts.GenericIdentifierAst(pos, "Tup", generics)]))

    @staticmethod
    def Var(inner_types: Seq = None, pos: int = -1):
        # Convert the inner types into generic arguments and load them into a group for the variant type.
        inner_type_generics = (inner_types or Seq()).map(lambda x: Asts.GenericTypeArgumentUnnamedAst(-1, x))
        generics = Asts.GenericArgumentGroupAst(arguments=inner_type_generics)
        return Asts.TypeAst(pos, Asts.ConventionMovAst(), Seq([Asts.IdentifierAst(pos, "std")]), Seq([Asts.GenericIdentifierAst(pos, "Var", generics)]))

    @staticmethod
    def FunRef(param_types, return_type, pos: int = -1):
        # Convert the parameter/return type(s) into generic arguments and load them into a group for the function type.
        return_type_generic = Asts.GenericTypeArgumentUnnamedAst(-1, return_type)
        param_types_generic = Asts.GenericTypeArgumentUnnamedAst(-1, param_types)
        generics = Asts.GenericArgumentGroupAst(arguments=Seq([param_types_generic, return_type_generic]))
        return Asts.TypeAst(pos, Asts.ConventionMovAst(), Seq([Asts.IdentifierAst(pos, "std")]), Seq([Asts.GenericIdentifierAst(pos, "FunRef", generics)]))

    @staticmethod
    def FunMut(param_types, return_type, pos: int = -1):
        # Convert the parameter/return type(s) into generic arguments and load them into a group for the function type.
        param_types_generic = Asts.GenericTypeArgumentUnnamedAst(-1, param_types)
        return_type_generic = Asts.GenericTypeArgumentUnnamedAst(-1, return_type)
        generics = Asts.GenericArgumentGroupAst(arguments=Seq([param_types_generic, return_type_generic]))
        return Asts.TypeAst(pos, Asts.ConventionMovAst(), Seq([Asts.IdentifierAst(pos, "std")]), Seq([Asts.GenericIdentifierAst(pos, "FunMut", generics)]))

    @staticmethod
    def FunMov(param_types, return_type, pos: int = -1):
        # Convert the parameter/return type(s) into generic arguments and load them into a group for the function type.
        param_types_generic = Asts.GenericTypeArgumentUnnamedAst(-1, param_types)
        return_type_generic = Asts.GenericTypeArgumentUnnamedAst(-1, return_type)
        generics = Asts.GenericArgumentGroupAst(arguments=Seq([param_types_generic, return_type_generic]))
        return Asts.TypeAst(pos, Asts.ConventionMovAst(), Seq([Asts.IdentifierAst(pos, "std")]), Seq([Asts.GenericIdentifierAst(pos, "FunMov", generics)]))

    @staticmethod
    def GenRef(gen_type=None, ret_type=None, send_type=None, pos: int = -1):
        # Convert the gen/send type(s) into generic arguments and load them into a group for the generator type.
        gen_type = Asts.GenericTypeArgumentUnnamedAst(-1, gen_type or CommonTypes.Void())
        send_type = Asts.GenericTypeArgumentUnnamedAst(-1, send_type or CommonTypes.Void())
        generics = Asts.GenericArgumentGroupAst(arguments=Seq([gen_type, send_type]))
        return Asts.TypeAst(pos, Asts.ConventionMovAst(), Seq([Asts.IdentifierAst(pos, "std")]), Seq([Asts.GenericIdentifierAst(pos, "GenRef", generics)]))

    @staticmethod
    def GenMut(gen_type=None, ret_type=None, send_type=None, pos: int = -1):
        # Convert the gen/send type(s) into generic arguments and load them into a group for the generator type.
        gen_type = Asts.GenericTypeArgumentUnnamedAst(-1, gen_type or CommonTypes.Void())
        send_type = Asts.GenericTypeArgumentUnnamedAst(-1, send_type or CommonTypes.Void())
        generics = Asts.GenericArgumentGroupAst(arguments=Seq([gen_type, send_type]))
        return Asts.TypeAst(pos, Asts.ConventionMovAst(), Seq([Asts.IdentifierAst(pos, "std")]), Seq([Asts.GenericIdentifierAst(pos, "GenMut", generics)]))

    @staticmethod
    def GenMov(gen_type=None, ret_type=None, send_type=None, pos: int = -1):
        # Convert the gen/send type(s) into generic arguments and load them into a group for the generator type.
        gen_type = Asts.GenericTypeArgumentUnnamedAst(-1, gen_type or CommonTypes.Void())
        send_type = Asts.GenericTypeArgumentUnnamedAst(-1, send_type or CommonTypes.Void())
        generics = Asts.GenericArgumentGroupAst(arguments=Seq([gen_type, send_type]))
        return Asts.TypeAst(pos, Asts.ConventionMovAst(), Seq([Asts.IdentifierAst(pos, "std")]), Seq([Asts.GenericIdentifierAst(pos, "GenMov", generics)]))
