from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Meta.AstVisbility import visibility_enabled_ast
from SPPCompiler.SemanticAnalysis.MultiStage.Stage1_PreProcessor import Stage1_PreProcessor, PreProcessingContext
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.AnnotationAst import AnnotationAst
    from SPPCompiler.SemanticAnalysis.ASTs.FunctionParameterGroupAst import FunctionParameterGroupAst
    from SPPCompiler.SemanticAnalysis.ASTs.GenericParameterGroupAst import GenericParameterGroupAst
    from SPPCompiler.SemanticAnalysis.ASTs.InnerScopeAst import InnerScopeAst
    from SPPCompiler.SemanticAnalysis.ASTs.StatementAst import StatementAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst
    from SPPCompiler.SemanticAnalysis.ASTs.WhereBlockAst import WhereBlockAst
    from SPPCompiler.SemanticAnalysis.ASTs.IdentifierAst import IdentifierAst


@dataclass
@visibility_enabled_ast
class FunctionPrototypeAst(Ast, Stage1_PreProcessor):
    annotations: Seq[AnnotationAst]
    tok_fun: TokenAst
    name: IdentifierAst
    generic_parameter_group: Optional[GenericParameterGroupAst]
    function_parameter_group: FunctionParameterGroupAst
    tok_arrow: TokenAst
    return_type: TypeAst
    where_block: Optional[WhereBlockAst]
    body: InnerScopeAst[StatementAst]

    _orig: IdentifierAst = field(default=None, kw_only=True, repr=False)
    _abstract: bool = field(default=False, kw_only=True, repr=False)
    _virtual: bool = field(default=False, kw_only=True, repr=False)

    def __post_init__(self) -> None:
        # Import the necessary classes to create default instances.
        from SPPCompiler.SemanticAnalysis import GenericParameterGroupAst, InnerScopeAst
        from SPPCompiler.SemanticAnalysis import WhereBlockAst

        # Convert the annotations into a sequence, and create other defaults.
        self.annotations = Seq(self.annotations)
        self.generic_parameter_group = self.generic_parameter_group or GenericParameterGroupAst.default()
        self.where_block = self.where_block or WhereBlockAst.default()
        self.body = self.body or InnerScopeAst.default()

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

    def pre_process(self, context: PreProcessingContext) -> None:
        from SPPCompiler.SemanticAnalysis import ClassPrototypeAst, ModulePrototypeAst, SupPrototypeInheritanceAst
        from SPPCompiler.SemanticAnalysis import TypeAst, InnerScopeAst
        from SPPCompiler.SemanticAnalysis.Meta.AstMutation import AstMutation
        from SPPCompiler.SyntacticAnalysis.Parser import Parser
        super().pre_process(context)

        # Substitute the "Self" parameter's type with the name of the method.
        if not isinstance(context, ModulePrototypeAst) and self.function_parameter_group.get_self():
            self.function_parameter_group.get_self().type = context.name

        # Convert the "fun" function to a "sup" superimposition of a "Fun[Mov|Mut|Ref]" type over a mock type.
        mock_class_name = TypeAst.from_function_identifier(self.name)
        function_type = self._deduce_mock_class_type()
        function_call = self._deduce_mock_class_call(function_type)

        # If this is the first overload being converted, then the class needs to be made for the type.
        if self._ctx.body.members.filter_to_type(ClassPrototypeAst).filter(lambda c: c.name == mock_class_name).is_empty():
            mock_class_ast = AstMutation.inject_code(f"cls {mock_class_name} {{}}", Parser.parse_class_prototype)
            mock_constant_ast = AstMutation.inject_code(f"cmp {self.name}: {mock_class_name} = {mock_class_name}()", Parser.parse_global_constant)
            self._ctx.body.members.append(mock_class_ast)
            self._ctx.body.members.append(mock_constant_ast)

        # Superimpose the function type over the mock class.
        function_ast = copy.deepcopy(self)
        mock_superimposition_body = InnerScopeAst.default(Seq([function_ast]))
        mock_superimposition = SupPrototypeInheritanceAst(self.pos, None, self.generic_parameter_group, mock_class_name, self.where_block, mock_superimposition_body, None, function_type)
        self._ctx.body.members.insert(0, mock_superimposition)
        self._ctx.body.members.remove(self)

        # Pre-process the annotations of this function's duplicate.
        Seq(self.annotations).for_each(lambda a: a.pre_process(function_ast))

    def _deduce_mock_class_type(self) -> TypeAst:
        from SPPCompiler.SemanticAnalysis import ConventionMovAst, ConventionMutAst, ConventionRefAst
        from SPPCompiler.SemanticAnalysis import ModulePrototypeAst
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes

        if isinstance(self._ctx, ModulePrototypeAst) or not self.function_parameter_group.get_self():
            return CommonTypes.FunRef(CommonTypes.Tup(self.function_parameter_group.parameters.map_attr("type")), self.return_type)

        if isinstance(self.function_parameter_group.get_self().convention, ConventionMovAst):
            return CommonTypes.FunMov(CommonTypes.Tup(self.function_parameter_group.parameters.map_attr("type")), self.return_type)

        if isinstance(self.function_parameter_group.get_self().convention, ConventionMutAst):
            return CommonTypes.FunMut(CommonTypes.Tup(self.function_parameter_group.parameters.map_attr("type")), self.return_type)

        if isinstance(self.function_parameter_group.get_self().convention, ConventionRefAst):
            return CommonTypes.FunRef(CommonTypes.Tup(self.function_parameter_group.parameters.map_attr("type")), self.return_type)

    def _deduce_mock_class_call(self, function_type) -> IdentifierAst:
        from SPPCompiler.SemanticAnalysis import IdentifierAst
        return IdentifierAst(self.name.pos, f"call_{function_type.types[-1].value.split("_")[-1].lower()}")

    def __deepcopy__(self, memodict=None) -> FunctionPrototypeAst:
        # Copy all attributes except for "_protected" attributes, which are re-linked.
        return FunctionPrototypeAst(
            copy.deepcopy(self.pos), copy.deepcopy(self.annotations), copy.deepcopy(self.tok_fun),
            copy.deepcopy(self.name), copy.deepcopy(self.generic_parameter_group),
            copy.deepcopy(self.function_parameter_group), copy.deepcopy(self.tok_arrow),
            copy.deepcopy(self.return_type), copy.deepcopy(self.where_block), copy.deepcopy(self.body),
            _ctx=self._ctx, _orig=self._orig, _abstract=self._abstract, _virtual=self._virtual)


__all__ = ["FunctionPrototypeAst"]
