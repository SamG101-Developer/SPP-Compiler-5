from __future__ import annotations

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Utils.CodeInjection import CodeInjection
from SPPCompiler.SyntacticAnalysis.Parser import SppParser


class CommonTypes:
    @staticmethod
    def U8(pos: int):
        type = Asts.TypeSingleAst(pos, Asts.GenericIdentifierAst(pos, "U8"))
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "u8")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "number")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def U16(pos: int):
        type = Asts.TypeSingleAst(pos, Asts.GenericIdentifierAst(pos, "U16"))
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "u16")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "number")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def U32(pos: int):
        type = Asts.TypeSingleAst(pos, Asts.GenericIdentifierAst(pos, "U32"))
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "u32")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "number")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def U64(pos: int):
        type = Asts.TypeSingleAst(pos, Asts.GenericIdentifierAst(pos, "U64"))
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "u64")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "number")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def U128(pos: int):
        type = Asts.TypeSingleAst(pos, Asts.GenericIdentifierAst(pos, "U128"))
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "u128")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "number")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def U256(pos: int):
        type = Asts.TypeSingleAst(pos, Asts.GenericIdentifierAst(pos, "U256"))
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "u256")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "number")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def USize(pos: int):
        type = Asts.TypeSingleAst(pos, Asts.GenericIdentifierAst(pos, "USize"))
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "usize")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "number")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def I8(pos: int):
        type = Asts.TypeSingleAst(pos, Asts.GenericIdentifierAst(pos, "I8"))
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "i8")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "number")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def I16(pos: int):
        type = Asts.TypeSingleAst(pos, Asts.GenericIdentifierAst(pos, "I16"))
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "i16")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "number")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def I32(pos: int):
        type = Asts.TypeSingleAst(pos, Asts.GenericIdentifierAst(pos, "I32"))
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "i32")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "number")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def I64(pos: int):
        type = Asts.TypeSingleAst(pos, Asts.GenericIdentifierAst(pos, "I64"))
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "i64")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "number")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def I128(pos: int):
        type = Asts.TypeSingleAst(pos, Asts.GenericIdentifierAst(pos, "I128"))
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "i128")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "number")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def I256(pos: int):
        type = Asts.TypeSingleAst(pos, Asts.GenericIdentifierAst(pos, "I256"))
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "i256")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "number")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def F8(pos: int):
        type = Asts.TypeSingleAst(pos, Asts.GenericIdentifierAst(pos, "F8"))
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "f8")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "number")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def F16(pos: int):
        type = Asts.TypeSingleAst(pos, Asts.GenericIdentifierAst(pos, "F16"))
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "f16")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "number")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def F32(pos: int):
        type = Asts.TypeSingleAst(pos, Asts.GenericIdentifierAst(pos, "F32"))
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "f32")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "number")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def F64(pos: int):
        type = Asts.TypeSingleAst(pos, Asts.GenericIdentifierAst(pos, "F64"))
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "f64")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "number")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def F128(pos: int):
        type = Asts.TypeSingleAst(pos, Asts.GenericIdentifierAst(pos, "F128"))
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "f128")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "number")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def F256(pos: int):
        type = Asts.TypeSingleAst(pos, Asts.GenericIdentifierAst(pos, "F256"))
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "f256")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "number")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def BigInt(pos: int):
        type = Asts.TypeSingleAst(pos, Asts.GenericIdentifierAst(pos, "BigInt"))
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "bigint")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "number")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def BigDec(pos: int):
        type = Asts.TypeSingleAst(pos, Asts.GenericIdentifierAst(pos, "BigDec"))
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "bigdec")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "number")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def Void(pos: int):
        type = Asts.TypeSingleAst(pos, Asts.GenericIdentifierAst(pos, "Void"))
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "void")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def Bool(pos: int):
        type = Asts.TypeSingleAst(pos, Asts.GenericIdentifierAst(pos, "Bool"))
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "boolean")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def Str(pos: int):
        type = Asts.TypeSingleAst(pos, Asts.GenericIdentifierAst(pos, "Str"))
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "string")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def Copy(pos: int):
        type = Asts.TypeSingleAst(pos, Asts.GenericIdentifierAst(pos, "Copy"))
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "copy")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def Fut(pos: int, inner_type: Asts.TypeAst):
        generics = [Asts.GenericTypeArgumentUnnamedAst(pos, inner_type)]
        generics = Asts.GenericArgumentGroupAst(pos, arguments=generics)
        type = Asts.TypeSingleAst(pos, Asts.GenericIdentifierAst(pos, "Fut", generics))
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "future")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def Arr(pos: int, elem_type: Asts.TypeAst, size: Asts.IntegerLiteralAst):
        generics = [Asts.GenericTypeArgumentUnnamedAst(pos, elem_type), Asts.GenericCompArgumentUnnamedAst(pos, size)]
        generics = Asts.GenericArgumentGroupAst(pos, arguments=generics)
        type = Asts.TypeSingleAst(pos, Asts.GenericIdentifierAst(pos, "Arr", generics))
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "array")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def ArrDynamic(pos: int, elem_type: Asts.TypeAst) -> Asts.TypeAst:
        generics = [Asts.GenericTypeArgumentUnnamedAst(pos, elem_type)]
        generics = Asts.GenericArgumentGroupAst(pos, arguments=generics)
        type = Asts.TypeSingleAst(pos, Asts.GenericIdentifierAst(pos, "ArrDynamic", generics))
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "array")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def Opt(pos: int, inner_type: Asts.TypeAst):
        generics = [Asts.GenericTypeArgumentUnnamedAst(pos, inner_type)]
        generics = Asts.GenericArgumentGroupAst(pos, arguments=generics)
        type = Asts.TypeSingleAst(pos, Asts.GenericIdentifierAst(pos, "Opt", generics))
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "option")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def NoneType(pos: int):
        type = Asts.TypeSingleAst(pos, Asts.GenericIdentifierAst(pos, "None"))
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "option")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def Tup(pos: int, inner_types: list[Asts.TypeAst] = None):
        generics = [Asts.GenericTypeArgumentUnnamedAst(pos, v) for v in inner_types or []]
        generics = Asts.GenericArgumentGroupAst(pos, arguments=generics)
        type = Asts.TypeSingleAst(pos, Asts.GenericIdentifierAst(pos, "Tup", generics))
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "tuple")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def Var(pos: int, inner_types: list[Asts.TypeAst] = None):
        generics = [Asts.GenericTypeArgumentUnnamedAst(pos, v) for v in inner_types or []]
        generics = Asts.GenericArgumentGroupAst(pos, arguments=generics)
        type = Asts.TypeSingleAst(pos, Asts.GenericIdentifierAst(pos, "Var", generics))
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "variant")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def FunMov(pos: int, param_types: Asts.TypeAst, return_type: Asts.TypeAst):
        generics = [Asts.GenericTypeArgumentUnnamedAst(pos, param_types), Asts.GenericTypeArgumentUnnamedAst(pos, return_type)]
        generics = Asts.GenericArgumentGroupAst(pos, arguments=generics)
        type = Asts.TypeSingleAst(pos, Asts.GenericIdentifierAst(pos, "FunMov", generics))
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "function")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def FunMut(pos: int, param_types: Asts.TypeAst, return_type: Asts.TypeAst):
        generics = [Asts.GenericTypeArgumentUnnamedAst(pos, param_types), Asts.GenericTypeArgumentUnnamedAst(pos, return_type)]
        generics = Asts.GenericArgumentGroupAst(pos, arguments=generics)
        type = Asts.TypeSingleAst(pos, Asts.GenericIdentifierAst(pos, "FunMut", generics))
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "function")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def FunRef(pos: int, param_types: Asts.TypeAst, return_type: Asts.TypeAst):
        generics = [Asts.GenericTypeArgumentUnnamedAst(pos, param_types), Asts.GenericTypeArgumentUnnamedAst(pos, return_type)]
        generics = Asts.GenericArgumentGroupAst(pos, arguments=generics)
        type = Asts.TypeSingleAst(pos, Asts.GenericIdentifierAst(pos, "FunRef", generics))
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "function")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def Single(pos: int, internal_type: Asts.TypeAst):
        generics = [Asts.GenericTypeArgumentUnnamedAst(pos, internal_type)]
        generics = Asts.GenericArgumentGroupAst(pos, arguments=generics)
        type = Asts.TypeSingleAst(pos, Asts.GenericIdentifierAst(pos, "Single", generics))
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "single")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def Gen(pos: int, yield_type: Asts.TypeAst = None, send_type: Asts.TypeAst = None):
        generics = [Asts.GenericTypeArgumentUnnamedAst(pos, yield_type), Asts.GenericTypeArgumentUnnamedAst(pos, send_type)]
        generics = Asts.GenericArgumentGroupAst(pos, arguments=generics)
        type = Asts.TypeSingleAst(pos, Asts.GenericIdentifierAst(pos, "Gen", generics))
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "generator")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def GenOnce(pos: int, yield_type: Asts.TypeAst = None, send_type: Asts.TypeAst = None):
        generics = [Asts.GenericTypeArgumentUnnamedAst(pos, yield_type), Asts.GenericTypeArgumentUnnamedAst(pos, send_type)]
        generics = Asts.GenericArgumentGroupAst(pos, arguments=generics)
        type = Asts.TypeSingleAst(pos, Asts.GenericIdentifierAst(pos, "GenOnce", generics))
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "generator")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def GenOpt(pos: int, yield_type: Asts.TypeAst = None, send_type: Asts.TypeAst = None):
        generics = [Asts.GenericTypeArgumentUnnamedAst(pos, yield_type), Asts.GenericTypeArgumentUnnamedAst(pos, send_type)]
        generics = Asts.GenericArgumentGroupAst(pos, arguments=generics)
        type = Asts.TypeSingleAst(pos, Asts.GenericIdentifierAst(pos, "GenOpt", generics))
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "generator")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def GenRes(pos: int, yield_type: Asts.TypeAst = None, err_type: Asts.TypeAst = None, send_type: Asts.TypeAst = None):
        generics = [Asts.GenericTypeArgumentUnnamedAst(pos, yield_type), Asts.GenericTypeArgumentUnnamedAst(pos, err_type), Asts.GenericTypeArgumentUnnamedAst(pos, send_type)]
        generics = Asts.GenericArgumentGroupAst(pos, arguments=generics)
        type = Asts.TypeSingleAst(pos, Asts.GenericIdentifierAst(pos, "GenRes", generics))
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "generator")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def Generated(pos: int, yield_type: Asts.TypeAst = None) -> Asts.TypeAst:
        generics = [Asts.GenericTypeArgumentUnnamedAst(pos, yield_type)]
        generics = Asts.GenericArgumentGroupAst(pos, arguments=generics)
        type = Asts.TypeSingleAst(pos, Asts.GenericIdentifierAst(pos, "Generated", generics))
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "generator")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def GeneratedOpt(pos: int, yield_type: Asts.TypeAst = None) -> Asts.TypeAst:
        generics = [Asts.GenericTypeArgumentUnnamedAst(pos, yield_type)]
        generics = Asts.GenericArgumentGroupAst(pos, arguments=generics)
        type = Asts.TypeSingleAst(pos, Asts.GenericIdentifierAst(pos, "GeneratedOpt", generics))
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "generator")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def GeneratedRes(pos: int, yield_type: Asts.TypeAst = None, err_type: Asts.TypeAst = None) -> Asts.TypeAst:
        generics = [Asts.GenericTypeArgumentUnnamedAst(pos, yield_type), Asts.GenericTypeArgumentUnnamedAst(pos, err_type)]
        generics = Asts.GenericArgumentGroupAst(pos, arguments=generics)
        type = Asts.TypeSingleAst(pos, Asts.GenericIdentifierAst(pos, "GeneratedRes", generics))
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
    def Self(pos: int):
        return Asts.TypeSingleAst(
            pos=pos,
            name=Asts.GenericIdentifierAst(
                pos=pos,
                value="Self"
            )
        )


