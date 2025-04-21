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
    def Arr(pos: int, elem_type: Asts.TypeAst, size: Asts.ExpressionAst):
        return CodeInjection.inject_code(
            f"std::array::Arr[{elem_type}, {size}]", SppParser.parse_type, pos_adjust=pos)

    @staticmethod
    def Opt(pos: int, inner_type: Asts.TypeAst):
        return CodeInjection.inject_code(
            f"std::option::Opt[{inner_type}]", SppParser.parse_type, pos_adjust=pos)

    @staticmethod
    def Tup(pos: int, inner_types: Seq[Asts.TypeAst] = None):
        return CodeInjection.inject_code(
            f"std::tuple::Tup[{', '.join((inner_types or Seq()).map(str))}]", SppParser.parse_type, pos_adjust=pos)

    @staticmethod
    def Var(pos: int, inner_types: Seq[Asts.TypeAst] = None):
        return CodeInjection.inject_code(
            f"std::variant::Var[{', '.join((inner_types or Seq()).map(str))}]", SppParser.parse_type, pos_adjust=pos)

    @staticmethod
    def FunRef(pos: int, param_types: Seq[Asts.TypeAst], return_type: Asts.TypeAst):
        return CodeInjection.inject_code(
            f"std::function::FunRef[{param_types}, {return_type}]", SppParser.parse_type, pos_adjust=pos)

    @staticmethod
    def FunMut(pos: int, param_types: Seq[Asts.TypeAst], return_type: Asts.TypeAst):
        return CodeInjection.inject_code(
            f"std::function::FunMut[{param_types}, {return_type}]", SppParser.parse_type, pos_adjust=pos)

    @staticmethod
    def FunMov(pos: int, param_types: Seq[Asts.TypeAst], return_type: Asts.TypeAst):
        return CodeInjection.inject_code(
            f"std::function::FunMov[{param_types}, {return_type}]", SppParser.parse_type, pos_adjust=pos)

    @staticmethod
    def Gen(pos: int, yield_type: Asts.TypeAst = None, send_type: Asts.TypeAst = None):
        return CodeInjection.inject_code(
            f"std::generator::Gen[{yield_type}, {send_type}]", SppParser.parse_type, pos_adjust=pos)

    @staticmethod
    def GenOnce(pos: int, yield_type: Asts.TypeAst = None):
        return CodeInjection.inject_code(
            f"std::generator::Gen[{yield_type}]", SppParser.parse_type, pos_adjust=pos)

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
        return CodeInjection.inject_code(f"Self", SppParser.parse_type, pos_adjust=pos)


class CommonTypesPrecompiled:
    EMPTY_TUPLE: Asts.TypeAst = "Pending..."
    EMPTY_ARRAY: Asts.TypeAst = "Pending..."
    EMPTY_GENERATOR: Asts.TypeAst = "Pending..."
    EMPTY_VARIANT: Asts.TypeAst = "Pending..."
    EMPTY_VOID: Asts.TypeAst = "Pending..."

    @staticmethod
    def initialize():
        CommonTypesPrecompiled.EMPTY_TUPLE = CommonTypes.Tup(pos=0).without_generics()
        CommonTypesPrecompiled.EMPTY_ARRAY = CommonTypes.Arr(pos=0, elem_type=None, size=None).without_generics()
        CommonTypesPrecompiled.EMPTY_GENERATOR = CommonTypes.Gen(pos=0).without_generics()
        CommonTypesPrecompiled.EMPTY_VARIANT = CommonTypes.Var(pos=0).without_generics()
        CommonTypesPrecompiled.EMPTY_VOID = CommonTypes.Void(pos=0).without_generics()


__all__ = [
    "CommonTypes",
    "CommonTypesPrecompiled"]
