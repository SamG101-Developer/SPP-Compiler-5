from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from llvmlite import ir as llvm

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstMutation import AstMutation
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.VisibilityEnabled import VisibilityEnabled
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import PreProcessingContext
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SyntacticAnalysis.Parser import SppParser
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class FunctionPrototypeAst(Ast, VisibilityEnabled):
    annotations: Seq[Asts.AnnotationAst] = field(default_factory=Seq)
    tok_fun: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.KwFun))
    name: Asts.IdentifierAst = field(default=None)
    generic_parameter_group: Asts.GenericParameterGroupAst = field(default_factory=lambda: Asts.GenericParameterGroupAst())
    function_parameter_group: Asts.FunctionParameterGroupAst = field(default_factory=lambda: Asts.FunctionParameterGroupAst())
    tok_arrow: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.TkArrowR))
    return_type: Asts.TypeAst = field(default=None)
    where_block: Asts.WhereBlockAst = field(default_factory=lambda: Asts.WhereBlockAst())
    body: Asts.FunctionImplementationAst = field(default_factory=lambda: Asts.FunctionImplementationAst())

    _orig: Optional[Asts.IdentifierAst] = field(default=None, kw_only=True, repr=False)
    _abstract: Optional[Asts.AnnotationAst] = field(default=None, kw_only=True, repr=False)
    _virtual: Optional[Asts.AnnotationAst] = field(default=None, kw_only=True, repr=False)
    _non_implemented: Optional[Asts.AnnotationAst] = field(default=None, kw_only=True, repr=False)
    _cold: Optional[Asts.AnnotationAst] = field(default=None, kw_only=True, repr=False)
    _hot: Optional[Asts.AnnotationAst] = field(default=None, kw_only=True, repr=False)

    def __post_init__(self) -> None:
        assert self.name
        assert self.return_type

    def __eq__(self, other: FunctionPrototypeAst) -> bool:
        # Check both ASTs are the same type and have the same name, generic parameter group, function parameter group,
        # return type and where block.
        return all([
            self.name == other.name,
            self.generic_parameter_group == other.generic_parameter_group,
            self.function_parameter_group == other.function_parameter_group,
            self.return_type == other.return_type,
            self.where_block == other.where_block])

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.annotations.print(printer, " "),
            self.tok_fun.print(printer) + " ",
            self.name.print(printer),
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

    def pre_process(self, context: PreProcessingContext) -> None:
        super().pre_process(context)

        # Substitute the "Self" parameter's type with the name of the method.
        if not isinstance(context, Asts.ModulePrototypeAst) and self.function_parameter_group.get_self():
            generic_substitution = Asts.GenericTypeArgumentNamedAst(pos=0, name=CommonTypes.Self(), value=context.name)
            generic_substitution = Seq([generic_substitution])
            self.function_parameter_group.get_self()._true_self_type = context.name
            self.function_parameter_group.get_self().type = self.function_parameter_group.get_self().type.sub_generics(generic_substitution)

        # Pre-process the annotations.
        for a in self.annotations:
            a.pre_process(self)

        # Convert the "fun" function to a "sup" superimposition of a "Fun[Mov|Mut|Ref]" type over a mock type.
        mock_class_name = AstMutation.inject_code(
            self.name.to_function_identifier().value, SppParser.parse_type, pos_adjust=self.pos)
        function_type = self._deduce_mock_class_type()
        function_call = Asts.IdentifierAst(self.name.pos, "call")

        # If this is the first overload being converted, then the class needs to be made for the type.
        if context.body.members.filter_to_type(Asts.ClassPrototypeAst).filter(lambda c: c.name == mock_class_name).is_empty():
            mock_class_ast = AstMutation.inject_code(
                f"cls {mock_class_name} {{}}",
                SppParser.parse_class_prototype, pos_adjust=self.pos)
            mock_constant_ast = AstMutation.inject_code(
                f"cmp {self.name}: {mock_class_name} = {mock_class_name}()",
                SppParser.parse_global_constant, pos_adjust=self.pos)
            context.body.members.append(mock_class_ast)
            context.body.members.append(mock_constant_ast)

        # Superimpose the function type over the mock class. Todo: switch to parser?
        function_ast = copy.deepcopy(self)
        function_ast._orig = self.name
        mock_superimposition_body = Asts.SupImplementationAst(members=Seq([function_ast]))
        mock_superimposition = Asts.SupPrototypeExtensionAst(
            pos=self.pos, generic_parameter_group=self.generic_parameter_group, name=mock_class_name,
            super_class=function_type, where_block=self.where_block, body=mock_superimposition_body, _ctx=self._ctx)
        context.body.members.insert(0, mock_superimposition)
        context.body.members.remove(self)

        # Pre-process the annotations of this function's duplicate.
        for a in function_ast.annotations:
            a.pre_process(function_ast)

    def generate_top_level_scopes(self, scope_manager: ScopeManager) -> None:
        # Create a new scope for the function.
        scope_manager.create_and_move_into_new_scope(f"<function:{self._orig}:{self.pos}>", self)
        super().generate_top_level_scopes(scope_manager)

        # Run top level scope logic for the annotations.
        for a in self.annotations:
            a.generate_top_level_scopes(scope_manager)

        # Ensure the function return type does not have a convention.
        if type(c := self.return_type.get_convention()) is not Asts.ConventionMovAst:
            raise SemanticErrors.InvalidConventionLocationError().add(c, self.return_type, "function return type").scopes(scope_manager.current_scope)

        # Generate the generic parameters and attributes of the function.
        for p in self.generic_parameter_group.parameters:
            p.generate_top_level_scopes(scope_manager)

        # Move out of the function scope.
        scope_manager.move_out_of_current_scope()

    def generate_top_level_aliases(self, scope_manager: ScopeManager, **kwargs) -> None:
        # Skip the class scope (no sup-scope work to do).
        scope_manager.move_to_next_scope()
        scope_manager.move_out_of_current_scope()

    def load_super_scopes(self, scope_manager: ScopeManager) -> None:
        from SPPCompiler.SemanticAnalysis.Meta.AstFunctions import AstFunctions, FunctionConflictCheckType

        scope_manager.move_to_next_scope()

        # Get the owner scope for function conflict checking.
        match self._ctx:
            case Asts.ModulePrototypeAst(): type_scope = scope_manager.current_scope.parent_module
            case _: type_scope = self._ctx._scope_cls

        # Check for function conflicts.
        if conflict := AstFunctions.check_for_conflicting_method(scope_manager.current_scope, type_scope, self, FunctionConflictCheckType.InvalidOverload):
            raise SemanticErrors.FunctionPrototypeConflictError().add(self._orig, conflict._orig).scopes(scope_manager.current_scope)

        # Type analysis (loads generic types for later)
        for p in self.function_parameter_group.parameters:
            p.type.analyse_semantics(scope_manager)
        self.return_type.analyse_semantics(scope_manager)
        self.return_type = scope_manager.current_scope.get_symbol(self.return_type).fq_name

        scope_manager.move_out_of_current_scope()

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        scope_manager.move_to_next_scope()

        # Analyse the semantics of everything except the body (subclasses handle this).
        for a in self.annotations:
            a.analyse_semantics(scope_manager, **kwargs)
        self.generic_parameter_group.analyse_semantics(scope_manager, **kwargs)
        self.function_parameter_group.analyse_semantics(scope_manager, **kwargs)
        self.return_type.analyse_semantics(scope_manager, **kwargs)
        self.where_block.analyse_semantics(scope_manager, **kwargs)

        # Subclasses will finish analysis and exit the scope.

    def generate_llvm_definitions(self, scope_handler: ScopeManager, llvm_module: llvm.Module = None, builder: llvm.IRBuilder = None, block: llvm.Block = None, **kwargs) -> Any:
        scope_handler.move_to_next_scope()

        # Generate the LLVM definition for the function prototype.
        llvm_parameter_types = self.function_parameter_group.generate_llvm_definitions(scope_handler, llvm_module)
        llvm_return_type = self.return_type.generate_llvm_definitions(scope_handler, llvm_module)
        llvm_function_type = llvm.FunctionType(llvm_return_type, llvm_parameter_types)
        llvm_function = llvm.Function(llvm_module, llvm_function_type, self.print_signature(AstPrinter()))

        # Use the FunctionImplementationAst to generate the LLVM declaration.
        self.body.generate_llvm_definitions(scope_handler, llvm_module, llvm_function=llvm_function)
        scope_handler.move_out_of_current_scope()

    def _deduce_mock_class_type(self) -> Asts.TypeAst:
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes

        # Module-level functions are always FunRef.
        if isinstance(self._ctx, Asts.ModulePrototypeAst) or not self.function_parameter_group.get_self():
            return CommonTypes.FunRef(CommonTypes.Tup(self.function_parameter_group.parameters.map_attr("type"), pos=self.pos), self.return_type, pos=self.pos)

        # Class methods with "self" are the FunMov type.
        if isinstance(self.function_parameter_group.get_self().convention, Asts.ConventionMovAst):
            return CommonTypes.FunMov(CommonTypes.Tup(self.function_parameter_group.parameters.map_attr("type"), pos=self.pos), self.return_type, pos=self.pos)

        # Class methods with "&mut self" are the FunMut type.
        if isinstance(self.function_parameter_group.get_self().convention, Asts.ConventionMutAst):
            return CommonTypes.FunMut(CommonTypes.Tup(self.function_parameter_group.parameters.map_attr("type"), pos=self.pos), self.return_type, pos=self.pos)

        # Class methods with "&self" are the FunRef type.
        if isinstance(self.function_parameter_group.get_self().convention, Asts.ConventionRefAst):
            return CommonTypes.FunRef(CommonTypes.Tup(self.function_parameter_group.parameters.map_attr("type"), pos=self.pos), self.return_type, pos=self.pos)

        raise NotImplementedError(f"Unknown convention for function {self.name}")

    def __deepcopy__(self, memodict: Dict = None) -> FunctionPrototypeAst:
        # Copy all attributes except for "_protected" attributes, which are re-linked by reference.
        return type(self)(
            self.pos, self.annotations, self.tok_fun,
            copy.deepcopy(self.name), copy.deepcopy(self.generic_parameter_group),
            copy.deepcopy(self.function_parameter_group), self.tok_arrow,
            copy.deepcopy(self.return_type), copy.deepcopy(self.where_block), copy.deepcopy(self.body),
            _ctx=self._ctx, _orig=self._orig, _scope=None, _abstract=self._abstract, _virtual=self._virtual,
            _non_implemented=self._non_implemented)


__all__ = ["FunctionPrototypeAst"]
