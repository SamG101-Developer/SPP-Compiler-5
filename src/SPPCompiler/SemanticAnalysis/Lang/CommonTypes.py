from __future__ import annotations
from typing import Type, TYPE_CHECKING

from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst
    from SPPCompiler.SemanticAnalysis.ASTs.ConventionAst import ConventionAst


class CommonTypes:
    @staticmethod
    def type_variant_to_convention(type: TypeAst) -> Type[ConventionAst]:
        from SPPCompiler.SemanticAnalysis import ConventionMovAst, ConventionMutAst, ConventionRefAst

        match type.types[-1].value[:-3].lower():
            case "mov": return ConventionMovAst
            case "mut": return ConventionMutAst
            case "ref": return ConventionRefAst
            case _: raise ValueError(f"Invalid type variant: {type.types[-1].value}")

    @staticmethod
    def U8(pos: int = -1):
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst
        return TypeAst(pos, [IdentifierAst(pos, "std")], [GenericIdentifierAst(pos, "U8", None)])

    @staticmethod
    def U16(pos: int = -1):
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst
        return TypeAst(pos, [IdentifierAst(pos, "std")], [GenericIdentifierAst(pos, "U16", None)])

    @staticmethod
    def U32(pos: int = -1):
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst
        return TypeAst(pos, [IdentifierAst(pos, "std")], [GenericIdentifierAst(pos, "U32", None)])

    @staticmethod
    def U64(pos: int = -1):
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst
        return TypeAst(pos, [IdentifierAst(pos, "std")], [GenericIdentifierAst(pos, "U64", None)])

    @staticmethod
    def U128(pos: int = -1):
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst
        return TypeAst(pos, [IdentifierAst(pos, "std")], [GenericIdentifierAst(pos, "U128", None)])

    @staticmethod
    def U256(pos: int = -1):
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst
        return TypeAst(pos, [IdentifierAst(pos, "std")], [GenericIdentifierAst(pos, "U256", None)])

    @staticmethod
    def I8(pos: int = -1):
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst
        return TypeAst(pos, [IdentifierAst(pos, "std")], [GenericIdentifierAst(pos, "I8", None)])

    @staticmethod
    def I16(pos: int = -1):
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst
        return TypeAst(pos, [IdentifierAst(pos, "std")], [GenericIdentifierAst(pos, "I16", None)])

    @staticmethod
    def I32(pos: int = -1):
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst
        return TypeAst(pos, [IdentifierAst(pos, "std")], [GenericIdentifierAst(pos, "I32", None)])

    @staticmethod
    def I64(pos: int = -1):
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst
        return TypeAst(pos, [IdentifierAst(pos, "std")], [GenericIdentifierAst(pos, "I64", None)])

    @staticmethod
    def I128(pos: int = -1):
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst
        return TypeAst(pos, [IdentifierAst(pos, "std")], [GenericIdentifierAst(pos, "I128", None)])

    @staticmethod
    def I256(pos: int = -1):
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst
        return TypeAst(pos, [IdentifierAst(pos, "std")], [GenericIdentifierAst(pos, "I256", None)])

    @staticmethod
    def F8(pos: int = -1):
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst
        return TypeAst(pos, [IdentifierAst(pos, "std")], [GenericIdentifierAst(pos, "F8", None)])

    @staticmethod
    def F16(pos: int = -1):
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst
        return TypeAst(pos, [IdentifierAst(pos, "std")], [GenericIdentifierAst(pos, "F16", None)])

    @staticmethod
    def F32(pos: int = -1):
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst
        return TypeAst(pos, [IdentifierAst(pos, "std")], [GenericIdentifierAst(pos, "F32", None)])

    @staticmethod
    def F64(pos: int = -1):
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst
        return TypeAst(pos, [IdentifierAst(pos, "std")], [GenericIdentifierAst(pos, "F64", None)])

    @staticmethod
    def F128(pos: int = -1):
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst
        return TypeAst(pos, [IdentifierAst(pos, "std")], [GenericIdentifierAst(pos, "F128", None)])

    @staticmethod
    def F256(pos: int = -1):
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst
        return TypeAst(pos, [IdentifierAst(pos, "std")], [GenericIdentifierAst(pos, "F256", None)])

    @staticmethod
    def Self(pos: int = -1):
        from SPPCompiler.SemanticAnalysis import TypeAst, GenericIdentifierAst
        return TypeAst(pos, [], [GenericIdentifierAst(pos, "Self", None)])

    @staticmethod
    def Void(pos: int = -1):
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst
        return TypeAst(pos, [IdentifierAst(pos, "std")], [GenericIdentifierAst(pos, "Void", None)])

    @staticmethod
    def Bool(pos: int = -1):
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst
        return TypeAst(pos, [IdentifierAst(pos, "std")], [GenericIdentifierAst(pos, "Bool", None)])

    @staticmethod
    def BigInt(pos: int = -1):
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst
        return TypeAst(pos, [IdentifierAst(pos, "std")], [GenericIdentifierAst(pos, "BigInt", None)])

    @staticmethod
    def BigDec(pos: int = -1):
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst
        return TypeAst(pos, [IdentifierAst(pos, "std")], [GenericIdentifierAst(pos, "BigDec", None)])

    @staticmethod
    def Str(pos: int = -1):
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst
        return TypeAst(pos, [IdentifierAst(pos, "std")], [GenericIdentifierAst(pos, "Str", None)])

    @staticmethod
    def Rgx(pos: int = -1):
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst
        return TypeAst(pos, [IdentifierAst(pos, "std")], [GenericIdentifierAst(pos, "Rgx", None)])

    """
    @staticmethod
    def CtxRef(pos: int = -1):
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst
        return TypeAst(pos, [IdentifierAst(pos, "std")], [GenericIdentifierAst(pos, "CtxRef", None)])

    @staticmethod
    def CtxMut(pos: int = -1):
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst
        return TypeAst(pos, [IdentifierAst(pos, "std")], [GenericIdentifierAst(pos, "CtxMut", None)])

    @staticmethod
    def Fut(inner_type, pos: int = -1):
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst, GenericArgumentGroupAst, GenericTypeArgumentUnnamedAst, TokenAst
        from SPPCompiler.LexicalAnalysis.TokenType import TokenType
        inner_type = GenericTypeArgumentUnnamedAst(-1, inner_type)
        return TypeAst(pos, [IdentifierAst(pos, "std")], [GenericIdentifierAst(pos, "Fut", GenericArgumentGroupAst(-1, TokenAst.default(TokenType.TkBrackL), [inner_type], TokenAst.default(TokenType.TkBrackR)))])
    """

    @staticmethod
    def Arr(elem_type, size, pos: int = -1):
        # Import ASTs needed for the type and generic argument creation.
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst, GenericArgumentGroupAst
        from SPPCompiler.SemanticAnalysis import GenericCompArgumentUnnamedAst, GenericTypeArgumentUnnamedAst

        # Convert the element type and size into generic arguments and load them into a group for the array type.
        elem_type_generic = GenericTypeArgumentUnnamedAst(-1, elem_type)
        size_comp_generic = GenericCompArgumentUnnamedAst(-1, size)
        generics = GenericArgumentGroupAst.default(Seq([elem_type_generic, size_comp_generic]))
        return TypeAst(pos, Seq([IdentifierAst(pos, "std")]), Seq([GenericIdentifierAst(pos, "Arr", generics)]))

    @staticmethod
    def Opt(inner_type, pos: int = -1):
        # Import ASTs needed for the type and generic argument creation.
        from SPPCompiler.SemanticAnalysis import IdentifierAst, GenericIdentifierAst, TypeAst
        from SPPCompiler.SemanticAnalysis import GenericArgumentGroupAst, GenericTypeArgumentUnnamedAst

        # Convert the inner type into a generic argument and load it into a group for the optional type.
        inner_type_generic = GenericTypeArgumentUnnamedAst(-1, inner_type)
        generics = GenericArgumentGroupAst.default(Seq([inner_type_generic]))
        return TypeAst(pos, Seq([IdentifierAst(pos, "std")]), Seq([GenericIdentifierAst(pos, "Opt", generics)]))

    @staticmethod
    def Tup(inner_types, pos: int = -1):
        # Import ASTs needed for the type and generic argument creation.
        from SPPCompiler.SemanticAnalysis import IdentifierAst, GenericIdentifierAst, TypeAst
        from SPPCompiler.SemanticAnalysis import GenericArgumentGroupAst, GenericTypeArgumentUnnamedAst

        # Convert the inner types into generic arguments and load them into a group for the tuple type.
        inner_type_generics = inner_types.map(lambda x: GenericTypeArgumentUnnamedAst(-1, x))
        generics = GenericArgumentGroupAst.default(inner_type_generics)
        return TypeAst(pos, Seq([IdentifierAst(pos, "std")]), Seq([GenericIdentifierAst(pos, "Tup", generics)]))

    @staticmethod
    def Var(inner_types, pos: int = -1):
        # Import ASTs needed for the type and generic argument creation.
        from SPPCompiler.SemanticAnalysis import IdentifierAst, GenericIdentifierAst, TypeAst
        from SPPCompiler.SemanticAnalysis import GenericArgumentGroupAst, GenericTypeArgumentUnnamedAst

        # Convert the inner types into generic arguments and load them into a group for the variant type.
        inner_type_generics = inner_types.map(lambda x: GenericTypeArgumentUnnamedAst(-1, x))
        generics = GenericArgumentGroupAst.default(inner_type_generics)
        return TypeAst(pos, Seq([IdentifierAst(pos, "std")]), Seq([GenericIdentifierAst(pos, "Var", generics)]))

    @staticmethod
    def FunRef(param_types, return_type, pos: int = -1):  # param_types is a tuple
        # Import ASTs needed for the type and generic argument creation.
        from SPPCompiler.SemanticAnalysis import IdentifierAst, GenericIdentifierAst, TypeAst
        from SPPCompiler.SemanticAnalysis import GenericArgumentGroupAst, GenericTypeArgumentUnnamedAst

        # Convert the parameter/return type(s) into generic arguments and load them into a group for the function type.
        return_type_generic = GenericTypeArgumentUnnamedAst(-1, return_type)
        param_types_generic = GenericTypeArgumentUnnamedAst(-1, param_types)
        generics = GenericArgumentGroupAst.default(Seq([param_types_generic, return_type_generic]))
        return TypeAst(pos, Seq([IdentifierAst(pos, "std")]), Seq([GenericIdentifierAst(pos, "FunRef", generics)]))

    @staticmethod
    def FunMut(param_types, return_type, pos: int = -1):  # param_types is a tuple
        # Import ASTs needed for the type and generic argument creation.
        from SPPCompiler.SemanticAnalysis import IdentifierAst, GenericIdentifierAst, TypeAst
        from SPPCompiler.SemanticAnalysis import GenericArgumentGroupAst, GenericTypeArgumentUnnamedAst

        # Convert the parameter/return type(s) into generic arguments and load them into a group for the function type.
        param_types_generic = GenericTypeArgumentUnnamedAst(-1, param_types)
        return_type_generic = GenericTypeArgumentUnnamedAst(-1, return_type)
        generics = GenericArgumentGroupAst.default(Seq([param_types_generic, return_type_generic]))
        return TypeAst(pos, Seq([IdentifierAst(pos, "std")]), Seq([GenericIdentifierAst(pos, "FunMut", generics)]))

    @staticmethod
    def FunMov(param_types, return_type, pos: int = -1):  # param_types is a tuple
        # Import ASTs needed for the type and generic argument creation.
        from SPPCompiler.SemanticAnalysis import IdentifierAst, GenericIdentifierAst, TypeAst
        from SPPCompiler.SemanticAnalysis import GenericArgumentGroupAst, GenericTypeArgumentUnnamedAst

        # Convert the parameter/return type(s) into generic arguments and load them into a group for the function type.
        param_types_generic = GenericTypeArgumentUnnamedAst(-1, param_types)
        return_type_generic = GenericTypeArgumentUnnamedAst(-1, return_type)
        generics = GenericArgumentGroupAst.default(Seq([param_types_generic, return_type_generic]))
        return TypeAst(pos, Seq([IdentifierAst(pos, "std")]), Seq([GenericIdentifierAst(pos, "FunMov", generics)]))

    @staticmethod
    def GenRef(gen_type=None, ret_type=None, send_type=None, pos: int = -1):
        # Import ASTs needed for the type and generic argument creation.
        from SPPCompiler.SemanticAnalysis import IdentifierAst, GenericIdentifierAst, TypeAst
        from SPPCompiler.SemanticAnalysis import GenericArgumentGroupAst, GenericTypeArgumentUnnamedAst

        # Convert the gen/send type(s) into generic arguments and load them into a group for the generator type.
        gen_type = GenericTypeArgumentUnnamedAst(-1, gen_type or CommonTypes.Void())
        send_type = GenericTypeArgumentUnnamedAst(-1, send_type or CommonTypes.Void())
        generics = GenericArgumentGroupAst.default(Seq([gen_type, send_type]))
        return TypeAst(pos, Seq([IdentifierAst(pos, "std")]), Seq([GenericIdentifierAst(pos, "GenRef", generics)]))

    @staticmethod
    def GenMut(gen_type=None, ret_type=None, send_type=None, pos: int = -1):
        # Import ASTs needed for the type and generic argument creation.
        from SPPCompiler.SemanticAnalysis import IdentifierAst, GenericIdentifierAst, TypeAst
        from SPPCompiler.SemanticAnalysis import GenericArgumentGroupAst, GenericTypeArgumentUnnamedAst

        # Convert the gen/send type(s) into generic arguments and load them into a group for the generator type.
        gen_type = GenericTypeArgumentUnnamedAst(-1, gen_type or CommonTypes.Void())
        send_type = GenericTypeArgumentUnnamedAst(-1, send_type or CommonTypes.Void())
        generics = GenericArgumentGroupAst.default(Seq([gen_type, send_type]))
        return TypeAst(pos, Seq([IdentifierAst(pos, "std")]), Seq([GenericIdentifierAst(pos, "GenMut", generics)]))

    @staticmethod
    def GenMov(gen_type=None, ret_type=None, send_type=None, pos: int = -1):
        # Import ASTs needed for the type and generic argument creation.
        from SPPCompiler.SemanticAnalysis import IdentifierAst, GenericIdentifierAst, TypeAst
        from SPPCompiler.SemanticAnalysis import GenericArgumentGroupAst, GenericTypeArgumentUnnamedAst

        # Convert the gen/send type(s) into generic arguments and load them into a group for the generator type.
        gen_type = GenericTypeArgumentUnnamedAst(-1, gen_type or CommonTypes.Void())
        send_type = GenericTypeArgumentUnnamedAst(-1, send_type or CommonTypes.Void())
        generics = GenericArgumentGroupAst.default(Seq([gen_type, send_type]))
        return TypeAst(pos, Seq([IdentifierAst(pos, "std")]), Seq([GenericIdentifierAst(pos, "GenMov", generics)]))

    """
    @staticmethod
    def Copy(pos: int = -1):
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst
        return TypeAst(pos, [IdentifierAst(pos, "std")], [GenericIdentifierAst(pos, "Copy", None)])
    """