class CommonTypesPrecompiled:
    EMPTY_TUP: Asts.TypeAst = "Pending..."
    EMPTY_ARR: Asts.TypeAst = "Pending..."
    EMPTY_ARR_DYNAMIC: Asts.TypeAst = "Pending..."
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
    I8: Asts.TypeAst = "Pending..."
    I16: Asts.TypeAst = "Pending..."
    I32: Asts.TypeAst = "Pending..."
    I64: Asts.TypeAst = "Pending..."
    I128: Asts.TypeAst = "Pending..."
    I256: Asts.TypeAst = "Pending..."
    USIZE: Asts.TypeAst = "Pending..."
    BOOL: Asts.TypeAst = "Pending..."
    STR: Asts.TypeAst = "Pending..."

    @staticmethod
    def initialize():
        CommonTypesPrecompiled.EMPTY_TUP = CommonTypes.Tup(pos=0).without_generics
        CommonTypesPrecompiled.EMPTY_ARR = CommonTypes.Arr(pos=0, elem_type=Asts.Ast(), size=Asts.Ast()).without_generics
        CommonTypesPrecompiled.EMPTY_ARR_DYNAMIC = CommonTypes.ArrDynamic(pos=0, elem_type=Asts.Ast()).without_generics
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
        CommonTypesPrecompiled.I8 = CommonTypes.I8(pos=0).without_generics
        CommonTypesPrecompiled.I16 = CommonTypes.I16(pos=0).without_generics
        CommonTypesPrecompiled.I32 = CommonTypes.I32(pos=0).without_generics
        CommonTypesPrecompiled.I64 = CommonTypes.I64(pos=0).without_generics
        CommonTypesPrecompiled.I128 = CommonTypes.I128(pos=0).without_generics
        CommonTypesPrecompiled.I256 = CommonTypes.I256(pos=0).without_generics
        CommonTypesPrecompiled.USIZE = CommonTypes.USize(pos=0).without_generics
        CommonTypesPrecompiled.BOOL = CommonTypes.Bool(pos=0).without_generics
        CommonTypesPrecompiled.STR = CommonTypes.Str(pos=0).without_generics


__all__ = [
    "CommonTypes",
    "CommonTypesPrecompiled"]
