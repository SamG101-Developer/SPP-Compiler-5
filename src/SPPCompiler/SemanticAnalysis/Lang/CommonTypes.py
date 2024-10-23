from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst


class CommonTypes:
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

    @staticmethod
    def Arr(elem_type, pos: int = -1):  # todo: array size too
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst, GenericArgumentGroupAst, GenericTypeArgumentUnnamedAst, TokenAst
        from SPPCompiler.LexicalAnalysis.TokenType import TokenType
        elem_type = GenericArgumentGroupAst(-1, TokenAst.default(TokenType.TkBrackL), [GenericTypeArgumentUnnamedAst(-1, elem_type)], TokenAst.default(TokenType.TkBrackR))
        return TypeAst(pos, [IdentifierAst(pos, "std")], [GenericIdentifierAst(pos, "Arr", elem_type)])
    """

    @staticmethod
    def Opt(inner_type, pos: int = -1):
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst, GenericArgumentGroupAst, GenericTypeArgumentUnnamedAst, TokenAst
        from SPPCompiler.LexicalAnalysis.TokenType import TokenType
        inner_type = GenericTypeArgumentUnnamedAst(-1, inner_type)
        return TypeAst(pos, [IdentifierAst(pos, "std")], [GenericIdentifierAst(pos, "Opt", GenericArgumentGroupAst(-1, TokenAst.default(TokenType.TkBrackL), [inner_type], TokenAst.default(TokenType.TkBrackR)))])

    @staticmethod
    def Tup(types, pos: int = -1):
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst, GenericArgumentGroupAst, GenericTypeArgumentUnnamedAst, TokenAst
        from SPPCompiler.LexicalAnalysis.TokenType import TokenType
        types = GenericArgumentGroupAst(-1, TokenAst.default(TokenType.TkBrackL), [GenericTypeArgumentUnnamedAst(-1, x) for x in types], TokenAst.default(TokenType.TkBrackR))
        return TypeAst(pos, [IdentifierAst(pos, "std")], [GenericIdentifierAst(pos, "Tup", types)])

    @staticmethod
    def Var(types, pos: int = -1):
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst, GenericArgumentGroupAst, GenericTypeArgumentUnnamedAst, TokenAst
        from SPPCompiler.LexicalAnalysis.TokenType import TokenType
        types = GenericArgumentGroupAst(-1, TokenAst.default(TokenType.TkBrackL), [GenericTypeArgumentUnnamedAst(-1, x) for x in types], TokenAst.default(TokenType.TkBrackR))
        return TypeAst(pos, [IdentifierAst(pos, "std")], [GenericIdentifierAst(pos, "Var", types)])

    @staticmethod
    def FunRef(param_types, return_type, pos: int = -1):  # param_types is a tuple
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst
        from SPPCompiler.SemanticAnalysis import GenericArgumentGroupAst, GenericTypeArgumentUnnamedAst
        return_type_generic = GenericTypeArgumentUnnamedAst(-1, return_type)
        param_types_generic = GenericTypeArgumentUnnamedAst(-1, param_types)
        types = GenericArgumentGroupAst.default([return_type_generic, param_types_generic])
        return TypeAst(pos, [IdentifierAst(pos, "std")], [GenericIdentifierAst(pos, "FunRef", types)])

    @staticmethod
    def FunMut(param_types, return_type, pos: int = -1):  # param_types is a tuple
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst
        from SPPCompiler.SemanticAnalysis import GenericArgumentGroupAst, GenericTypeArgumentUnnamedAst
        return_type_generic = GenericTypeArgumentUnnamedAst(-1, return_type)
        param_types_generic = GenericTypeArgumentUnnamedAst(-1, param_types)
        types = GenericArgumentGroupAst.default([return_type_generic, param_types_generic])
        return TypeAst(pos, [IdentifierAst(pos, "std")], [GenericIdentifierAst(pos, "FunMut", types)])

    @staticmethod
    def FunMov(param_types, return_type, pos: int = -1):  # param_types is a tuple
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst
        from SPPCompiler.SemanticAnalysis import GenericArgumentGroupAst, GenericTypeArgumentUnnamedAst
        return_type_generic = GenericTypeArgumentUnnamedAst(-1, return_type)
        param_types_generic = GenericTypeArgumentUnnamedAst(-1, param_types)
        types = GenericArgumentGroupAst.default([return_type_generic, param_types_generic])
        return TypeAst(pos, [IdentifierAst(pos, "std")], [GenericIdentifierAst(pos, "FunMov", types)])

    """
    @staticmethod
    def GenRef(gen_type=None, ret_type=None, send_type=None, pos: int = -1):
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst, GenericArgumentGroupAst, GenericTypeArgumentUnnamedAst, TokenAst
        from SPPCompiler.LexicalAnalysis.TokenType import TokenType
        gen_type = GenericTypeArgumentUnnamedAst(-1, gen_type or CommonTypes.void())
        send_type = GenericTypeArgumentUnnamedAst(-1, send_type or CommonTypes.void())
        return TypeAst(pos, [IdentifierAst(pos, "std")], [GenericIdentifierAst(pos, "GenRef", GenericArgumentGroupAst(-1, TokenAst.default(TokenType.TkBrackL), [gen_type, send_type], TokenAst.default(TokenType.TkBrackR)))])

    @staticmethod
    def GenMut(gen_type=None, ret_type=None, send_type=None, pos: int = -1):
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst, GenericArgumentGroupAst, GenericTypeArgumentUnnamedAst, TokenAst
        from SPPCompiler.LexicalAnalysis.TokenType import TokenType
        gen_type = GenericTypeArgumentUnnamedAst(-1, gen_type or CommonTypes.void())
        send_type = GenericTypeArgumentUnnamedAst(-1, send_type or CommonTypes.void())
        return TypeAst(pos, [IdentifierAst(pos, "std")], [GenericIdentifierAst(pos, "GenMut", GenericArgumentGroupAst(-1, TokenAst.default(TokenType.TkBrackL), [gen_type, send_type], TokenAst.default(TokenType.TkBrackR)))])

    @staticmethod
    def GenMov(gen_type=None, ret_type=None, send_type=None, pos: int = -1):
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst, GenericArgumentGroupAst, GenericTypeArgumentUnnamedAst, TokenAst
        from SPPCompiler.LexicalAnalysis.TokenType import TokenType
        gen_type = GenericTypeArgumentUnnamedAst(-1, gen_type or CommonTypes.void())
        send_type = GenericTypeArgumentUnnamedAst(-1, send_type or CommonTypes.void())
        return TypeAst(pos, [IdentifierAst(pos, "std")], [GenericIdentifierAst(pos, "GenMov", GenericArgumentGroupAst(-1, TokenAst.default(TokenType.TkBrackL), [gen_type, send_type], TokenAst.default(TokenType.TkBrackR)))])

    @staticmethod
    def Copy(pos: int = -1):
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TypeAst, GenericIdentifierAst
        return TypeAst(pos, [IdentifierAst(pos, "std")], [GenericIdentifierAst(pos, "Copy", None)])
    """
