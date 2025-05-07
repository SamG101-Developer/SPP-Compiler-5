from __future__ import annotations

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Utils.CodeInjection import CodeInjection
from SPPCompiler.SyntacticAnalysis.Parser import SppParser
from SPPCompiler.Utils.Sequence import Seq


class CommonTypes:
    @staticmethod
    def U8(pos: int):
        return CodeInjection.inject_code(
            f"std::number::u8::U8", SppParser.parse_type, pos_adjust=pos)

    @staticmethod
    def U16(pos: int):
        return CodeInjection.inject_code(
            f"std::number::u16::U16", SppParser.parse_type, pos_adjust=pos)

    @staticmethod
    def U32(pos: int):
        return CodeInjection.inject_code(
            f"std::number::u32::U32", SppParser.parse_type, pos_adjust=pos)

    @staticmethod
    def U64(pos: int):
        return CodeInjection.inject_code(
            f"std::number::u64::U64", SppParser.parse_type, pos_adjust=pos)

    @staticmethod
    def U128(pos: int):
        return CodeInjection.inject_code(
            f"std::number::u128::U128", SppParser.parse_type, pos_adjust=pos)

    @staticmethod
    def U256(pos: int):
        return CodeInjection.inject_code(
            f"std::number::u256::U256", SppParser.parse_type, pos_adjust=pos)

    @staticmethod
    def USize(pos: int):
        return CodeInjection.inject_code(
            f"std::number::usize::USize", SppParser.parse_type, pos_adjust=pos)

    @staticmethod
    def I8(pos: int):
        return CodeInjection.inject_code(
            f"std::number::i8::I8", SppParser.parse_type, pos_adjust=pos)

    @staticmethod
    def I16(pos: int):
        return CodeInjection.inject_code(
            f"std::number::i16::I16", SppParser.parse_type, pos_adjust=pos)

    @staticmethod
    def I32(pos: int):
        return CodeInjection.inject_code(
            f"std::number::i32::I32", SppParser.parse_type, pos_adjust=pos)

    @staticmethod
    def I64(pos: int):
        return CodeInjection.inject_code(
            f"std::number::i64::I64", SppParser.parse_type, pos_adjust=pos)

    @staticmethod
    def I128(pos: int):
        return CodeInjection.inject_code(
            f"std::number::i128::I128", SppParser.parse_type, pos_adjust=pos)

    @staticmethod
    def I256(pos: int):
        return CodeInjection.inject_code(
            f"std::number::i256::I256", SppParser.parse_type, pos_adjust=pos)

    @staticmethod
    def F8(pos: int):
        return CodeInjection.inject_code(
            f"std::number::f8::F8", SppParser.parse_type, pos_adjust=pos)

    @staticmethod
    def F16(pos: int):
        return CodeInjection.inject_code(
            f"std::number::f16::F16", SppParser.parse_type, pos_adjust=pos)

    @staticmethod
    def F32(pos: int):
        return CodeInjection.inject_code(
            f"std::number::f32::F32", SppParser.parse_type, pos_adjust=pos)

    @staticmethod
    def F64(pos: int):
        return CodeInjection.inject_code(
            f"std::number::f64::F64", SppParser.parse_type, pos_adjust=pos)

    @staticmethod
    def F128(pos: int):
        return CodeInjection.inject_code(
            f"std::number::f128::F128", SppParser.parse_type, pos_adjust=pos)

    @staticmethod
    def F256(pos: int):
        return CodeInjection.inject_code(
            f"std::number::f256::F256", SppParser.parse_type, pos_adjust=pos)

    @staticmethod
    def BigInt(pos: int):
        return CodeInjection.inject_code(
            f"std::number::bigint::BigInt", SppParser.parse_type, pos_adjust=pos)

    @staticmethod
    def BigDec(pos: int):
        return CodeInjection.inject_code(
            f"std::number::bigdec::BigDec", SppParser.parse_type, pos_adjust=pos)

    @staticmethod
    def Void(pos: int):
        return CodeInjection.inject_code(
            f"std::void::Void", SppParser.parse_type, pos_adjust=pos)

    @staticmethod
    def Bool(pos: int):
        return CodeInjection.inject_code(
            f"std::boolean::Bool", SppParser.parse_type, pos_adjust=pos)

    @staticmethod
    def Str(pos: int):
        return CodeInjection.inject_code(
            f"std::string::Str", SppParser.parse_type, pos_adjust=pos)

    @staticmethod
    def Copy(pos: int):
        return CodeInjection.inject_code(
            f"std::copy::Copy", SppParser.parse_type, pos_adjust=pos)

    @staticmethod
    def Fut(pos: int, inner_type: Asts.TypeAst):
        return CodeInjection.inject_code(
            f"std::future::Fut[{inner_type}]", SppParser.parse_type, pos_adjust=pos)

    @staticmethod
    def Arr(pos: int, elem_type: Asts.TypeAst, size: Asts.IntegerLiteralAst):
        generics = [Asts.GenericTypeArgumentUnnamedAst(value=elem_type), Asts.GenericCompArgumentUnnamedAst(value=size)]
        generics = Asts.GenericArgumentGroupAst(pos, arguments=generics)
        type = Asts.TypeSingleAst(pos, Asts.GenericIdentifierAst(pos, "Arr", generics))
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "array")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def ArrDynamic(pos: int, elem_type: Asts.TypeAst) -> Asts.TypeAst:
        generics = [Asts.GenericTypeArgumentUnnamedAst(value=elem_type)]
        generics = Asts.GenericArgumentGroupAst(pos, arguments=generics)
        type = Asts.TypeSingleAst(pos, Asts.GenericIdentifierAst(pos, "ArrDynamic", generics))
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "array")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def Opt(pos: int, inner_type: Asts.TypeAst):
        generics = [Asts.GenericTypeArgumentUnnamedAst(value=inner_type)]
        generics = Asts.GenericArgumentGroupAst(pos, arguments=generics)
        type = Asts.TypeSingleAst(pos, Asts.GenericIdentifierAst(pos, "Opt", generics))
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "option")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def Tup(pos: int, inner_types: Seq[Asts.TypeAst] = None):
        generics = [Asts.GenericTypeArgumentUnnamedAst(value=v) for v in inner_types or []]
        generics = Asts.GenericArgumentGroupAst(pos, arguments=generics)
        type = Asts.TypeSingleAst(pos, Asts.GenericIdentifierAst(pos, "Tup", generics))
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "tuple")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def Var(pos: int, inner_types: Seq[Asts.TypeAst] = None):
        generics = [Asts.GenericTypeArgumentUnnamedAst(value=v) for v in inner_types or []]
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
        generics = [Asts.GenericTypeArgumentUnnamedAst(value=internal_type)]
        generics = Asts.GenericArgumentGroupAst(pos, arguments=generics)
        type = Asts.TypeSingleAst(pos, Asts.GenericIdentifierAst(pos, "Single", generics))
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "single")), type)
        type = Asts.TypeUnaryExpressionAst(pos, Asts.TypeUnaryOperatorNamespaceAst(pos, Asts.IdentifierAst(pos, "std")), type)
        return type

    @staticmethod
    def Gen(pos: int, yield_type: Asts.TypeAst = None, send_type: Asts.TypeAst = None):
        return CodeInjection.inject_code(
            f"std::generator::Gen[{yield_type}, {send_type}]", SppParser.parse_type, pos_adjust=pos)

    @staticmethod
    def GenOnce(pos: int, yield_type: Asts.TypeAst = None):
        return CodeInjection.inject_code(
            f"std::generator::GenOnce[{yield_type}]", SppParser.parse_type, pos_adjust=pos)

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
    EMPTY_TUPLE: Asts.TypeAst = "Pending..."
    EMPTY_ARRAY: Asts.TypeAst = "Pending..."
    EMPTY_ARRAY_DYNAMIC: Asts.TypeAst = "Pending..."
    EMPTY_GENERATOR: Asts.TypeAst = "Pending..."
    EMPTY_VARIANT: Asts.TypeAst = "Pending..."
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
        CommonTypesPrecompiled.EMPTY_TUPLE = CommonTypes.Tup(pos=0).without_generics()
        CommonTypesPrecompiled.EMPTY_ARRAY = CommonTypes.Arr(pos=0, elem_type=Asts.Ast(), size=Asts.Ast()).without_generics()
        CommonTypesPrecompiled.EMPTY_ARRAY_DYNAMIC = CommonTypes.ArrDynamic(pos=0, elem_type=Asts.Ast()).without_generics()
        CommonTypesPrecompiled.EMPTY_GENERATOR = CommonTypes.Gen(pos=0).without_generics()
        CommonTypesPrecompiled.EMPTY_VARIANT = CommonTypes.Var(pos=0).without_generics()
        CommonTypesPrecompiled.EMPTY_FUN_MOV = CommonTypes.FunMov(pos=0, param_types=Asts.Ast(), return_type=Asts.Ast()).without_generics()
        CommonTypesPrecompiled.EMPTY_FUN_MUT = CommonTypes.FunMut(pos=0, param_types=Asts.Ast(), return_type=Asts.Ast()).without_generics()
        CommonTypesPrecompiled.EMPTY_FUN_REF = CommonTypes.FunRef(pos=0, param_types=Asts.Ast(), return_type=Asts.Ast()).without_generics()
        CommonTypesPrecompiled.EMPTY_SINGLE = CommonTypes.Single(pos=0, internal_type=Asts.Ast()).without_generics()
        CommonTypesPrecompiled.VOID = CommonTypes.Void(pos=0).without_generics()
        CommonTypesPrecompiled.COPY = CommonTypes.Copy(pos=0).without_generics()
        CommonTypesPrecompiled.BIGINT = CommonTypes.BigInt(pos=0).without_generics()
        CommonTypesPrecompiled.BIGDEC = CommonTypes.BigDec(pos=0).without_generics()
        CommonTypesPrecompiled.F8 = CommonTypes.F8(pos=0).without_generics()
        CommonTypesPrecompiled.F16 = CommonTypes.F16(pos=0).without_generics()
        CommonTypesPrecompiled.F32 = CommonTypes.F32(pos=0).without_generics()
        CommonTypesPrecompiled.F64 = CommonTypes.F64(pos=0).without_generics()
        CommonTypesPrecompiled.F128 = CommonTypes.F128(pos=0).without_generics()
        CommonTypesPrecompiled.F256 = CommonTypes.F256(pos=0).without_generics()
        CommonTypesPrecompiled.U8 = CommonTypes.U8(pos=0).without_generics()
        CommonTypesPrecompiled.U16 = CommonTypes.U16(pos=0).without_generics()
        CommonTypesPrecompiled.U32 = CommonTypes.U32(pos=0).without_generics()
        CommonTypesPrecompiled.U64 = CommonTypes.U64(pos=0).without_generics()
        CommonTypesPrecompiled.U128 = CommonTypes.U128(pos=0).without_generics()
        CommonTypesPrecompiled.U256 = CommonTypes.U256(pos=0).without_generics()
        CommonTypesPrecompiled.I8 = CommonTypes.I8(pos=0).without_generics()
        CommonTypesPrecompiled.I16 = CommonTypes.I16(pos=0).without_generics()
        CommonTypesPrecompiled.I32 = CommonTypes.I32(pos=0).without_generics()
        CommonTypesPrecompiled.I64 = CommonTypes.I64(pos=0).without_generics()
        CommonTypesPrecompiled.I128 = CommonTypes.I128(pos=0).without_generics()
        CommonTypesPrecompiled.I256 = CommonTypes.I256(pos=0).without_generics()
        CommonTypesPrecompiled.USIZE = CommonTypes.USize(pos=0).without_generics()
        CommonTypesPrecompiled.BOOL = CommonTypes.Bool(pos=0).without_generics()
        CommonTypesPrecompiled.STR = CommonTypes.Str(pos=0).without_generics()


__all__ = [
    "CommonTypes",
    "CommonTypesPrecompiled"]
