from __future__ import annotations

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.SemanticAnalysis.Meta.AstMutation import AstMutation
from SPPCompiler.SyntacticAnalysis.Parser import SppParser
from SPPCompiler.Utils.Sequence import Seq


class CommonTypes:
    @staticmethod
    def type_variant_to_convention(type: Asts.TypeAst) -> Asts.ConventionAst:

        match type.type_parts()[0].value[-3:].lower():
            case "mov":
                return Asts.ConventionMovAst()
            case "mut":
                return Asts.ConventionMutAst()
            case "ref":
                return Asts.ConventionRefAst()
            case _:
                raise ValueError(f"Invalid type variant: {type.type_parts()[0].value}")

    @staticmethod
    def U8(pos: int = -1):
        return AstMutation.inject_code(f"std::U8", SppParser.parse_type)

    @staticmethod
    def U16(pos: int = -1):
        return AstMutation.inject_code(f"std::U16", SppParser.parse_type)

    @staticmethod
    def U32(pos: int = -1):
        return AstMutation.inject_code(f"std::U32", SppParser.parse_type)

    @staticmethod
    def U64(pos: int = -1):
        return AstMutation.inject_code(f"std::U64", SppParser.parse_type)

    @staticmethod
    def U128(pos: int = -1):
        return AstMutation.inject_code(f"std::U128", SppParser.parse_type)

    @staticmethod
    def U256(pos: int = -1):
        return AstMutation.inject_code(f"std::U256", SppParser.parse_type)

    @staticmethod
    def I8(pos: int = -1):
        return AstMutation.inject_code(f"std::I8", SppParser.parse_type)

    @staticmethod
    def I16(pos: int = -1):
        return AstMutation.inject_code(f"std::I16", SppParser.parse_type)

    @staticmethod
    def I32(pos: int = -1):
        return AstMutation.inject_code(f"std::I32", SppParser.parse_type)

    @staticmethod
    def I64(pos: int = -1):
        return AstMutation.inject_code(f"std::I64", SppParser.parse_type)

    @staticmethod
    def I128(pos: int = -1):
        return AstMutation.inject_code(f"std::I128", SppParser.parse_type)

    @staticmethod
    def I256(pos: int = -1):
        return AstMutation.inject_code(f"std::I256", SppParser.parse_type)

    @staticmethod
    def F8(pos: int = -1):
        return AstMutation.inject_code(f"std::F8", SppParser.parse_type)

    @staticmethod
    def F16(pos: int = -1):
        return AstMutation.inject_code(f"std::F16", SppParser.parse_type)

    @staticmethod
    def F32(pos: int = -1):
        return AstMutation.inject_code(f"std::F32", SppParser.parse_type)

    @staticmethod
    def F64(pos: int = -1):
        return AstMutation.inject_code(f"std::F64", SppParser.parse_type)

    @staticmethod
    def F128(pos: int = -1):
        return AstMutation.inject_code(f"std::F128", SppParser.parse_type)

    @staticmethod
    def F256(pos: int = -1):
        return AstMutation.inject_code(f"std::F256", SppParser.parse_type)

    @staticmethod
    def Void(pos: int = -1):
        return AstMutation.inject_code(f"std::Void", SppParser.parse_type)

    @staticmethod
    def Bool(pos: int = -1):
        return AstMutation.inject_code(f"std::Bool", SppParser.parse_type)

    @staticmethod
    def BigInt(pos: int = -1):
        return AstMutation.inject_code(f"std::BigInt", SppParser.parse_type)

    @staticmethod
    def BigDec(pos: int = -1):
        return AstMutation.inject_code(f"std::BigDec", SppParser.parse_type)

    @staticmethod
    def Str(pos: int = -1):
        return AstMutation.inject_code(f"std::Str", SppParser.parse_type)

    @staticmethod
    def Copy(pos: int = -1):
        return AstMutation.inject_code(f"std::Copy", SppParser.parse_type)

    @staticmethod
    def Fut(inner_type, pos: int = -1):
        return AstMutation.inject_code(f"std::Fut[{inner_type}]", SppParser.parse_type)

    @staticmethod
    def Arr(elem_type, size, pos: int = -1):
        return AstMutation.inject_code(f"std::Arr[{elem_type}, {size}]", SppParser.parse_type)

    @staticmethod
    def Opt(inner_type, pos: int = -1):
        return AstMutation.inject_code(f"std::Opt[{inner_type}]", SppParser.parse_type)

    @staticmethod
    def Tup(inner_types: Seq = None, pos: int = -1):
        return AstMutation.inject_code(f"std::Tup[{', '.join((inner_types or Seq()).map(str))}]", SppParser.parse_type)

    @staticmethod
    def Var(inner_types: Seq = None, pos: int = -1):
        return AstMutation.inject_code(f"std::Var[{', '.join((inner_types or Seq()).map(str))}]", SppParser.parse_type)

    @staticmethod
    def Isc(inner_types: Seq = None, pos: int = -1):
        return AstMutation.inject_code(f"std::Isc[{', '.join((inner_types or Seq()).map(str))}]", SppParser.parse_type)

    @staticmethod
    def FunRef(param_types, return_type, pos: int = -1):
        return AstMutation.inject_code(f"std::FunRef[{param_types}, {return_type}]", SppParser.parse_type)

    @staticmethod
    def FunMut(param_types, return_type, pos: int = -1):
        return AstMutation.inject_code(f"std::FunMut[{param_types}, {return_type}]", SppParser.parse_type)

    @staticmethod
    def FunMov(param_types, return_type, pos: int = -1):
        return AstMutation.inject_code(f"std::FunMov[{param_types}, {return_type}]", SppParser.parse_type)

    @staticmethod
    def GenRef(gen_type=None, send_type=None, pos: int = -1):
        return AstMutation.inject_code(f"std::GenRef[{gen_type}, {send_type}]", SppParser.parse_type)

    @staticmethod
    def GenMut(gen_type=None, send_type=None, pos: int = -1):
        return AstMutation.inject_code(f"std::GenMut[{gen_type}, {send_type}]", SppParser.parse_type)

    @staticmethod
    def GenMov(gen_type=None, send_type=None, pos: int = -1):
        return AstMutation.inject_code(f"std::GenMov[{gen_type}, {send_type}]", SppParser.parse_type)

    @staticmethod
    def Self(pos: int = -1):
        # Todo: change
        return Asts.TypeSingleAst(pos=pos, name=Asts.GenericIdentifierAst(pos=pos, value="Self"))


class CommonTypesPrecompiled:
    EMPTY_TUPLE: Asts.TypeAst = "Pending..."
    EMPTY_ARRAY: Asts.TypeAst = "Pending..."

    @staticmethod
    def initialize():
        CommonTypesPrecompiled.EMPTY_TUPLE = CommonTypes.Tup().without_generics()
        CommonTypesPrecompiled.EMPTY_ARRAY = CommonTypes.Arr(None, 0).without_generics()


__all__ = [
    "CommonTypes",
    "CommonTypesPrecompiled"]
