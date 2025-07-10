from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, Optional

from llvmlite import ir

from SPPCompiler.CodeGen import LlvmExternalSymbolRegister
from SPPCompiler.CodeGen.Mangle import Mangler
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstFunctionUtils import AstFunctionUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import AstPrinter, ast_printer_method
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Utils.CompilerStages import PreProcessingContext
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors
from SPPCompiler.Utils.FastDeepcopy import fast_deepcopy
from SPPCompiler.Utils.Sequence import Seq, SequenceUtils


@dataclass(slots=True)
class FunctionPrototypeAst(Asts.Ast, Asts.Mixins.VisibilityEnabledAst):
    annotations: Seq[Asts.AnnotationAst] = field(default_factory=Seq)
    tok_fun: Asts.TokenAst = field(default=None)
    name: Asts.IdentifierAst = field(default=None)
    generic_parameter_group: Asts.GenericParameterGroupAst = field(default=None)
    function_parameter_group: Asts.FunctionParameterGroupAst = field(default=None)
    tok_arrow: Asts.TokenAst = field(default=None)
    return_type: Asts.TypeAst = field(default=None)
    where_block: Asts.WhereBlockAst = field(default=None)
    body: Asts.FunctionImplementationAst = field(default=None)

    _orig: Optional[Asts.IdentifierAst] = field(default=None, kw_only=True, repr=False)
    _abstract: Optional[Asts.AnnotationAst] = field(default=None, kw_only=True, repr=False)
    _virtual: Optional[Asts.AnnotationAst] = field(default=None, kw_only=True, repr=False)
    _non_implemented: Optional[Asts.AnnotationAst] = field(default=None, kw_only=True, repr=False)
    _cold: Optional[Asts.AnnotationAst] = field(default=None, kw_only=True, repr=False)
    _hot: Optional[Asts.AnnotationAst] = field(default=None, kw_only=True, repr=False)

    def __post_init__(self) -> None:
        self.tok_fun = self.tok_fun or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.KwFun)
        self.function_parameter_group = self.function_parameter_group or Asts.FunctionParameterGroupAst()
        self.generic_parameter_group = self.generic_parameter_group or Asts.GenericParameterGroupAst()
        self.where_block = self.where_block or Asts.WhereBlockAst()
        self.body = self.body or Asts.FunctionImplementationAst()
        self.tok_arrow = self.tok_arrow or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkArrowR)
        self._orig = self._orig or Asts.IdentifierAst(pos=self.pos, value="<anonymous>")

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            SequenceUtils.print(printer, self.annotations, sep="\n"),
            self.tok_fun.print(printer) + " ",
            self.name.print(printer) if self.name else "",
            self.generic_parameter_group.print(printer),
            self.function_parameter_group.print(printer) + " ",
            self.tok_arrow.print(printer) + " ",
            self.return_type.print(printer),
            self.where_block.print(printer),
            self.body.print(printer)]
        return "".join(string)

    @ast_printer_method
    def print_signature(self, printer: AstPrinter, owner: Asts.TypeAst = None) -> str:
        string = [
            self._orig.print(printer),
            self.generic_parameter_group.print(printer),
            self.function_parameter_group.print(printer) + " ",
            self.tok_arrow.print(printer) + " ",
            self.return_type.print(printer),
            self.where_block.print(printer)]
        if owner:
            string.insert(0, owner.print(printer) + "::")
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.body.pos_end

    def pre_process(self, ctx: PreProcessingContext) -> None:
        Asts.Ast.pre_process(self, ctx)

        # Substitute the "Self" parameter's type with the name of the method.
        generic_substitution = Asts.GenericTypeArgumentNamedAst(pos=0, name=CommonTypes.Self(pos=0), value=ctx.name)
        generic_substitution = [generic_substitution]
        if not isinstance(ctx, Asts.ModulePrototypeAst) and self.function_parameter_group.get_self_param():
            self.function_parameter_group.get_self_param()._true_self_type = ctx.name
            self.function_parameter_group.get_self_param().type = self.function_parameter_group.get_self_param().type.substituted_generics(generic_substitution)
        for p in self.function_parameter_group.params:
            p.type = p.type.substituted_generics(generic_substitution)
        self.return_type = self.return_type.substituted_generics(generic_substitution)

        # Pre-process the annotations.
        for a in self.annotations:
            a.pre_process(self)

        # Convert the "fun" function to a "sup" superimposition of a "Fun[Mov|Mut|Ref]" type over a mock type.
        mock_class_name = Asts.TypeSingleAst.from_identifier(self.name.to_function_identifier())
        function_type = self._deduce_mock_class_type()
        function_call = Asts.IdentifierAst(self.name.pos, "call")

        # If this is the first overload being converted, then the class needs to be made for the type.
        if not [m for m in ctx.body.members if isinstance(m, Asts.ClassPrototypeAst) and m.name.without_generics == mock_class_name.without_generics]:
            mock_class_ast = Asts.ClassPrototypeAst(
                name=mock_class_name)
            mock_constant_ast = Asts.CmpStatementAst(
                name=self.name, type=mock_class_name, value=Asts.ObjectInitializerAst(class_type=mock_class_name))
            ctx.body.members.append(mock_class_ast)
            ctx.body.members.append(mock_constant_ast)

        # Superimpose the function type over the mock class. Todo: switch to parser?
        function_ast = self
        function_ast._orig = self.name
        mock_superimposition_body = Asts.SupImplementationAst(members=[function_ast])
        mock_superimposition = Asts.SupPrototypeExtensionAst(
            pos=self.pos, generic_parameter_group=self.generic_parameter_group.opt_to_req(), name=mock_class_name,
            super_class=function_type, where_block=self.where_block, body=mock_superimposition_body, _ctx=self._ctx)
        ctx.body.members.insert(0, mock_superimposition)
        ctx.body.members.remove(self)

    def generate_top_level_scopes(self, sm: ScopeManager) -> None:
        # Create a new scope for the function.
        sm.create_and_move_into_new_scope(f"<function#{self._orig}#{self.pos}>", self)
        Asts.Ast.generate_top_level_scopes(self, sm)

        # If there is a self parameter in a free function, throw an error.
        if self.function_parameter_group.get_self_param() and isinstance(self._ctx, Asts.ModulePrototypeAst):
            raise SemanticErrors.ParameterSelfOutsideSuperimpositionError().add(
                self.function_parameter_group.get_self_param(), self).scopes(sm.current_scope)

        # Run top level scope logic for the annotations.
        for a in self.annotations:
            a.generate_top_level_scopes(sm)

        # Ensure the function return type does not have a convention.
        if c := self.return_type.convention:
            raise SemanticErrors.InvalidConventionLocationError().add(
                c, self.return_type, "function return type").scopes(sm.current_scope)

        # Generate the generic parameters and attributes of the function.
        for p in self.generic_parameter_group.parameters:
            p.generate_top_level_scopes(sm)

        # Move out of the function scope.
        sm.move_out_of_current_scope()

    def generate_top_level_aliases(self, sm: ScopeManager, **kwargs) -> None:
        # Skip the class scope (no sup-scope work to do).
        sm.move_to_next_scope()
        sm.move_out_of_current_scope()

    def qualify_types(self, sm: ScopeManager, **kwargs) -> None:
        sm.move_to_next_scope()
        self.generic_parameter_group.qualify_types(sm, **kwargs)
        sm.move_out_of_current_scope()

    def load_super_scopes(self, sm: ScopeManager, **kwargs) -> None:
        sm.move_to_next_scope()

        for p in self.function_parameter_group.params:
            p.type.analyse_semantics(sm, **kwargs)
        self.return_type.analyse_semantics(sm, **kwargs)

        sm.move_out_of_current_scope()

    def pre_analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        sm.move_to_next_scope()

        # Get the owner scope for function conflict checking.
        match self._ctx:
            case Asts.ModulePrototypeAst(): type_scope = sm.current_scope.parent_module
            case _: type_scope = self._ctx._scope.get_symbol(self._ctx.name).scope

        # Check for function conflicts.
        if conflict := AstFunctionUtils.check_for_conflicting_overload(sm.current_scope, type_scope, self):
            raise SemanticErrors.FunctionPrototypeConflictError().add(
                self._orig, conflict._orig).scopes(sm.current_scope)

        sm.move_out_of_current_scope()

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        sm.move_to_next_scope()

        # Analyse the semantics of everything except the body (subclasses handle this).
        for a in self.annotations:
            a.analyse_semantics(sm, **kwargs)

        self.generic_parameter_group.analyse_semantics(sm, **kwargs)
        self.function_parameter_group.analyse_semantics(sm, **kwargs)

        # Repeat the check here for generic substitution return types.
        self.return_type.analyse_semantics(sm, **kwargs)
        if c := self.return_type.convention:
            raise SemanticErrors.InvalidConventionLocationError().add(
                c, self.return_type, "function return type").scopes(sm.current_scope)

        self.where_block.analyse_semantics(sm, **kwargs)

        # Subclasses will finish analysis and exit the scope.

    def check_memory(self, sm: ScopeManager, **kwargs) -> None:
        # Check the memory of the function body.
        sm.move_to_next_scope()
        self.function_parameter_group.check_memory(sm, **kwargs)
        self.body.check_memory(sm, **kwargs)
        sm.move_out_of_current_scope()

    def code_gen_pass_1(self, sm: ScopeManager, llvm_module: ir.Module, **kwargs) -> None:
        # Generate the LLVM code for the function.
        sm.move_to_next_scope()

        # Load ffi functions. Todo: check this.
        if str(sm.current_scope.ancestors[-2].name) == "ffi":
            dll_name = str(sm.current_scope.ancestors[-3].name)
            dll_path = os.path.join(kwargs["root_path"], "ffi", dll_name, "lib", dll_name + ".dll")
            LlvmExternalSymbolRegister.register_external_functions(self, dll_path, sm)

        # Get the parameter types and return type for the function.
        types = [p.type for p in self.function_parameter_group.params] + [self.return_type]
        if self.function_parameter_group.get_self_param(): types.pop(0)
        type_symbols = [sm.current_scope.get_symbol(t) for t in types]

        # Any generic function is not generated; only substituted prototypes are.
        if all([type_symbol.llvm_info for type_symbol in type_symbols]):
            llvm_parameter_types = [sm.current_scope.get_symbol(p.type).llvm_info.llvm_type for p in self.function_parameter_group.get_non_self_params()]
            llvm_return_type = sm.current_scope.get_symbol(self.return_type).llvm_info.llvm_type
            llvm_function_type = ir.FunctionType(llvm_return_type, llvm_parameter_types)
            llvm_function = ir.Function(llvm_module, llvm_function_type, Mangler.mangle_function_name(sm.current_scope.parent, self))

        # Skip all function body scopes, as they are handled in the second pass.
        while sm.current_scope is not self._scope.final_child_scope():
            sm.move_to_next_scope()

    def _deduce_mock_class_type(self) -> Asts.TypeAst:
        # Module-level functions are always FunRef.
        if isinstance(self._ctx, Asts.ModulePrototypeAst) or not self.function_parameter_group.get_self_param():
            return CommonTypes.FunRef(self.pos, CommonTypes.Tup(self.pos, [p.type for p in self.function_parameter_group.params]), self.return_type)

        # Class methods with "self" are the FunMov type.
        if self.function_parameter_group.get_self_param().convention is None:
            return CommonTypes.FunMov(self.pos, CommonTypes.Tup(self.pos, [p.type for p in self.function_parameter_group.params]), self.return_type)

        # Class methods with "&mut self" are the FunMut type.
        if isinstance(self.function_parameter_group.get_self_param().convention, Asts.ConventionMutAst):
            return CommonTypes.FunMut(self.pos, CommonTypes.Tup(self.pos, [p.type for p in self.function_parameter_group.params]), self.return_type)

        # Class methods with "&self" are the FunRef type.
        if isinstance(self.function_parameter_group.get_self_param().convention, Asts.ConventionRefAst):
            return CommonTypes.FunRef(self.pos, CommonTypes.Tup(self.pos, [p.type for p in self.function_parameter_group.params]), self.return_type)

        raise NotImplementedError(f"Unknown convention for function {self.name}")

    def __deepcopy__(self, memodict: Dict = None) -> FunctionPrototypeAst:
        # Copy all attributes except for "_protected" attributes, which are re-linked by reference.
        return type(self)(
            self.pos, self.annotations, self.tok_fun,
            fast_deepcopy(self.name), fast_deepcopy(self.generic_parameter_group),
            fast_deepcopy(self.function_parameter_group), self.tok_arrow, fast_deepcopy(self.return_type),
            fast_deepcopy(self.where_block), self.body, _ctx=self._ctx, _orig=self._orig, _scope=None,
            _abstract=self._abstract, _virtual=self._virtual, _non_implemented=self._non_implemented)


__all__ = [
    "FunctionPrototypeAst"]
