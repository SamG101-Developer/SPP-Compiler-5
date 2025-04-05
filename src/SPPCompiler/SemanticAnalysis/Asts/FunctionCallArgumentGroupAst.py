from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstMemoryUtils import AstMemoryUtils
from SPPCompiler.SemanticAnalysis.AstUtils.AstOrderingUtils import AstOrderingUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.CodeInjection import CodeInjection
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypesPrecompiled
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors
from SPPCompiler.SyntacticAnalysis.Parser import SppParser
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class FunctionCallArgumentGroupAst(Asts.Ast):
    tok_l: Asts.TokenAst = field(default=None)
    arguments: Seq[Asts.FunctionCallArgumentAst] = field(default_factory=Seq)
    tok_r: Asts.TokenAst = field(default=None)

    def __post_init__(self) -> None:
        self.tok_l = self.tok_l or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkLeftParenthesis)
        self.tok_r = self.tok_r or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkRightParenthesis)

    def __copy__(self) -> FunctionCallArgumentGroupAst:
        return FunctionCallArgumentGroupAst(arguments=self.arguments.copy())

    def __eq__(self, other: FunctionCallArgumentGroupAst) -> bool:
        # Check both ASTs are the same type and have the same arguments.
        return isinstance(other, FunctionCallArgumentGroupAst) and self.arguments == other.arguments

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_l.print(printer),
            self.arguments.print(printer, ", "),
            self.tok_r.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.tok_r.pos_end

    def get_named_args(self) -> Seq[Asts.FunctionCallArgumentNamedAst]:
        # Get all the named function call arguments.
        return self.arguments.filter_to_type(Asts.FunctionCallArgumentNamedAst)

    def get_unnamed_args(self) -> Seq[Asts.FunctionCallArgumentUnnamedAst]:
        # Get all the unnamed function call arguments.
        return self.arguments.filter_to_type(Asts.FunctionCallArgumentUnnamedAst)

    def analyse_pre_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # Code that is run before the overload is selected.

        # Check there are no duplicate argument names.
        argument_names = self.arguments.filter_to_type(Asts.FunctionCallArgumentNamedAst).map(lambda a: a.name)
        if duplicates := argument_names.non_unique():
            raise SemanticErrors.IdentifierDuplicationError().add(
                duplicates[0][0], duplicates[0][1], "named arguments").scopes(sm.current_scope)

        # Check the arguments are in the correct order.
        if difference := AstOrderingUtils.order_args(self.arguments):
            raise SemanticErrors.OrderInvalidError().add(
                difference[0][0], difference[0][1], difference[1][0], difference[1][1], "argument").scopes(sm.current_scope)

        # Expand tuple-expansion arguments ("..tuple" => "tuple.0, tuple.1, ...").
        for i, argument in self.arguments.enumerate():
            if isinstance(argument, Asts.FunctionCallArgumentUnnamedAst) and argument.tok_unpack:

                # Check the argument type is a tuple
                tuple_argument_type = argument.infer_type(sm, **kwargs)
                if not tuple_argument_type.without_generics().symbolic_eq(CommonTypesPrecompiled.EMPTY_TUPLE, sm.current_scope):
                    raise SemanticErrors.ArgumentTupleExpansionOfNonTupleError().add(argument.value, tuple_argument_type).scopes(sm.current_scope)

                # Replace the tuple-expansion argument with the expanded arguments
                self.arguments.pop(i)
                for j in range(tuple_argument_type.type_parts()[0].generic_argument_group.arguments.length - 1, -1, -1):
                    new_argument = CodeInjection.inject_code(
                        f"{argument.value}.{j}", SppParser.parse_function_call_argument_unnamed,
                        pos_adjust=self.arguments[i].pos)
                    new_argument.convention = argument.convention
                    self.arguments.insert(i, new_argument)

        # Analyse the arguments.
        for a in self.arguments:
            a.analyse_semantics(sm, **kwargs)

    def analyse_semantics(self, sm: ScopeManager, target_proto: Asts.FunctionPrototypeAst = None, is_async: Optional[Asts.TokenAst] = None, **kwargs) -> None:
        # Code that is run after the overload is selected.

        # Mark if pins are required, and the ast to mark as errored if required.
        pins_required = is_async or isinstance(target_proto, Asts.CoroutinePrototypeAst)

        # Define the borrow sets to maintain the law of exclusivity.
        borrows_ref = Seq()
        borrows_mut = Seq()

        # Begin the analysis of the arguments against each other.
        for argument in self.arguments:

            # Ensure the argument isn't moved or partially moved (applies to all conventions).
            symbol = sm.current_scope.get_variable_symbol_outermost_part(argument.value)
            AstMemoryUtils.enforce_memory_integrity(
                argument.value, argument, sm,
                check_move_from_borrowed_context=False, check_pins=False, update_memory_info=False)
            if not symbol:
                continue

            if argument.convention is None:
                # Don't recheck the moves or partial moves, but ensure the pins are maintained here.
                AstMemoryUtils.enforce_memory_integrity(
                    argument.value, argument, sm,
                    check_move=False, check_partial_move=False, check_pins=True)

                # Check the move doesn't overlap with any borrows.
                if overlap := (borrows_ref + borrows_mut).find(lambda b: AstMemoryUtils.overlaps(b, argument.value)):
                    raise SemanticErrors.MemoryOverlapUsageError().add(overlap, argument.value).scopes(sm.current_scope)

            elif isinstance(argument.convention, Asts.ConventionMutAst):
                # Check the argument isn't already an immutable borrow.
                if symbol.memory_info.is_borrow_ref:
                    raise SemanticErrors.MutabilityInvalidMutationError().add(argument.value, argument.convention, symbol.memory_info.ast_initialization).scopes(sm.current_scope)

                # Check the argument's value is mutable.
                if not symbol.is_mutable:
                    raise SemanticErrors.MutabilityInvalidMutationError().add(argument.value, argument.convention, symbol.memory_info.ast_initialization).scopes(sm.current_scope)

                # Check the mutable borrow doesn't overlap with any other borrow in the same scope.
                if overlap := (borrows_ref + borrows_mut).find(lambda b: AstMemoryUtils.overlaps(b, argument.value)):
                    raise SemanticErrors.MemoryOverlapUsageError().add(overlap, argument.value).scopes(sm.current_scope)

                # If the target requires pinning, pin it automatically.
                if pins_required and not (overlap := symbol.memory_info.ast_pinned.find(lambda p: AstMemoryUtils.left_overlap(p, argument.value))):
                    symbol.memory_info.ast_pinned.append(argument.value)

                # Add the mutable borrow to the mutable borrow set.
                borrows_mut.append(argument.value)

            elif isinstance(argument.convention, Asts.ConventionRefAst):
                # Check the immutable borrow doesn't overlap with any other mutable borrow in the same scope.
                if overlap := borrows_mut.find(lambda b: AstMemoryUtils.overlaps(b, argument.value)):
                    raise SemanticErrors.MemoryOverlapUsageError().add(overlap, argument.value).scopes(sm.current_scope)

                # If the target requires pinning, pin it automatically.
                if pins_required and not (overlap := symbol.memory_info.ast_pinned.find(lambda p: AstMemoryUtils.left_overlap(p, argument.value))):
                    symbol.memory_info.ast_pinned.append(argument.value)

                # Add the immutable borrow to the immutable borrow set.
                borrows_ref.append(argument.value)


__all__ = [
    "FunctionCallArgumentGroupAst"]
