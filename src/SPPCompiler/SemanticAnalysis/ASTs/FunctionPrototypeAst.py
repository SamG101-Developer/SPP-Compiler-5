from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING, Any
import copy

from llvmlite import ir as llvm

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.VisibilityEnabled import VisibilityEnabled
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages, PreProcessingContext
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.AnnotationAst import AnnotationAst
    from SPPCompiler.SemanticAnalysis.ASTs.FunctionParameterGroupAst import FunctionParameterGroupAst
    from SPPCompiler.SemanticAnalysis.ASTs.GenericParameterGroupAst import GenericParameterGroupAst
    from SPPCompiler.SemanticAnalysis.ASTs.FunctionImplementationAst import FunctionImplementationAst
    from SPPCompiler.SemanticAnalysis.ASTs.ModulePrototypeAst import ModulePrototypeAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst
    from SPPCompiler.SemanticAnalysis.ASTs.WhereBlockAst import WhereBlockAst
    from SPPCompiler.SemanticAnalysis.ASTs.IdentifierAst import IdentifierAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class FunctionPrototypeAst(Ast, VisibilityEnabled, CompilerStages):
    annotations: Seq[AnnotationAst]
    tok_fun: TokenAst
    name: IdentifierAst
    generic_parameter_group: Optional[GenericParameterGroupAst]
    function_parameter_group: FunctionParameterGroupAst
    tok_arrow: TokenAst
    return_type: TypeAst
    where_block: Optional[WhereBlockAst]
    body: FunctionImplementationAst

    _orig: Optional[IdentifierAst] = field(default=None, kw_only=True, repr=False)
    _abstract: Optional[AnnotationAst] = field(default=None, kw_only=True, repr=False)
    _virtual: Optional[AnnotationAst] = field(default=None, kw_only=True, repr=False)
    _non_implemented: Optional[AnnotationAst] = field(default=None, kw_only=True, repr=False)
    _cold: Optional[AnnotationAst] = field(default=None, kw_only=True, repr=False)
    _hot: Optional[AnnotationAst] = field(default=None, kw_only=True, repr=False)

    def __post_init__(self) -> None:
        # Import the necessary classes to create default instances.
        from SPPCompiler.SemanticAnalysis import GenericParameterGroupAst
        from SPPCompiler.SemanticAnalysis import WhereBlockAst

        # Convert the annotations into a sequence, and create other defaults.
        self.annotations = Seq(self.annotations)
        self.generic_parameter_group = self.generic_parameter_group or GenericParameterGroupAst.default()
        self.where_block = self.where_block or WhereBlockAst.default()
        self.body = self.body or FunctionImplementationAst.default()

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
    def print_signature(self, printer: AstPrinter, owner: TypeAst = None) -> str:
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

    def pre_process(self, context: PreProcessingContext) -> None:
        from SPPCompiler.SemanticAnalysis import ClassPrototypeAst, ModulePrototypeAst, SupPrototypeInheritanceAst
        from SPPCompiler.SemanticAnalysis import TypeAst, SupImplementationAst
        from SPPCompiler.SemanticAnalysis.Meta.AstMutation import AstMutation
        from SPPCompiler.SyntacticAnalysis.Parser import SppParser
        super().pre_process(context)

        # Substitute the "Self" parameter's type with the name of the method.
        if not isinstance(context, ModulePrototypeAst) and self.function_parameter_group.get_self():
            self.function_parameter_group.get_self().type = context.name

        # Pre-process the annotations.
        for a in self.annotations:
            a.pre_process(self)

        # Convert the "fun" function to a "sup" superimposition of a "Fun[Mov|Mut|Ref]" type over a mock type.
        mock_class_name = TypeAst.from_function_identifier(self.name)
        function_type = self._deduce_mock_class_type()
        function_call = self._deduce_mock_class_call(function_type)

        # If this is the first overload being converted, then the class needs to be made for the type.
        if context.body.members.filter_to_type(ClassPrototypeAst).filter(lambda c: c.name == mock_class_name).is_empty():
            mock_class_ast = AstMutation.inject_code(
                f"cls {mock_class_name} {{}}",
                SppParser.parse_class_prototype)
            mock_constant_ast = AstMutation.inject_code(
                f"cmp {self.name}: {mock_class_name} = {mock_class_name}()",
                SppParser.parse_global_constant)
            context.body.members.append(mock_class_ast)
            context.body.members.append(mock_constant_ast)

        # Superimpose the function type over the mock class.
        function_ast = copy.deepcopy(self)
        function_ast._orig = self.name
        mock_superimposition_body = SupImplementationAst.default(Seq([function_ast]))
        mock_superimposition = SupPrototypeInheritanceAst(self.pos, None, self.generic_parameter_group, mock_class_name, self.where_block, mock_superimposition_body, None, function_type)
        context.body.members.insert(0, mock_superimposition)
        context.body.members.remove(self)

        # Pre-process the annotations of this function's duplicate.
        for a in function_ast.annotations:
            a.pre_process(function_ast)

    def generate_symbols(self, scope_manager: ScopeManager) -> None:

        # Create a new scope for the function.
        scope_manager.create_and_move_into_new_scope(f"<function:{self._orig}:{self.pos}>", self)
        super().generate_symbols(scope_manager)

        # Generate the generic parameters and attributes of the function.
        for p in self.generic_parameter_group.parameters:
            p.generate_symbols(scope_manager)

        # Move out of the function scope.
        scope_manager.move_out_of_current_scope()

    def alias_types(self, scope_manager: ScopeManager, **kwargs) -> None:
        # Skip the class scope (no sup-scope work to do).
        scope_manager.move_to_next_scope()
        scope_manager.move_out_of_current_scope()

    def load_sup_scopes(self, scope_manager: ScopeManager) -> None:
        from SPPCompiler.SemanticAnalysis import ModulePrototypeAst
        from SPPCompiler.SemanticAnalysis.Meta.AstFunctions import AstFunctions, FunctionConflictCheckType
        from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors

        scope_manager.move_to_next_scope()

        # Get the owner scope for function conflict checking.
        match self._ctx:
            case ModulePrototypeAst(): type_scope = scope_manager.current_scope.parent_module
            case _: type_scope = self._ctx._scope_cls

        # Check for function conflicts.
        if conflict := AstFunctions.check_for_conflicting_method(scope_manager.current_scope, type_scope, self, FunctionConflictCheckType.InvalidOverload):
            raise SemanticErrors.FunctionPrototypeConflictError().add(self._orig, conflict._orig)

        scope_manager.move_out_of_current_scope()

    def inject_sup_scopes(self, scope_manager: ScopeManager) -> None:
        scope_manager.move_to_next_scope()
        scope_manager.move_out_of_current_scope()

    def alias_types_regeneration(self, scope_manager: ScopeManager) -> None:
        scope_manager.move_to_next_scope()
        scope_manager.move_out_of_current_scope()

    def regenerate_generic_types(self, scope_manager: ScopeManager) -> None:
        scope_manager.move_to_next_scope()
        self.return_type.analyse_semantics(scope_manager)
        for t in self.function_parameter_group.parameters.map_attr("type"):
            t.analyse_semantics(scope_manager)
        scope_manager.move_out_of_current_scope()

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        scope_manager.move_to_next_scope()

        # Analyse the semantics of everything except the body (subclasses handle this).
        for a in self.annotations:
            a.analyse_semantics(scope_manager, **kwargs)
        self.generic_parameter_group.analyse_semantics(scope_manager, **kwargs)
        self.function_parameter_group.analyse_semantics(scope_manager, **kwargs)
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

    def _deduce_mock_class_type(self) -> TypeAst:
        from SPPCompiler.SemanticAnalysis import ConventionMovAst, ConventionMutAst, ConventionRefAst
        from SPPCompiler.SemanticAnalysis import ModulePrototypeAst
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes

        # Module-level functions are always FunRef.
        if isinstance(self._ctx, ModulePrototypeAst) or not self.function_parameter_group.get_self():
            return CommonTypes.FunRef(CommonTypes.Tup(self.function_parameter_group.parameters.map_attr("type")), self.return_type)

        # Class methods with "self" are the FunMov type.
        if isinstance(self.function_parameter_group.get_self().convention, ConventionMovAst):
            return CommonTypes.FunMov(CommonTypes.Tup(self.function_parameter_group.parameters.map_attr("type")), self.return_type)

        # Class methods with "&mut self" are the FunMut type.
        if isinstance(self.function_parameter_group.get_self().convention, ConventionMutAst):
            return CommonTypes.FunMut(CommonTypes.Tup(self.function_parameter_group.parameters.map_attr("type")), self.return_type)

        # Class methods with "&self" are the FunRef type.
        if isinstance(self.function_parameter_group.get_self().convention, ConventionRefAst):
            return CommonTypes.FunRef(CommonTypes.Tup(self.function_parameter_group.parameters.map_attr("type")), self.return_type)

    def _deduce_mock_class_call(self, function_type) -> IdentifierAst:
        from SPPCompiler.SemanticAnalysis import IdentifierAst
        return IdentifierAst(self.name.pos, f"call_{function_type.types[-1].value.split("_")[-1].lower()}")

    def __deepcopy__(self, memodict=None) -> FunctionPrototypeAst:
        # Copy all attributes except for "_protected" attributes, which are re-linked.
        return type(self)(
            copy.deepcopy(self.pos), self.annotations, self.tok_fun,
            copy.deepcopy(self.name), copy.deepcopy(self.generic_parameter_group),
            copy.deepcopy(self.function_parameter_group), self.tok_arrow,
            copy.deepcopy(self.return_type), copy.deepcopy(self.where_block), copy.deepcopy(self.body),
            _ctx=self._ctx, _orig=self._orig, _scope=None, _abstract=self._abstract, _virtual=self._virtual,
            _non_implemented=self._non_implemented)


__all__ = ["FunctionPrototypeAst"]
