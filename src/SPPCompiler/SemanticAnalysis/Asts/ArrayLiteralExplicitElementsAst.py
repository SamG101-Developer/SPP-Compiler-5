from __future__ import annotations

from dataclasses import dataclass, field

from llvmlite import ir

from SPPCompiler.CodeGen.LlvmConfig import LlvmConfig
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstTypeUtils import AstTypeUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import AstPrinter, ast_printer_method
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors
from SPPCompiler.Utils.Sequence import SequenceUtils


@dataclass(slots=True, repr=False)
class ArrayLiteralExplicitElementsAst(Asts.Ast, Asts.Mixins.TypeInferrable):
    """
    The ArrayLiteralExplicitElementAst class is an AST node that represents an array literal with n elements. The type
    of the element is never given, because every expression in S++ is type-inferrable on declaration. This means that
    the type of the array is inferred from the first element in the array.

    Example:

    .. code-block:: S++

        let x = [1_u8, 2_u8, 3_u8, 4_u8]

    This will create a std::array::Arr[std::number::U8, 4] type. Arrays in S++ are low-level constructs, and map
    directly to memory. For example, this array will be stored in memory as 4 consecutive bytes. It is analogous to a C
    array[], but as a first-class, safe type.
    """

    tok_l: Asts.TokenAst = field(default=None)
    """The opening ``[`` token marking an array literal."""

    elems: list[Asts.ExpressionAst] = field(default_factory=list)
    """The expressions representing the elements in the array literal."""

    tok_r: Asts.TokenAst = field(default=None)
    """The closing ``]`` token marking the end of an array literal."""

    def __eq__(self, other: ArrayLiteralExplicitElementsAst) -> bool:
        # Needed for cmp-generic arg checking
        return type(other) is ArrayLiteralExplicitElementsAst and self.elems == other.elems

    def __hash__(self) -> int:
        """
        Array literals can be used as comptime generic arguments, and so might be stored in a list when considering
        generic arguments to a type. As such, a ``__hash__`` function is required. Uniqueness is the only thing required
        (ie two arguments could be the same value, but are different arguments), so a fast ``id`` call can be used,
        ensuring uniqueness.
        """

        # Use the id of the object to ensure uniqueness.
        return id(self)

    def __str__(self) -> str:
        # String representation of the array literal.
        elem_string = ", ".join(str(elem) for elem in self.elems)
        return f"[{elem_string}]"

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_l.print(printer),
            SequenceUtils.print(printer, self.elems, sep=", "),
            self.tok_r.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.tok_r.pos_end

    def infer_type(self, sm: ScopeManager, **kwargs) -> Asts.TypeAst:
        """
        The inferred type will always be std::Arr, with its generic arguments determined by the inferred element type,
        and the number of elements. The type will be "std::Arr[Element=<self.element_type>, n=<self.size>]".

        :param sm: The scope manager.
        :param kwargs: Additional keyword arguments.
        :return: The inferred array type.
        """

        # Create the standard "std::array::Arr[T, n: BigNum]" type, with generic items.
        size = Asts.TokenAst.raw(token_type=SppTokenType.LxNumber, token_metadata=str(len(self.elems)))
        size = Asts.IntegerLiteralAst(pos=self.pos, value=size, raw_type=Asts.TypeIdentifierAst.from_identifier(Asts.IdentifierAst(value="uz")))
        element_type = self.elems[0].infer_type(sm, **kwargs)
        array_type = CommonTypes.Arr(self.pos, element_type, size)
        array_type.analyse_semantics(sm, **kwargs)
        return array_type

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        """
        As this literal takes values inside the brackets, the type of element is inferred from them. All the elements
        must be the same type. To enforce memory rules, none of these elements can be borrows, in the same way class
        attributes cannot be borrows.

        :param sm: The scope manager.
        :param kwargs: Additional keyword arguments.
        :raise SemanticErrors.ExpressionTypeInvalidError: This exception is raised if an expression for a value is
            syntactically valid but makes no sense in this context (".." or a type).
        :raise SemanticErrors.ArrayElementsDifferentTypesError(): This exception is raised if an array element
            has a different type that the first element. It is a specialized type mismatch error.
        :raise SemanticErrors.ArrayElementBorrowedError(): This exception is raised if an array element is in the
            borrowed state, invalidating it from being stored in an array.
        """

        zeroth_elem = self.elems[0]
        zeroth_elem_type = zeroth_elem.infer_type(sm, **kwargs)

        # Analyse the elements in the array.
        for elem in self.elems:
            if isinstance(elem, (Asts.TokenAst, Asts.TypeAst)):
                raise SemanticErrors.ExpressionTypeInvalidError().add(elem).scopes(sm.current_scope)
            elem.analyse_semantics(sm, **kwargs)

        # Check all elements have the same type as the 0th element.
        all_elem_types_and_ast = zip([e.infer_type(sm, **kwargs) for e in self.elems], self.elems)
        for elem_type, elem in list(all_elem_types_and_ast)[1:]:
            if not AstTypeUtils.symbolic_eq(zeroth_elem_type, elem_type, sm.current_scope, sm.current_scope):
                raise SemanticErrors.ArrayElementsDifferentTypesError().add(
                    zeroth_elem, zeroth_elem_type, elem, elem_type).scopes(sm.current_scope)

        # Check all elements are owned / not borrowed.
        for elem in self.elems:
            if borrow_symbol := sm.current_scope.get_variable_symbol_outermost_part(elem):
                if borrow_ast := borrow_symbol.memory_info.ast_borrowed:
                    raise SemanticErrors.ArrayElementBorrowedError().add(
                        elem, borrow_ast).scopes(sm.current_scope)

        # Analyse the inferred array type to generate the generic implementation.
        self.infer_type(sm, **kwargs).analyse_semantics(sm, **kwargs)

    def code_gen_pass_2(self, sm: ScopeManager, llvm_module: ir.Module, **kwargs) -> ir.AllocaInstr:
        """
        This array AST will create an array with the element all created, by recursively calling ``code_gen_pass_2`` on
        each element AST belonging to this array literal. The array will be created on the stack, and the elements will
        be stored in the array.

        :param sm: The scope manager.
        :param llvm_module: The LLVM module to generate code into.
        :param kwargs: Additional keyword arguments.
        :return: The LLVM array object that can be used in the expression context.
        """

        # Use the 0-element generator to create the array (shared code).
        array_ptr = Asts.ArrayLiteralRepeatedElementAst.code_gen_pass_2(self, sm, llvm_module, **kwargs)

        # For each element, covert it to LLVM and store it in the array.
        zero = ir.Constant(ir.IntType(LlvmConfig.LLVM_USIZE), 0)
        for i in range(len(self.elems)):
            index = ir.Constant(ir.IntType(LlvmConfig.LLVM_USIZE), i)
            elem_ptr = kwargs["builder"].gep(array_ptr, [zero, index])
            elem = self.elems[i].code_gen_pass_2(sm, llvm_module, **kwargs)
            kwargs["builder"].store(elem, elem_ptr)

        # Return the array pointer to be used in the expression context.
        return array_ptr


__all__ = [
    "ArrayLiteralExplicitElementsAst"]
