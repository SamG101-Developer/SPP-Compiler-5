from __future__ import annotations

from llvmlite import ir

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstTypeUtils import AstTypeUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypesPrecompiled
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors


def spp_to_llvm_type(spp_type: Asts.TypeAst, sm: ScopeManager, *, is_return: bool = False) -> ir.Type:
    """
    All pointers returned from C Abi are mapped to Single[T] in S++, except for char* and const char* which are mapped
    to Str in S++.

    :param spp_type:
    :param sm:
    :param is_return:
    :return:
    """

    if spp_type.get_convention():
        return ir.PointerType(spp_to_llvm_type(spp_type.without_conventions(), sm))
    elif AstTypeUtils.symbolic_eq(spp_type, CommonTypesPrecompiled.F32, sm.current_scope, sm.current_scope):
        return ir.FloatType()
    elif AstTypeUtils.symbolic_eq(spp_type, CommonTypesPrecompiled.F64, sm.current_scope, sm.current_scope):
        return ir.DoubleType()
    elif AstTypeUtils.symbolic_eq(spp_type, CommonTypesPrecompiled.I8, sm.current_scope, sm.current_scope):
        return ir.IntType(8)
    elif AstTypeUtils.symbolic_eq(spp_type, CommonTypesPrecompiled.I16, sm.current_scope, sm.current_scope):
        return ir.IntType(16)
    elif AstTypeUtils.symbolic_eq(spp_type, CommonTypesPrecompiled.I32, sm.current_scope, sm.current_scope):
        return ir.IntType(32)
    elif AstTypeUtils.symbolic_eq(spp_type, CommonTypesPrecompiled.I64, sm.current_scope, sm.current_scope):
        return ir.IntType(64)
    elif AstTypeUtils.symbolic_eq(spp_type, CommonTypesPrecompiled.U8, sm.current_scope, sm.current_scope):
        return ir.IntType(8)
    elif AstTypeUtils.symbolic_eq(spp_type, CommonTypesPrecompiled.U16, sm.current_scope, sm.current_scope):
        return ir.IntType(16)
    elif AstTypeUtils.symbolic_eq(spp_type, CommonTypesPrecompiled.U32, sm.current_scope, sm.current_scope):
        return ir.IntType(32)
    elif AstTypeUtils.symbolic_eq(spp_type, CommonTypesPrecompiled.U64, sm.current_scope, sm.current_scope):
        return ir.IntType(64)
    elif AstTypeUtils.symbolic_eq(spp_type, CommonTypesPrecompiled.BOOL, sm.current_scope, sm.current_scope):
        return ir.IntType(1)
    elif AstTypeUtils.symbolic_eq(spp_type, CommonTypesPrecompiled.STR, sm.current_scope, sm.current_scope):
        return ir.ArrayType(ir.IntType(8), 0)
    elif AstTypeUtils.symbolic_eq(spp_type, CommonTypesPrecompiled.VOID, sm.current_scope, sm.current_scope):
        return ir.VoidType()
    elif AstTypeUtils.symbolic_eq(spp_type.without_generics(), CommonTypesPrecompiled.EMPTY_ARRAY_DYNAMIC, sm.current_scope, sm.current_scope):
        return ir.PointerType(spp_to_llvm_type(spp_type.type_parts()[0].generic_argument_group.arguments[0].value, sm))
    elif AstTypeUtils.symbolic_eq(spp_type.without_generics(), CommonTypesPrecompiled.EMPTY_ARRAY, sm.current_scope, sm.current_scope):
        n = int(spp_type.type_parts()[0].generic_argument_group.arguments[1].value.value.token_data)
        return ir.ArrayType(spp_to_llvm_type(spp_type.type_parts()[0].generic_argument_group.arguments[0].value, sm), n)
    elif is_return and AstTypeUtils.symbolic_eq(spp_type.without_generics(), CommonTypesPrecompiled.EMPTY_SINGLE, sm.current_scope, sm.current_scope):
        return ir.PointerType(spp_to_llvm_type(spp_type.type_parts()[0].generic_argument_group.arguments[0].value, sm))
    else:
        raise SemanticErrors.InvalidFfiSppTypeError().add(spp_type).scopes(sm.current_scope)
