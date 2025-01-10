from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast, Default
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Meta.AstOrdering import AstOrdering
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.CoroutinePrototypeAst import CoroutinePrototypeAst
    from SPPCompiler.SemanticAnalysis.ASTs.FunctionCallArgumentAst import FunctionCallArgumentAst
    from SPPCompiler.SemanticAnalysis.ASTs.FunctionCallArgumentNamedAst import FunctionCallArgumentNamedAst
    from SPPCompiler.SemanticAnalysis.ASTs.FunctionCallArgumentUnnamedAst import FunctionCallArgumentUnnamedAst
    from SPPCompiler.SemanticAnalysis.ASTs.FunctionPrototypeAst import FunctionPrototypeAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst


@dataclass
class FunctionCallArgumentGroupAst(Ast, Default, CompilerStages):
    tok_left_paren: TokenAst
    arguments: Seq[FunctionCallArgumentAst]
    tok_right_paren: TokenAst

    def __post_init__(self) -> None:
        # Convert the arguments into a sequence.
        self.arguments = Seq(self.arguments)

    def __copy__(self) -> FunctionCallArgumentGroupAst:
        return FunctionCallArgumentGroupAst.default(self.arguments.copy())

    def __eq__(self, other: FunctionCallArgumentGroupAst) -> bool:
        # Check both ASTs are the same type and have the same arguments.
        return isinstance(other, FunctionCallArgumentGroupAst) and self.arguments == other.arguments

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_left_paren.print(printer),
            self.arguments.print(printer, ", "),
            self.tok_right_paren.print(printer)]
        return "".join(string)

    @staticmethod
    def default(arguments: Seq[FunctionCallArgumentAst] = None) -> FunctionCallArgumentGroupAst:
        from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
        from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
        return FunctionCallArgumentGroupAst(-1, TokenAst.default(SppTokenType.TkParenL), arguments or Seq(), TokenAst.default(SppTokenType.TkParenR))

    def get_named(self) -> Seq[FunctionCallArgumentNamedAst]:
        # Get all the named function call arguments.
        from SPPCompiler.SemanticAnalysis import FunctionCallArgumentNamedAst
        return self.arguments.filter_to_type(FunctionCallArgumentNamedAst)

    def get_unnamed(self) -> Seq[FunctionCallArgumentUnnamedAst]:
        # Get all the unnamed function call arguments.
        from SPPCompiler.SemanticAnalysis import FunctionCallArgumentUnnamedAst
        return self.arguments.filter_to_type(FunctionCallArgumentUnnamedAst)

    def analyse_pre_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # Code that is run before the overload is selected.
        from SPPCompiler.SemanticAnalysis import FunctionCallArgumentNamedAst, FunctionCallArgumentUnnamedAst
        from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
        from SPPCompiler.SemanticAnalysis.Meta.AstMutation import AstMutation
        from SPPCompiler.SyntacticAnalysis.Parser import SppParser

        # Check there are no duplicate argument names.
        argument_names = self.arguments.filter_to_type(FunctionCallArgumentNamedAst).map(lambda a: a.name)
        if duplicates := argument_names.non_unique():
            raise SemanticErrors.IdentifierDuplicationError().add(duplicates[0][0], duplicates[0][1], "named arguments")

        # Check the arguments are in the correct order.
        if difference := AstOrdering.order_args(self.arguments):
            raise SemanticErrors.OrderInvalidError().add(difference[0][0], difference[0][1], difference[1][0], difference[1][1], "argument")

        # Expand tuple-expansion arguments ("..tuple" => "tuple.0, tuple.1, ...").
        for i, argument in self.arguments.enumerate():
            if isinstance(argument, FunctionCallArgumentUnnamedAst) and argument.tok_unpack:

                # Check the argument type is a tuple
                tuple_argument_type = argument.infer_type(scope_manager, **kwargs).type
                if not tuple_argument_type.without_generics().symbolic_eq(CommonTypes.Tup(), scope_manager.current_scope):
                    raise SemanticErrors.ArgumentTupleExpansionOfNonTupleError().add(argument.value, tuple_argument_type)

                # Replace the tuple-expansion argument with the expanded arguments
                self.arguments.pop(i)
                for j in range(tuple_argument_type.types[-1].generic_argument_group.arguments.length - 1, -1, -1):
                    new_argument = AstMutation.inject_code(f"{argument.value}.{j}", SppParser.parse_function_call_argument_unnamed)
                    new_argument.convention = argument.convention
                    self.arguments.insert(i, new_argument)

        # Analyse the arguments.
        for a in self.arguments:
            a.analyse_semantics(scope_manager, **kwargs)

    def analyse_semantics(self, scope_manager: ScopeManager, target: FunctionPrototypeAst = None, is_async: TokenAst = None, **kwargs) -> None:
        # Code that is run after the overload is selected.
        from SPPCompiler.SemanticAnalysis import ConventionMovAst, ConventionMutAst, ConventionRefAst, CoroutinePrototypeAst
        from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
        from SPPCompiler.SemanticAnalysis.Meta.AstMemory import AstMemoryHandler

        # Mark if pins are required, and the ast to mark as errored if required.
        pins_required = is_async or isinstance(target, CoroutinePrototypeAst)
        pin_error_ast = is_async or target

        # Define the borrow sets to maintain the law of exclusivity.
        borrows_ref = Seq()
        borrows_mut = Seq()

        # Begin the analysis of the arguments against each other.
        for argument in self.arguments:

            # Ensure the argument isn't moved or partially moved (applies to all conventions).
            symbol = scope_manager.current_scope.get_variable_symbol_outermost_part(argument.value)
            AstMemoryHandler.enforce_memory_integrity(
                argument.value, argument, scope_manager,
                check_move_from_borrowed_context=False, check_pins=False, update_memory_info=False)
            if not symbol:
                continue

            if isinstance(argument.convention, ConventionMovAst):
                # Don't recheck the moves or partial moves, but ensure the pins are maintained here.
                AstMemoryHandler.enforce_memory_integrity(
                    argument.value, argument, scope_manager,
                    check_move=False, check_partial_move=False, check_pins=True)

                # Check the move doesn't overlap with any borrows.
                if overlap := (borrows_ref + borrows_mut).find(lambda b: AstMemoryHandler.overlaps(b, argument.value)):
                    raise SemanticErrors.MemoryOverlapUsageError().add(overlap, argument.value)

            elif isinstance(argument.convention, ConventionMutAst):
                # Check the argument being mutably borrowed isn't an immutable borrow.
                if symbol.memory_info.is_borrow_ref:
                    raise SemanticErrors.MutabilityInvalidMutationError().add(argument.value, argument.convention, symbol.memory_info.ast_borrowed)

                # Check the argument's value is mutable.
                if not symbol.is_mutable:
                    raise SemanticErrors.MutabilityInvalidMutationError().add(argument.value, argument.convention, symbol.memory_info.ast_initialization)

                # Check the mutable borrow doesn't overlap with any other borrow in the same scope.
                if overlap := (borrows_ref + borrows_mut).find(lambda b: AstMemoryHandler.overlaps(b, argument.value)):
                    raise SemanticErrors.MemoryOverlapUsageError().add(overlap, argument.value)

                # If the target requires pinning, ensure the borrow is pinned.
                if pins_required and not (overlap := symbol.memory_info.ast_pinned.find(lambda p: AstMemoryHandler.left_overlap(p, argument.value))):
                    raise SemanticErrors.MemoryUsageOfUnpinnedBorrowError().add(argument.value, pin_error_ast)

                # No error with pinning -> mark the pin target.
                elif pins_required and "assignment" in kwargs and (target := kwargs["assignment"]):
                    symbol.memory_info.pin_target = target

                # Add the mutable borrow to the mutable borrow set.
                borrows_mut.append(argument.value)

            elif isinstance(argument.convention, ConventionRefAst):
                # Check the immutable borrow doesn't overlap with any other mutable borrow in the same scope.
                if overlap := borrows_mut.find(lambda b: AstMemoryHandler.overlaps(b, argument.value)):
                    raise SemanticErrors.MemoryOverlapUsageError().add(overlap, argument.value)

                # If the target requires pinning, ensure the borrow is pinned.
                if pins_required and not (overlap := symbol.memory_info.ast_pinned.find(lambda p: AstMemoryHandler.left_overlap(p, argument.value))):
                    raise SemanticErrors.MemoryUsageOfUnpinnedBorrowError().add(argument.value, pin_error_ast)

                # No error with pinning -> mark the pin target.
                elif pins_required and "assignment" in kwargs and (target := kwargs["assignment"]):
                    symbol.memory_info.pin_target = target

                # Add the immutable borrow to the immutable borrow set.
                borrows_ref.append(argument.value)


__all__ = ["FunctionCallArgumentGroupAst"]
