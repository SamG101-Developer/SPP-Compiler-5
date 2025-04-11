from __future__ import annotations

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Utils.CodeInjection import CodeInjection
from SPPCompiler.SyntacticAnalysis.Parser import SppParser
from SPPCompiler.Utils.Sequence import Seq


class CommonTypes:
    @staticmethod
    def type_variant_to_convention(type: Asts.TypeAst) -> Asts.ConventionAst:

        match type.type_parts()[0].value[-3:].lower():
            case "mov":
                return Asts.ConventionMovAst(pos=type.pos)
            case "mut":
                return Asts.ConventionMutAst(pos=type.pos)
            case "ref":
                return Asts.ConventionRefAst(pos=type.pos)
            case _:
                raise ValueError(f"Invalid type variant: {type.type_parts()[0].value}")

    @staticmethod
    def U8(pos: int):
        return CodeInjection.inject_code(
            f"std::number::U8", SppParser.parse_type, pos_adjust=pos)

    @staticmethod
    def U16(pos: int):
        return CodeInjection.inject_code(
            f"std::number::U16", SppParser.parse_type, pos_adjust=pos)

    @staticmethod
    def U32(pos: int):
        return CodeInjection.inject_code(
            f"std::number::U32", SppParser.parse_type, pos_adjust=pos)

    @staticmethod
    def U64(pos: int):
        return CodeInjection.inject_code(
            f"std::number::U64", SppParser.parse_type, pos_adjust=pos)

    @staticmethod
    def U128(pos: int):
        return CodeInjection.inject_code(
            f"std::number::U128", SppParser.parse_type, pos_adjust=pos)

    @staticmethod
    def U256(pos: int):
        return CodeInjection.inject_code(
            f"std::number::U256", SppParser.parse_type, pos_adjust=pos)

    @staticmethod
    def I8(pos: int):
        return CodeInjection.inject_code(
            f"std::number::I8", SppParser.parse_type, pos_adjust=pos)

    @staticmethod
    def I16(pos: int):
        return CodeInjection.inject_code(
            f"std::number::I16", SppParser.parse_type, pos_adjust=pos)

    @staticmethod
    def I32(pos: int):
        return CodeInjection.inject_code(
            f"std::number::I32", SppParser.parse_type, pos_adjust=pos)

    @staticmethod
    def I64(pos: int):
        return CodeInjection.inject_code(
            f"std::number::I64", SppParser.parse_type, pos_adjust=pos)

    @staticmethod
    def I128(pos: int):
        return CodeInjection.inject_code(
            f"std::number::I128", SppParser.parse_type, pos_adjust=pos)

    @staticmethod
    def I256(pos: int):
        return CodeInjection.inject_code(
            f"std::number::I256", SppParser.parse_type, pos_adjust=pos)

    @staticmethod
    def F8(pos: int):
        return CodeInjection.inject_code(
            f"std::number::F8", SppParser.parse_type, pos_adjust=pos)

    @staticmethod
    def F16(pos: int):
        return CodeInjection.inject_code(
            f"std::number::F16", SppParser.parse_type, pos_adjust=pos)

    @staticmethod
    def F32(pos: int):
        return CodeInjection.inject_code(
            f"std::number::F32", SppParser.parse_type, pos_adjust=pos)

    @staticmethod
    def F64(pos: int):
        return CodeInjection.inject_code(
            f"std::number::F64", SppParser.parse_type, pos_adjust=pos)

    @staticmethod
    def F128(pos: int):
        return CodeInjection.inject_code(
            f"std::number::F128", SppParser.parse_type, pos_adjust=pos)

    @staticmethod
    def F256(pos: int):
        return CodeInjection.inject_code(
            f"std::number::F256", SppParser.parse_type, pos_adjust=pos)

    @staticmethod
    def BigInt(pos: int):
        return CodeInjection.inject_code(
            f"std::number::BigInt", SppParser.parse_type, pos_adjust=pos)

    @staticmethod
    def BigDec(pos: int):
        return CodeInjection.inject_code(
            f"std::number::BigDec", SppParser.parse_type, pos_adjust=pos)

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
