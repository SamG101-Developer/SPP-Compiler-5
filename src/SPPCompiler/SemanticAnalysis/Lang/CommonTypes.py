from __future__ import annotations
from typing import Type, TYPE_CHECKING

from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    import SPPCompiler.SemanticAnalysis as Asts


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
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst
        return TypeAst(pos, Seq([IdentifierAst(pos, "std")]), Seq([GenericIdentifierAst(pos, "U8")]))

    @staticmethod
    def U16(pos: int = -1):
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst
        return TypeAst(pos, Seq([IdentifierAst(pos, "std")]), Seq([GenericIdentifierAst(pos, "U16")]))

    @staticmethod
    def U32(pos: int = -1):
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst
        return TypeAst(pos, Seq([IdentifierAst(pos, "std")]), Seq([GenericIdentifierAst(pos, "U32")]))

    @staticmethod
    def U64(pos: int = -1):
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst
        return TypeAst(pos, Seq([IdentifierAst(pos, "std")]), Seq([GenericIdentifierAst(pos, "U64")]))

    @staticmethod
    def U128(pos: int = -1):
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst
        return TypeAst(pos, Seq([IdentifierAst(pos, "std")]), Seq([GenericIdentifierAst(pos, "U128")]))

    @staticmethod
    def U256(pos: int = -1):
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst
        return TypeAst(pos, Seq([IdentifierAst(pos, "std")]), Seq([GenericIdentifierAst(pos, "U256")]))

    @staticmethod
    def I8(pos: int = -1):
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst
        return TypeAst(pos, Seq([IdentifierAst(pos, "std")]), Seq([GenericIdentifierAst(pos, "I8")]))

    @staticmethod
    def I16(pos: int = -1):
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst
        return TypeAst(pos, Seq([IdentifierAst(pos, "std")]), Seq([GenericIdentifierAst(pos, "I16")]))

    @staticmethod
    def I32(pos: int = -1):
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst
        return TypeAst(pos, Seq([IdentifierAst(pos, "std")]), Seq([GenericIdentifierAst(pos, "I32")]))

    @staticmethod
    def I64(pos: int = -1):
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst
        return TypeAst(pos, Seq([IdentifierAst(pos, "std")]), Seq([GenericIdentifierAst(pos, "I64")]))

    @staticmethod
    def I128(pos: int = -1):
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst
        return TypeAst(pos, Seq([IdentifierAst(pos, "std")]), Seq([GenericIdentifierAst(pos, "I128")]))

    @staticmethod
    def I256(pos: int = -1):
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst
        return TypeAst(pos, Seq([IdentifierAst(pos, "std")]), Seq([GenericIdentifierAst(pos, "I256")]))

    @staticmethod
    def F8(pos: int = -1):
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst
        return TypeAst(pos, Seq([IdentifierAst(pos, "std")]), Seq([GenericIdentifierAst(pos, "F8")]))

    @staticmethod
    def F16(pos: int = -1):
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst
        return TypeAst(pos, Seq([IdentifierAst(pos, "std")]), Seq([GenericIdentifierAst(pos, "F16")]))

    @staticmethod
    def F32(pos: int = -1):
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst
        return TypeAst(pos, Seq([IdentifierAst(pos, "std")]), Seq([GenericIdentifierAst(pos, "F32")]))

    @staticmethod
    def F64(pos: int = -1):
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst
        return TypeAst(pos, Seq([IdentifierAst(pos, "std")]), Seq([GenericIdentifierAst(pos, "F64")]))

    @staticmethod
    def F128(pos: int = -1):
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst
        return TypeAst(pos, Seq([IdentifierAst(pos, "std")]), Seq([GenericIdentifierAst(pos, "F128")]))

    @staticmethod
    def F256(pos: int = -1):
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst
        return TypeAst(pos, Seq([IdentifierAst(pos, "std")]), Seq([GenericIdentifierAst(pos, "F256")]))

    @staticmethod
    def Self(pos: int = -1):
        from SPPCompiler.SemanticAnalysis import TypeAst, GenericIdentifierAst
        return TypeAst(pos, Seq([]), Seq([GenericIdentifierAst(pos, "Self")]))

    @staticmethod
    def Void(pos: int = -1):
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst
        return TypeAst(pos, Seq([IdentifierAst(pos, "std")]), Seq([GenericIdentifierAst(pos, "Void")]))

    @staticmethod
    def Bool(pos: int = -1):
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst
        return TypeAst(pos, Seq([IdentifierAst(pos, "std")]), Seq([GenericIdentifierAst(pos, "Bool")]))

    @staticmethod
    def BigInt(pos: int = -1):
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst
        return TypeAst(pos, Seq([IdentifierAst(pos, "std")]), Seq([GenericIdentifierAst(pos, "BigInt")]))

    @staticmethod
    def BigDec(pos: int = -1):
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst
        return TypeAst(pos, Seq([IdentifierAst(pos, "std")]), Seq([GenericIdentifierAst(pos, "BigDec")]))

    @staticmethod
    def Str(pos: int = -1):
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst
        return TypeAst(pos, Seq([IdentifierAst(pos, "std")]), Seq([GenericIdentifierAst(pos, "Str")]))

    @staticmethod
    def Rgx(pos: int = -1):
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst
        return TypeAst(pos, Seq([IdentifierAst(pos, "std")]), Seq([GenericIdentifierAst(pos, "Rgx")]))

    @staticmethod
    def Copy(pos: int = -1):
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst
        return TypeAst(pos, Seq([IdentifierAst(pos, "std")]), Seq([GenericIdentifierAst(pos, "Copy")]))

    @staticmethod
    def CtxRef(pos: int = -1):
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst
        return TypeAst(pos, Seq([IdentifierAst(pos, "std")]), Seq([GenericIdentifierAst(pos, "CtxRef")]))

    @staticmethod
    def CtxMut(pos: int = -1):
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst
        return TypeAst(pos, Seq([IdentifierAst(pos, "std")]), Seq([GenericIdentifierAst(pos, "CtxMut")]))

    @staticmethod
    def Box(inner_type=None, pos: int = -1):
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst, GenericTypeArgumentUnnamedAst
        from SPPCompiler.SemanticAnalysis import GenericArgumentGroupAst

        inner_type_generic = GenericTypeArgumentUnnamedAst(-1, inner_type)
        generics = GenericArgumentGroupAst(arguments=Seq([inner_type_generic]))
        return TypeAst(pos, Seq([IdentifierAst(pos, "std")]), Seq([GenericIdentifierAst(pos, "Box", generics)]))

    @staticmethod
    def Fut(inner_type, pos: int = -1):
        # Import ASTs needed for the type and generic argument creation.
        from SPPCompiler.SemanticAnalysis import IdentifierAst, GenericIdentifierAst, TypeAst
        from SPPCompiler.SemanticAnalysis import GenericArgumentGroupAst, GenericTypeArgumentUnnamedAst

        # Convert the inner type into a generic argument and load it into a group for the optional type.
        inner_type_generic = GenericTypeArgumentUnnamedAst(-1, inner_type)
        generics = GenericArgumentGroupAst(arguments=Seq([inner_type_generic]))
        return TypeAst(pos, Seq([IdentifierAst(pos, "std")]), Seq([GenericIdentifierAst(pos, "Fut", generics)]))

    @staticmethod
    def Arr(elem_type, size, pos: int = -1):
        # Import ASTs needed for the type and generic argument creation.
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst, GenericArgumentGroupAst
        from SPPCompiler.SemanticAnalysis import GenericCompArgumentUnnamedAst, GenericTypeArgumentUnnamedAst

        # Convert the element type and size into generic arguments and load them into a group for the array type.
        elem_type_generic = GenericTypeArgumentUnnamedAst(-1, elem_type)
        size_comp_generic = GenericCompArgumentUnnamedAst(-1, size)
        generics = GenericArgumentGroupAst(arguments=Seq([elem_type_generic, size_comp_generic]))
        return TypeAst(pos, Seq([IdentifierAst(pos, "std")]), Seq([GenericIdentifierAst(pos, "Arr", generics)]))

    @staticmethod
    def Opt(inner_type, pos: int = -1):
        # Import ASTs needed for the type and generic argument creation.
        from SPPCompiler.SemanticAnalysis import IdentifierAst, GenericIdentifierAst, TypeAst
        from SPPCompiler.SemanticAnalysis import GenericArgumentGroupAst, GenericTypeArgumentUnnamedAst

        # Convert the inner type into a generic argument and load it into a group for the optional type.
        inner_type_generic = GenericTypeArgumentUnnamedAst(-1, inner_type)
        generics = GenericArgumentGroupAst(arguments=Seq([inner_type_generic]))
        return TypeAst(pos, Seq([IdentifierAst(pos, "std")]), Seq([GenericIdentifierAst(pos, "Opt", generics)]))

    @staticmethod
    def Tup(inner_types: Seq = None, pos: int = -1):
        # Import ASTs needed for the type and generic argument creation.
        from SPPCompiler.SemanticAnalysis import IdentifierAst, GenericIdentifierAst, TypeAst
        from SPPCompiler.SemanticAnalysis import GenericArgumentGroupAst, GenericTypeArgumentUnnamedAst

        # Convert the inner types into generic arguments and load them into a group for the tuple type.
        inner_type_generics = (inner_types or Seq()).map(lambda x: GenericTypeArgumentUnnamedAst(-1, x))
        generics = GenericArgumentGroupAst(arguments=inner_type_generics)
        return TypeAst(pos, Seq([IdentifierAst(pos, "std")]), Seq([GenericIdentifierAst(pos, "Tup", generics)]))

    @staticmethod
    def Var(inner_types: Seq = None, pos: int = -1):
        # Import ASTs needed for the type and generic argument creation.
        from SPPCompiler.SemanticAnalysis import IdentifierAst, GenericIdentifierAst, TypeAst
        from SPPCompiler.SemanticAnalysis import GenericArgumentGroupAst, GenericTypeArgumentUnnamedAst

        # Convert the inner types into generic arguments and load them into a group for the variant type.
        inner_type_generics = (inner_types or Seq()).map(lambda x: GenericTypeArgumentUnnamedAst(-1, x))
        generics = GenericArgumentGroupAst(arguments=inner_type_generics)
        return TypeAst(pos, Seq([IdentifierAst(pos, "std")]), Seq([GenericIdentifierAst(pos, "Var", generics)]))

    @staticmethod
    def FunRef(param_types, return_type, pos: int = -1):  # param_types is a tuple
        # Import ASTs needed for the type and generic argument creation.
        from SPPCompiler.SemanticAnalysis import IdentifierAst, GenericIdentifierAst, TypeAst
        from SPPCompiler.SemanticAnalysis import GenericArgumentGroupAst, GenericTypeArgumentUnnamedAst

        # Convert the parameter/return type(s) into generic arguments and load them into a group for the function type.
        return_type_generic = GenericTypeArgumentUnnamedAst(-1, return_type)
        param_types_generic = GenericTypeArgumentUnnamedAst(-1, param_types)
        generics = GenericArgumentGroupAst(arguments=Seq([param_types_generic, return_type_generic]))
        return TypeAst(pos, Seq([IdentifierAst(pos, "std")]), Seq([GenericIdentifierAst(pos, "FunRef", generics)]))

    @staticmethod
    def FunMut(param_types, return_type, pos: int = -1):  # param_types is a tuple
        # Import ASTs needed for the type and generic argument creation.
        from SPPCompiler.SemanticAnalysis import IdentifierAst, GenericIdentifierAst, TypeAst
        from SPPCompiler.SemanticAnalysis import GenericArgumentGroupAst, GenericTypeArgumentUnnamedAst

        # Convert the parameter/return type(s) into generic arguments and load them into a group for the function type.
        param_types_generic = GenericTypeArgumentUnnamedAst(-1, param_types)
        return_type_generic = GenericTypeArgumentUnnamedAst(-1, return_type)
        generics = GenericArgumentGroupAst(arguments=Seq([param_types_generic, return_type_generic]))
        return TypeAst(pos, Seq([IdentifierAst(pos, "std")]), Seq([GenericIdentifierAst(pos, "FunMut", generics)]))

    @staticmethod
    def FunMov(param_types, return_type, pos: int = -1):  # param_types is a tuple
        # Import ASTs needed for the type and generic argument creation.
        from SPPCompiler.SemanticAnalysis import IdentifierAst, GenericIdentifierAst, TypeAst
        from SPPCompiler.SemanticAnalysis import GenericArgumentGroupAst, GenericTypeArgumentUnnamedAst

        # Convert the parameter/return type(s) into generic arguments and load them into a group for the function type.
        param_types_generic = GenericTypeArgumentUnnamedAst(-1, param_types)
        return_type_generic = GenericTypeArgumentUnnamedAst(-1, return_type)
        generics = GenericArgumentGroupAst(arguments=Seq([param_types_generic, return_type_generic]))
        return TypeAst(pos, Seq([IdentifierAst(pos, "std")]), Seq([GenericIdentifierAst(pos, "FunMov", generics)]))

    @staticmethod
    def GenRef(gen_type=None, ret_type=None, send_type=None, pos: int = -1):
        # Import ASTs needed for the type and generic argument creation.
        from SPPCompiler.SemanticAnalysis import IdentifierAst, GenericIdentifierAst, TypeAst
        from SPPCompiler.SemanticAnalysis import GenericArgumentGroupAst, GenericTypeArgumentUnnamedAst

        # Convert the gen/send type(s) into generic arguments and load them into a group for the generator type.
        gen_type = GenericTypeArgumentUnnamedAst(-1, gen_type or CommonTypes.Void())
        send_type = GenericTypeArgumentUnnamedAst(-1, send_type or CommonTypes.Void())
        generics = GenericArgumentGroupAst(arguments=Seq([gen_type, send_type]))
        return TypeAst(pos, Seq([IdentifierAst(pos, "std")]), Seq([GenericIdentifierAst(pos, "GenRef", generics)]))

    @staticmethod
    def GenMut(gen_type=None, ret_type=None, send_type=None, pos: int = -1):
        # Import ASTs needed for the type and generic argument creation.
        from SPPCompiler.SemanticAnalysis import IdentifierAst, GenericIdentifierAst, TypeAst
        from SPPCompiler.SemanticAnalysis import GenericArgumentGroupAst, GenericTypeArgumentUnnamedAst

        # Convert the gen/send type(s) into generic arguments and load them into a group for the generator type.
        gen_type = GenericTypeArgumentUnnamedAst(-1, gen_type or CommonTypes.Void())
        send_type = GenericTypeArgumentUnnamedAst(-1, send_type or CommonTypes.Void())
        generics = GenericArgumentGroupAst(arguments=Seq([gen_type, send_type]))
        return TypeAst(pos, Seq([IdentifierAst(pos, "std")]), Seq([GenericIdentifierAst(pos, "GenMut", generics)]))

    @staticmethod
    def GenMov(gen_type=None, ret_type=None, send_type=None, pos: int = -1):
        # Import ASTs needed for the type and generic argument creation.
        from SPPCompiler.SemanticAnalysis import IdentifierAst, GenericIdentifierAst, TypeAst
        from SPPCompiler.SemanticAnalysis import GenericArgumentGroupAst, GenericTypeArgumentUnnamedAst

        # Convert the gen/send type(s) into generic arguments and load them into a group for the generator type.
        gen_type = GenericTypeArgumentUnnamedAst(-1, gen_type or CommonTypes.Void())
        send_type = GenericTypeArgumentUnnamedAst(-1, send_type or CommonTypes.Void())
        generics = GenericArgumentGroupAst(arguments=Seq([gen_type, send_type]))
        return TypeAst(pos, Seq([IdentifierAst(pos, "std")]), Seq([GenericIdentifierAst(pos, "GenMov", generics)]))
