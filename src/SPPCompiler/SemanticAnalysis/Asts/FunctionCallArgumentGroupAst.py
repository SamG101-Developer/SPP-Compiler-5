from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstMemoryUtils import AstMemoryUtils
from SPPCompiler.SemanticAnalysis.AstUtils.AstOrderingUtils import AstOrderingUtils
from SPPCompiler.SemanticAnalysis.AstUtils.AstTypeUtils import AstTypeUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.CodeInjection import CodeInjection
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors
from SPPCompiler.SyntacticAnalysis.Parser import SppParser
from SPPCompiler.Utils.Sequence import Seq, SequenceUtils


@dataclass(slots=True)
class FunctionCallArgumentGroupAst(Asts.Ast):
    tok_l: Asts.TokenAst = field(default=None)
    arguments: Seq[Asts.FunctionCallArgumentAst] = field(default_factory=Seq)
    tok_r: Asts.TokenAst = field(default=None)

    def __post_init__(self) -> None:
        self.tok_l = self.tok_l or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkLeftParenthesis)
        self.tok_r = self.tok_r or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkRightParenthesis)

    def __copy__(self) -> FunctionCallArgumentGroupAst:
        return FunctionCallArgumentGroupAst(pos=self.pos, arguments=self.arguments.copy())

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_l.print(printer),
            SequenceUtils.print(printer, self.arguments, sep=", "),
            self.tok_r.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.tok_r.pos_end

    def get_named_args(self) -> Seq[Asts.FunctionCallArgumentNamedAst]:
        # Get all the named function call arguments.
        return [a for a in self.arguments if isinstance(a, Asts.FunctionCallArgumentNamedAst)]

    def get_unnamed_args(self) -> Seq[Asts.FunctionCallArgumentUnnamedAst]:
        # Get all the unnamed function call arguments.
        return [a for a in self.arguments if isinstance(a, Asts.FunctionCallArgumentUnnamedAst)]

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # Check there are no duplicate argument names.
        argument_names = [a.name for a in self.arguments if isinstance(a, Asts.FunctionCallArgumentNamedAst)]
        if duplicates := SequenceUtils.duplicates(argument_names):
            raise SemanticErrors.IdentifierDuplicationError().add(
                duplicates[0], duplicates[1], "named arguments").scopes(sm.current_scope)

        # Check the arguments are in the correct order.
        if dif := AstOrderingUtils.order_args(self.arguments):
            raise SemanticErrors.OrderInvalidError().add(
                dif[0][0], dif[0][1], dif[1][0], dif[1][1], "argument").scopes(sm.current_scope)

        # Expand tuple-expansion arguments ("..tuple" => "tuple.0, tuple.1, ...").
        for i, argument in enumerate(self.arguments):
            if isinstance(argument, Asts.FunctionCallArgumentUnnamedAst) and argument.tok_unpack is not None:

                # Check the argument type is a tuple
                tuple_argument_type = argument.infer_type(sm, **kwargs)
                if not AstTypeUtils.is_type_tuple(tuple_argument_type, sm.current_scope):
                    raise SemanticErrors.ArgumentTupleExpansionOfNonTupleError().add(
                        argument.value, tuple_argument_type).scopes(sm.current_scope)

                # Replace the tuple-expansion argument with the expanded arguments
                self.arguments.pop(i)
                for j in range(len(tuple_argument_type.type_parts[0].generic_argument_group.arguments) - 1, -1, -1):
                    new_argument = CodeInjection.inject_code(
                        f"{argument.value}.{j}", SppParser.parse_function_call_argument_unnamed,
                        pos_adjust=self.arguments[i].pos)
                    new_argument.convention = argument.convention
                    self.arguments.insert(i, new_argument)

        # Analyse the arguments.
        for a in self.arguments:
            a.analyse_semantics(sm, **kwargs)

    def check_memory(self, sm: ScopeManager, target_proto: Asts.FunctionPrototypeAst = None, is_async: Optional[Asts.TokenAst] = None, is_coro_resume: bool = False, **kwargs) -> None:
        """
        The function call argument group has some of the most complex memory analysis rules. This is the key area for
        the "law of exclusivity" to be applied. Other areas that require this, such as lambda captures, are re-modelled
        as a function argument group to re-use this logic.

        There can be 1 mutable XOR n immutable overlapping borrows to a symbol, allowing for thread safety. Pins are
        also applied for borrows into coroutines and async function calls.

        An additional 2 checks for mutable borrows are required, to ensure that mutability is allowed for the argument.
        The two checks are:
            1. For borrowed arguments, ensure the borrow is not a "&" (immutable) borrow.
            2. For non-borrowed arguments, ensure the symbol is marked as "mut" (mutable).

        There are instances when "pins are required". This forces the owned object being borrowed to remain exactly in
        place in memory, in the current and parent scopes. On top of this, the borrow is marked as "extended", to ensure
        that not only is the owned object moved, the borrow doesn't conflict with future borrows in the scope. For
        example, given the coroutine "cor g(a: &mut BigInt)", called as "let generator = g(&mut x)", the "x" is pinned,
        and "&mut x" is an extended borrow. This prevents "let y = x" and "other_func(&x)" from being valid, as the
        coroutine is borrowing the owned object "x", and the borrow is extended to the end of the scope. As soon as this
        scope ends, the pin is released, and the extended borrow is invalidated.

        :param sm: The scope manager.
        :param target_proto: The target function prototype that is being called.
        :param is_async: Whether these arguments are being applied as "async f()".
        :param is_coro_resume: Whether these arguments are being applied to a coroutine call.
        :param kwargs: Additional keyword arguments.
        """

        # Mark if pins are required, and the ast to mark as errored if required.
        is_target_coro = isinstance(target_proto, Asts.CoroutinePrototypeAst)
        pins_required = is_async or (target_proto if is_target_coro and not is_coro_resume else None)

        # Define the borrow sets to maintain the law of exclusivity.
        borrows_ref = []
        borrows_mut = []

        # Add the extended borrows into the borrow lists.
        for argument in self.arguments:
            sym = sm.current_scope.get_symbol(argument.value)
            if sym is None: continue
            if not sym.memory_info.borrow_refers_to: continue
            for _, b, m in sym.memory_info.borrow_refers_to:
                (borrows_mut if m else borrows_ref).append(b.value)

        for argument in self.arguments:

            # Get the outermost part of the argument as a symbol. If the argument is non-symbolic, then there is no need
            # to track borrows to it, as it is a temporary value.
            sym = sm.current_scope.get_variable_symbol_outermost_part(argument.value)
            if not sym: continue

            # Ensure the argument isn't moved or partially moved (applies to all conventions). For non-symbolic
            # arguments, nested checking is done via the argument itself.
            argument.check_memory(sm, **kwargs)
            AstMemoryUtils.enforce_memory_integrity(
                argument.value, argument, sm, check_move=True, check_partial_move=True,
                check_move_from_borrowed_ctx=False, check_pins=False, mark_moves=False)

            if argument.convention is None:
                # Don't bother rechecking the moves or partial moves, but ensure that attributes aren't being moved off
                # of a borrowed value and that pins are maintained. Mark the move or partial move of the argument.
                argument.check_memory(sm, **kwargs)
                AstMemoryUtils.enforce_memory_integrity(
                    argument.value, argument, sm, check_move=False, check_partial_move=False,
                    check_move_from_borrowed_ctx=True, check_pins=True, mark_moves=True)

                # Check the move doesn't overlap with any borrows. This is to ensure that "f(&x, x)" can never happen,
                # because the first argument requires the owned object to outlive the function call, and moving it as
                # the second argument breaks this.
                if overlap := [b for b in (borrows_ref + borrows_mut) if AstMemoryUtils.overlaps(b, argument.value)]:
                    raise SemanticErrors.MemoryOverlapUsageError().add(
                        overlap[0], argument.value).scopes(sm.current_scope)

            elif isinstance(argument.convention, Asts.ConventionMutAst):
                argument.check_memory(sm, **kwargs)

                # Check the mutable borrow doesn't overlap with any other borrow in the same scope.
                if overlap := [b for b in (borrows_ref + borrows_mut) if AstMemoryUtils.overlaps(b, argument.value)]:
                    raise SemanticErrors.MemoryOverlapUsageError().add(
                        overlap[0], argument.value).scopes(sm.current_scope)

                # Check the argument isn't already an immutable borrow.
                if sym.memory_info.ast_borrowed and sym.memory_info.is_borrow_ref:
                    raise SemanticErrors.MutabilityInvalidMutationError().add(
                        argument.value, argument.convention, sym.memory_info.ast_borrowed).scopes(sm.current_scope)

                # Check the argument's value is mutable.
                if not sym.is_mutable:
                    raise SemanticErrors.MutabilityInvalidMutationError().add(
                        argument.value, argument.convention, sym.memory_info.ast_initialization).scopes(sm.current_scope)

                # If the target requires pinning, pin it automatically.
                if pins_required:
                    sym.memory_info.ast_pins.append(argument.value)
                    sym.memory_info.is_borrow_mut = True
                    for assign_target in kwargs.get("assignment", []):
                        sm.current_scope.get_symbol(assign_target).memory_info.ast_pins.append(argument.value)
                        sym.memory_info.borrow_refers_to.append((assign_target, argument, True))
                    else:
                        sym.memory_info.borrow_refers_to.append((None, argument, True))

                # Add the mutable borrow to the mutable borrow set.
                borrows_mut.append(argument.value)

            elif isinstance(argument.convention, Asts.ConventionRefAst):
                argument.check_memory(sm, **kwargs)

                # Check the immutable borrow doesn't overlap with any other mutable borrow in the same scope.
                if overlap := [b for b in borrows_mut if AstMemoryUtils.overlaps(b, argument.value)]:
                    raise SemanticErrors.MemoryOverlapUsageError().add(
                        overlap[0], argument.value).scopes(sm.current_scope)

                # If the target requires pinning, pin it automatically.
                if pins_required:
                    sym.memory_info.ast_pins.append(argument.value)
                    sym.memory_info.is_borrow_ref = True
                    for assign_target in kwargs.get("assignment", []):
                        sm.current_scope.get_symbol(assign_target).memory_info.ast_pins.append(argument.value)
                        sym.memory_info.borrow_refers_to.append((assign_target, argument, False))
                    else:
                        sym.memory_info.borrow_refers_to.append((None, argument, False))

                # Add the immutable borrow to the immutable borrow set.
                borrows_ref.append(argument.value)


__all__ = [
    "FunctionCallArgumentGroupAst"]
