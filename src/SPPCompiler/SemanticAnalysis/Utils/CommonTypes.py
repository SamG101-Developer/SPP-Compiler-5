from __future__ import annotations

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Utils.CodeInjection import CodeInjection
from SPPCompiler.SyntacticAnalysis.Parser import SppParser


class CommonTypes:
    @staticmethod
    def Never(pos: int):
        type = Asts.TypeIdentifierAst.never_type(pos)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "never")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def U8(pos: int):
        type = Asts.TypeIdentifierAst(pos, "U8")
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "number")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def U16(pos: int):
        type = Asts.TypeIdentifierAst(pos, "U16")
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "number")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def U32(pos: int):
        type = Asts.TypeIdentifierAst(pos, "U32")
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "number")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def U64(pos: int):
        type = Asts.TypeIdentifierAst(pos, "U64")
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "number")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def U128(pos: int):
        type = Asts.TypeIdentifierAst(pos, "U128")
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "number")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def U256(pos: int):
        type = Asts.TypeIdentifierAst(pos, "U256")
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "number")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def USize(pos: int):
        type = Asts.TypeIdentifierAst(pos, "USize")
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "number")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def S8(pos: int):
        type = Asts.TypeIdentifierAst(pos, "S8")
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "number")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def S16(pos: int):
        type = Asts.TypeIdentifierAst(pos, "S16")
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "number")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def S32(pos: int):
        type = Asts.TypeIdentifierAst(pos, "S32")
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "number")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def S64(pos: int):
        type = Asts.TypeIdentifierAst(pos, "S64")
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "number")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def S128(pos: int):
        type = Asts.TypeIdentifierAst(pos, "S128")
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "number")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def S256(pos: int):
        type = Asts.TypeIdentifierAst(pos, "S256")
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "number")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def SSize(pos: int):
        type = Asts.TypeIdentifierAst(pos, "SSize")
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "number")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def F8(pos: int):
        type = Asts.TypeIdentifierAst(pos, "F8")
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "number")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def F16(pos: int):
        type = Asts.TypeIdentifierAst(pos, "F16")
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "number")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def F32(pos: int):
        type = Asts.TypeIdentifierAst(pos, "F32")
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "number")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def F64(pos: int):
        type = Asts.TypeIdentifierAst(pos, "F64")
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "number")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def F128(pos: int):
        type = Asts.TypeIdentifierAst(pos, "F128")
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "number")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def F256(pos: int):
        type = Asts.TypeIdentifierAst(pos, "F256")
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "number")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def BigInt(pos: int):
        type = Asts.TypeIdentifierAst(pos, "BigInt")
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "bigint")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "bignum")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def BigDec(pos: int):
        type = Asts.TypeIdentifierAst(pos, "BigDec")
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "bigdec")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "bignum")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def Void(pos: int):
        type = Asts.TypeIdentifierAst(pos, "Void")
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "void")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def Bool(pos: int):
        type = Asts.TypeIdentifierAst(pos, "Bool")
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "boolean")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def Str(pos: int):
        type = Asts.TypeIdentifierAst(pos, "Str")
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "string")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def Copy(pos: int):
        type = Asts.TypeIdentifierAst(pos, "Copy")
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "copy")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def Fut(pos: int, inner_type: Asts.TypeAst):
        generics = [Asts.GenericTypeArgumentUnnamedAst(pos, inner_type)]
        generics = Asts.GenericArgumentGroupAst(pos, arguments=generics)
        type = Asts.TypeIdentifierAst(pos, "Fut", generics)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "future")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def Arr(pos: int, elem_type: Asts.TypeAst, size: Asts.IntegerLiteralAst):
        generics = [Asts.GenericTypeArgumentUnnamedAst(pos, elem_type), Asts.GenericCompArgumentUnnamedAst(pos, size)]
        generics = Asts.GenericArgumentGroupAst(pos, arguments=generics)
        type = Asts.TypeIdentifierAst(pos, "Arr", generics)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "array")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def Slice(pos: int, elem_type: Asts.TypeAst) -> Asts.TypeAst:
        generics = [Asts.GenericTypeArgumentUnnamedAst(pos, elem_type)]
        generics = Asts.GenericArgumentGroupAst(pos, arguments=generics)
        type = Asts.TypeIdentifierAst(pos, "Slice", generics)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "slice")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def Opt(pos: int, inner_type: Asts.TypeAst):
        generics = [Asts.GenericTypeArgumentUnnamedAst(pos, inner_type)]
        generics = Asts.GenericArgumentGroupAst(pos, arguments=generics)
        type = Asts.TypeIdentifierAst(pos, "Opt", generics)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "option")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def NoneType(pos: int):
        type = Asts.TypeIdentifierAst(pos, "None")
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "option")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def Tup(pos: int, inner_types: list[Asts.TypeAst] = None):
        generics = [Asts.GenericTypeArgumentUnnamedAst(pos, v) for v in inner_types or []]
        generics = Asts.GenericArgumentGroupAst(pos, arguments=generics)
        type = Asts.TypeIdentifierAst(pos, "Tup", generics)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "tuple")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def Var(pos: int, inner_types: list[Asts.TypeAst] = None):
        generics = [Asts.GenericTypeArgumentUnnamedAst(pos, v) for v in inner_types or []]
        generics = Asts.GenericArgumentGroupAst(pos, arguments=generics)
        type = Asts.TypeIdentifierAst(pos, "Var", generics)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "variant")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def FunMov(pos: int, param_types: Asts.TypeAst, return_type: Asts.TypeAst):
        generics = [Asts.GenericTypeArgumentUnnamedAst(pos, param_types), Asts.GenericTypeArgumentUnnamedAst(pos, return_type)]
        generics = Asts.GenericArgumentGroupAst(pos, arguments=generics)
        type = Asts.TypeIdentifierAst(pos, "FunMov", generics)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "function")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def FunMut(pos: int, param_types: Asts.TypeAst, return_type: Asts.TypeAst):
        generics = [Asts.GenericTypeArgumentUnnamedAst(pos, param_types), Asts.GenericTypeArgumentUnnamedAst(pos, return_type)]
        generics = Asts.GenericArgumentGroupAst(pos, arguments=generics)
        type = Asts.TypeIdentifierAst(pos, "FunMut", generics)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "function")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def FunRef(pos: int, param_types: Asts.TypeAst, return_type: Asts.TypeAst):
        generics = [Asts.GenericTypeArgumentUnnamedAst(pos, param_types), Asts.GenericTypeArgumentUnnamedAst(pos, return_type)]
        generics = Asts.GenericArgumentGroupAst(pos, arguments=generics)
        type = Asts.TypeIdentifierAst(pos, "FunRef", generics)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "function")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def Single(pos: int, internal_type: Asts.TypeAst):
        generics = [Asts.GenericTypeArgumentUnnamedAst(pos, internal_type)]
        generics = Asts.GenericArgumentGroupAst(pos, arguments=generics)
        type = Asts.TypeIdentifierAst(pos, "Single", generics)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "single")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def Gen(pos: int, yield_type: Asts.TypeAst = None, send_type: Asts.TypeAst = None):
        generics = [Asts.GenericTypeArgumentUnnamedAst(pos, yield_type), Asts.GenericTypeArgumentUnnamedAst(pos, send_type)]
        generics = Asts.GenericArgumentGroupAst(pos, arguments=generics)
        type = Asts.TypeIdentifierAst(pos, "Gen", generics)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "generator")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def GenOnce(pos: int, yield_type: Asts.TypeAst = None, send_type: Asts.TypeAst = None):
        generics = [Asts.GenericTypeArgumentUnnamedAst(pos, yield_type), Asts.GenericTypeArgumentUnnamedAst(pos, send_type)]
        generics = Asts.GenericArgumentGroupAst(pos, arguments=generics)
        type = Asts.TypeIdentifierAst(pos, "GenOnce", generics)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "generator")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def GenOpt(pos: int, yield_type: Asts.TypeAst = None, send_type: Asts.TypeAst = None):
        generics = [Asts.GenericTypeArgumentUnnamedAst(pos, yield_type), Asts.GenericTypeArgumentUnnamedAst(pos, send_type)]
        generics = Asts.GenericArgumentGroupAst(pos, arguments=generics)
        type = Asts.TypeIdentifierAst(pos, "GenOpt", generics)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "generator")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def GenRes(pos: int, yield_type: Asts.TypeAst = None, err_type: Asts.TypeAst = None, send_type: Asts.TypeAst = None):
        generics = [Asts.GenericTypeArgumentUnnamedAst(pos, yield_type), Asts.GenericTypeArgumentUnnamedAst(pos, err_type), Asts.GenericTypeArgumentUnnamedAst(pos, send_type)]
        generics = Asts.GenericArgumentGroupAst(pos, arguments=generics)
        type = Asts.TypeIdentifierAst(pos, "GenRes", generics)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "generator")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def Generated(pos: int, yield_type: Asts.TypeAst = None) -> Asts.TypeAst:
        generics = [Asts.GenericTypeArgumentUnnamedAst(pos, yield_type)]
        generics = Asts.GenericArgumentGroupAst(pos, arguments=generics)
        type = Asts.TypeIdentifierAst(pos, "Generated", generics)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "generator")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def GeneratedOpt(pos: int, yield_type: Asts.TypeAst = None) -> Asts.TypeAst:
        generics = [Asts.GenericTypeArgumentUnnamedAst(pos, yield_type)]
        generics = Asts.GenericArgumentGroupAst(pos, arguments=generics)
        type = Asts.TypeIdentifierAst(pos, "GeneratedOpt", generics)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "generator")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def GeneratedRes(pos: int, yield_type: Asts.TypeAst = None, err_type: Asts.TypeAst = None) -> Asts.TypeAst:
        generics = [Asts.GenericTypeArgumentUnnamedAst(pos, yield_type), Asts.GenericTypeArgumentUnnamedAst(pos, err_type)]
        generics = Asts.GenericArgumentGroupAst(pos, arguments=generics)
        type = Asts.TypeIdentifierAst(pos, "GeneratedRes", generics)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "generator")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def DerefRef(pos: int, inner_type: Asts.TypeAst = None):
        return CodeInjection.inject_code(
            f"std::ops::deref::DerefRef[{inner_type}]", SppParser.parse_type, pos_adjust=pos)

    @staticmethod
    def DerefMut(pos: int, inner_type: Asts.TypeAst = None):
        return CodeInjection.inject_code(
            f"std::ops::deref::DerefMut[{inner_type}]", SppParser.parse_type, pos_adjust=pos)

    @staticmethod
    def Try(pos: int, output: Asts.TypeAst = None, residual: Asts.TypeAst = None):
        return CodeInjection.inject_code(
            f"std::ops::try::Try[{output}, {residual}]", SppParser.parse_type, pos_adjust=pos)

    @staticmethod
    def Self(pos: int):
        return Asts.TypeIdentifierAst(pos=pos, value="Self")


