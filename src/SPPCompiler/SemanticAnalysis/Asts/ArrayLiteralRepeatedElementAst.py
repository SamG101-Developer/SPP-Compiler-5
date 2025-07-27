from __future__ import annotations

from dataclasses import dataclass, field

from llvmlite import ir

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import AstPrinter, ast_printer_method
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors


@dataclass(slots=True, repr=False)
class ArrayLiteralRepeatedElementAst(Asts.Ast, Asts.Mixins.TypeInferrable):
    """
    The ``ArrayLiteralRepeatedElementAst`` class is an AST node that represents an array literal with a repeated
    element. The number of repeats is the size of the array, with the array element type being inferrable from the
    value. Note that the element is evaluated once, then copied N times, not constructed ``N`` times. Therefore, the
    element type must superimpose ``Copy``.

    Example:

    .. code-block:: S++

        let x = [0_32; 10]

    This will create a ``Arr[U32, 10]`` type.
    """

    tok_l: Asts.TokenAst = field(default=None)
    """The opening ``[`` token marking an array literal."""

    elem: Asts.ExpressionAst = field(default=None)
    """The element that will be repeated to form the array."""

    tok_semi_colon: Asts.TokenAst = field(default=None)
    """The semicolon ``;`` token separating the element and size of the array."""

    size: Asts.ExpressionAst = field(default=None)
    """The number representing the size of the array."""

    tok_r: Asts.TokenAst = field(default=None)
    """The closing ``]`` token marking the end of an array literal."""

    def __eq__(self, other: ArrayLiteralRepeatedElementAst) -> bool:
        return type(other) is ArrayLiteralRepeatedElementAst

    def __hash__(self) -> int:
        return id(self)

    def __str__(self):
        string = [
            "[", str(self.elem), "; ", str(self.size), "]"]
        return "".join(string)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            "[", self.elem.print(printer), "; ", self.size.print(printer), "]"]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.tok_r.pos_end

    def infer_type(self, sm: ScopeManager, **kwargs) -> Asts.TypeAst:
        """
        The inferred type will always be ``std::array::Arr``, with its generic arguments determined by the element and
        the size.

        :param sm: The scope manager.
        :param kwargs: Additional keyword arguments.
        :return: The inferred array type.
        """

        # Create the standard "std::array::Arr" type, with generic arguments.
        array_type = CommonTypes.Arr(self.pos, self.elem.infer_type(sm, **kwargs), self.size)
        array_type.analyse_semantics(sm, **kwargs)
        return array_type

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        """
        Analyse the element of the array literal, to make sure it is a valid element. This is done to ensure that the
        array type can be inferred correctly.

        :param sm: The scope manager.
        :param kwargs: Additional keyword arguments.
        """

        # Analyse the type of the element.
        self.elem.analyse_semantics(sm, **kwargs)
        elem_type = self.elem.infer_type(sm, **kwargs)
        elem_type_sym = sm.current_scope.get_symbol(elem_type)

        # Ensure the element type is copyable, so that is can be repeated in the array.
        if not elem_type_sym.is_copyable():
            raise SemanticErrors.MemoryNotInitializedUsageError().add(
                self.elem, self, self.size).scopes(sm.current_scope)

        # Ensure the element type is not a borrow, as array elements cannot be borrows.
        if c := elem_type.convention:
            raise SemanticErrors.InvalidConventionLocationError().add(
                c, elem_type, "array element type").scopes(sm.current_scope)

        # Ensure the size is a compile-time constant if symbolic.
        if size_sym := sm.current_scope.get_symbol(self.size):
            if size_sym is None or size_sym.memory_info.ast_comptime_const is None:
                raise SemanticErrors.CompileTimeConstantError().add(self.size).scopes(sm.current_scope)

        # Analyse the inferred array type to generate the generic implementation.
        self.infer_type(sm, **kwargs).analyse_semantics(sm, **kwargs)

    def code_gen_pass_2(self, sm: ScopeManager, llvm_module: ir.Module, **kwargs) -> ir.AllocaInstr:
        """
        The array type is std::array::Arr[T, n], which maps to the llvm array type. This AST means that there are no
        elements in each slot of the array, but the array itself is initialized. The code generation will create an
        array type object, on the stack, to be used in expression contexts.

        :param sm: The scope manager.
        :param llvm_module: The LLVM module to generate code into.
        :param kwargs: Additional keyword arguments.
        :return: The LLVM array object that can be used in the expression context.
        """

        # Todo


__all__ = [
    "ArrayLiteralRepeatedElementAst"]
