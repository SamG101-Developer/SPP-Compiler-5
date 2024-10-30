from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstBinUtils import AstBinUtils
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable, InferredType
from SPPCompiler.SemanticAnalysis.MultiStage.Stage4_SemanticAnalyser import Stage4_SemanticAnalyser
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.ASTs.CaseExpressionAst import CaseExpressionAst
    from SPPCompiler.SemanticAnalysis.ASTs.PostfixExpressionAst import PostfixExpressionAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class BinaryExpressionAst(Ast, TypeInferrable, Stage4_SemanticAnalyser):
    lhs: ExpressionAst
    op: TokenAst
    rhs: ExpressionAst
    _as_func: Optional[PostfixExpressionAst | CaseExpressionAst] = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        self._as_func = AstBinUtils.convert_to_function_call(self)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.lhs.print(printer) + " ",
            self.op.print(printer) + " ",
            self.rhs.print(printer)]
        return "".join(string)

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredType:
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
        from SPPCompiler.LexicalAnalysis.TokenType import TokenType

        # Comparisons using the "is" keyword are always boolean.
        if self.op.token.token_type == TokenType.KwIs:
            bool_type = CommonTypes.Bool(self.pos)
            return InferredType.from_type(bool_type)

        # Infer the type from the function equivalent of the binary expression.
        return self._as_func.infer_type(scope_manager, **kwargs)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        from SPPCompiler.SemanticAnalysis import TypeAst
        from SPPCompiler.SemanticAnalysis.Meta.AstErrors import AstErrors
        from SPPCompiler.SemanticAnalysis.Meta.AstMutation import AstMutation
        from SPPCompiler.SemanticAnalysis.Meta.AstMemory import AstMemoryHandler
        from SPPCompiler.SyntacticAnalysis.Parser import Parser

        # The TypeAst cannot be used as an expression for a binary operation.
        if isinstance(self.lhs, TypeAst):
            raise AstErrors.INVALID_EXPRESSION(self.lhs)
        if isinstance(self.rhs, TypeAst):
            raise AstErrors.INVALID_EXPRESSION(self.rhs)

        # Ensure the LHS and RHS are semantically valid.
        self.lhs.analyse_semantics(scope_manager, **kwargs)
        self.rhs.analyse_semantics(scope_manager, **kwargs)

        # Ensure the memory status of the left and right hand side.
        AstMemoryHandler.enforce_memory_integrity(self.lhs, self.op, scope_manager, update_memory_info=False)
        AstMemoryHandler.enforce_memory_integrity(self.rhs, self.op, scope_manager)

        # Check for compound assignment (for example "+="), that the lhs is symbolic.
        if self.op.token.token_type.name.endswith("Assign") and not scope_manager.current_scope.get_variable_symbol_outermost_part(self.lhs):
            raise AstErrors.INVALID_COMPOUND_ASSIGNMENT_LHS_EXPR(self.lhs)

        # Handle lhs-folding
        if isinstance(self.lhs, TokenAst):
            rhs_tuple_type = self.rhs.infer_type(scope_manager, **kwargs).type
            rhs_num_elements = rhs_tuple_type.types[-1].generic_argument_group.arguments.length

            # Convert "a + .." into "a.0 + a.1 + a.2" etc up to "rhs_num_elements".
            new_asts = Seq()
            for i in range(rhs_num_elements):
                new_ast = AstMutation.inject_code(f"{self.rhs}.{i}", Parser.parse_postfix_expression)
                new_asts.append(new_ast)

            # Change the "lhs" and "rhs" to a combination of the new elements.
            self.lhs, self.rhs = new_asts[1], new_asts[0]
            for new_ast in new_asts[2:]:
                self.lhs = new_ast
                self.rhs = BinaryExpressionAst(self.pos, self.lhs, self.op, self.rhs)

        # Handle rhs-folding
        if isinstance(self.rhs, TokenAst):
            lhs_tuple_type = self.lhs.infer_type(scope_manager, **kwargs).type
            lhs_num_elements = lhs_tuple_type.types[-1].generic_argument_group.arguments.length

            # Convert ".. + a" into "a.0 + a.1 + a.2" etc up to "lhs_num_elements".
            new_asts = Seq()
            for i in range(lhs_num_elements):
                new_ast = AstMutation.inject_code(f"{self.lhs}.{i}", Parser.parse_postfix_expression)
                new_asts.append(new_ast)

            # Change the "lhs" and "rhs" to a combination of the new elements.
            self.lhs, self.rhs = new_asts[0], new_asts[1]
            for new_ast in new_asts[2:]:
                self.lhs = BinaryExpressionAst(self.pos, self.lhs, self.op, self.rhs)
                self.rhs = new_ast

        # Analyse the function equivalent of the binary expression.
        self._as_func.analyse_semantics(scope_manager, **kwargs)


__all__ = ["BinaryExpressionAst"]