class CommonTypesPrecompiled:
    EMPTY_TUP: Asts.TypeAst = "Pending..."
    EMPTY_ARR: Asts.TypeAst = "Pending..."
    EMPTY_SLICE: Asts.TypeAst = "Pending..."
    EMPTY_GEN: Asts.TypeAst = "Pending..."
    EMPTY_GEN_ONCE: Asts.TypeAst = "Pending..."
    EMPTY_GEN_OPT: Asts.TypeAst = "Pending..."
    EMPTY_GEN_RES: Asts.TypeAst = "Pending..."
    EMPTY_GENERATED: Asts.TypeAst = "Pending..."
    EMPTY_GENERATED_OPT: Asts.TypeAst = "Pending..."
    EMPTY_GENERATED_RES: Asts.TypeAst = "Pending..."
    EMPTY_VAR: Asts.TypeAst = "Pending..."
    EMPTY_FUN_MOV: Asts.TypeAst = "Pending..."
    EMPTY_FUN_MUT: Asts.TypeAst = "Pending..."
    EMPTY_FUN_REF: Asts.TypeAst = "Pending..."
    EMPTY_SINGLE: Asts.TypeAst = "Pending..."
    VOID: Asts.TypeAst = "Pending..."
    COPY: Asts.TypeAst = "Pending..."
    BIGINT: Asts.TypeAst = "Pending..."
    BIGDEC: Asts.TypeAst = "Pending..."
    F8: Asts.TypeAst = "Pending..."
    F16: Asts.TypeAst = "Pending..."
    F32: Asts.TypeAst = "Pending..."
    F64: Asts.TypeAst = "Pending..."
    F128: Asts.TypeAst = "Pending..."
    F256: Asts.TypeAst = "Pending..."
    U8: Asts.TypeAst = "Pending..."
    U16: Asts.TypeAst = "Pending..."
    U32: Asts.TypeAst = "Pending..."
    U64: Asts.TypeAst = "Pending..."
    U128: Asts.TypeAst = "Pending..."
    U256: Asts.TypeAst = "Pending..."
    USIZE: Asts.TypeAst = "Pending..."
    S8: Asts.TypeAst = "Pending..."
    S16: Asts.TypeAst = "Pending..."
    S32: Asts.TypeAst = "Pending..."
    S64: Asts.TypeAst = "Pending..."
    S128: Asts.TypeAst = "Pending..."
    S256: Asts.TypeAst = "Pending..."
    SSIZE: Asts.TypeAst = "Pending..."
    BOOL: Asts.TypeAst = "Pending..."
    STR: Asts.TypeAst = "Pending..."
    TRY: Asts.TypeAst = "Pending..."
    NEVER: Asts.TypeAst = "Pending..."

    @staticmethod
    def initialize():
        CommonTypesPrecompiled.EMPTY_TUP = CommonTypes.Tup(pos=0).without_generics
        CommonTypesPrecompiled.EMPTY_ARR = CommonTypes.Arr(pos=0, elem_type=Asts.Ast(), size=Asts.Ast()).without_generics
        CommonTypesPrecompiled.EMPTY_SLICE = CommonTypes.Slice(pos=0, elem_type=Asts.Ast()).without_generics
        CommonTypesPrecompiled.EMPTY_GEN = CommonTypes.Gen(pos=0, yield_type=Asts.Ast(), send_type=Asts.Ast()).without_generics
        CommonTypesPrecompiled.EMPTY_GEN_ONCE = CommonTypes.GenOnce(pos=0, yield_type=Asts.Ast(), send_type=Asts.Ast()).without_generics
        CommonTypesPrecompiled.EMPTY_GEN_OPT = CommonTypes.GenOpt(pos=0, yield_type=Asts.Ast(), send_type=Asts.Ast()).without_generics
        CommonTypesPrecompiled.EMPTY_GEN_RES = CommonTypes.GenRes(pos=0, yield_type=Asts.Ast(), err_type=Asts.Ast(), send_type=Asts.Ast()).without_generics
        CommonTypesPrecompiled.EMPTY_GENERATED = CommonTypes.Generated(pos=0, yield_type=Asts.Ast()).without_generics
        CommonTypesPrecompiled.EMPTY_GENERATED_OPT = CommonTypes.GeneratedOpt(pos=0, yield_type=Asts.Ast()).without_generics
        CommonTypesPrecompiled.EMPTY_GENERATED_RES = CommonTypes.GeneratedRes(pos=0, yield_type=Asts.Ast(), err_type=Asts.Ast()).without_generics
        CommonTypesPrecompiled.EMPTY_VAR = CommonTypes.Var(pos=0).without_generics
        CommonTypesPrecompiled.EMPTY_FUN_MOV = CommonTypes.FunMov(pos=0, param_types=Asts.Ast(), return_type=Asts.Ast()).without_generics
        CommonTypesPrecompiled.EMPTY_FUN_MUT = CommonTypes.FunMut(pos=0, param_types=Asts.Ast(), return_type=Asts.Ast()).without_generics
        CommonTypesPrecompiled.EMPTY_FUN_REF = CommonTypes.FunRef(pos=0, param_types=Asts.Ast(), return_type=Asts.Ast()).without_generics
        CommonTypesPrecompiled.EMPTY_SINGLE = CommonTypes.Single(pos=0, internal_type=Asts.Ast()).without_generics
        CommonTypesPrecompiled.VOID = CommonTypes.Void(pos=0).without_generics
        CommonTypesPrecompiled.COPY = CommonTypes.Copy(pos=0).without_generics
        CommonTypesPrecompiled.BIGINT = CommonTypes.BigInt(pos=0).without_generics
        CommonTypesPrecompiled.BIGDEC = CommonTypes.BigDec(pos=0).without_generics
        CommonTypesPrecompiled.F8 = CommonTypes.F8(pos=0).without_generics
        CommonTypesPrecompiled.F16 = CommonTypes.F16(pos=0).without_generics
        CommonTypesPrecompiled.F32 = CommonTypes.F32(pos=0).without_generics
        CommonTypesPrecompiled.F64 = CommonTypes.F64(pos=0).without_generics
        CommonTypesPrecompiled.F128 = CommonTypes.F128(pos=0).without_generics
        CommonTypesPrecompiled.F256 = CommonTypes.F256(pos=0).without_generics
        CommonTypesPrecompiled.U8 = CommonTypes.U8(pos=0).without_generics
        CommonTypesPrecompiled.U16 = CommonTypes.U16(pos=0).without_generics
        CommonTypesPrecompiled.U32 = CommonTypes.U32(pos=0).without_generics
        CommonTypesPrecompiled.U64 = CommonTypes.U64(pos=0).without_generics
        CommonTypesPrecompiled.U128 = CommonTypes.U128(pos=0).without_generics
        CommonTypesPrecompiled.U256 = CommonTypes.U256(pos=0).without_generics
        CommonTypesPrecompiled.USIZE = CommonTypes.USize(pos=0).without_generics
        CommonTypesPrecompiled.S8 = CommonTypes.S8(pos=0).without_generics
        CommonTypesPrecompiled.S16 = CommonTypes.S16(pos=0).without_generics
        CommonTypesPrecompiled.S32 = CommonTypes.S32(pos=0).without_generics
        CommonTypesPrecompiled.S64 = CommonTypes.S64(pos=0).without_generics
        CommonTypesPrecompiled.S128 = CommonTypes.S128(pos=0).without_generics
        CommonTypesPrecompiled.S256 = CommonTypes.S256(pos=0).without_generics
        CommonTypesPrecompiled.SSIZE = CommonTypes.SSize(pos=0).without_generics
        CommonTypesPrecompiled.BOOL = CommonTypes.Bool(pos=0).without_generics
        CommonTypesPrecompiled.STR = CommonTypes.Str(pos=0).without_generics
        CommonTypesPrecompiled.TRY = CommonTypes.Try(pos=0).without_generics
        CommonTypesPrecompiled.NEVER = CommonTypes.Never(pos=0).without_generics


__all__ = [
    "CommonTypes",
    "CommonTypesPrecompiled"]
