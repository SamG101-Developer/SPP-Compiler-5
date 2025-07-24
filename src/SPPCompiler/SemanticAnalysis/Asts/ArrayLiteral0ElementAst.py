from __future__ import annotations

from dataclasses import dataclass, field

from llvmlite import ir

from SPPCompiler.CodeGen.LlvmConfig import LlvmConfig
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import AstPrinter, ast_printer_method
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors


@dataclass(slots=True, repr=False)
class ArrayLiteral0ElementAst(Asts.Ast, Asts.Mixins.TypeInferrable):
    """
    The ArrayLiteral0ElementAst class is an AST node that represents an array literal with no elements. Because types
    must be known immediately (no deferred inference), the type and size of the array must be given at declaration. This
    literal handles this by accepting the information within the square brackets.

    Example:

    .. code-block:: S++

        let x = [BigInt, 10]

    This will create a std::array::Arr[BigInt, 10] type. The value itself is "initialized" to an empty array, and this
    is safe because accessors return the Opt[T] type, allowing for safe access. Bounds checking is also be handled by
    the optional type.
    """

    tok_l: Asts.TokenAst = field(default=None)
    """The opening ``[`` token marking an array literal."""

    elem_type: Asts.TypeAst = field(default=None)
    """The type of elements that will populate this array."""

    tok_comma: Asts.TokenAst = field(default=None)
    """The comma separating the type and size of the array."""

    size: Asts.TokenAst = field(default=None)
    """The number representing the size of the array."""

    tok_r: Asts.TokenAst = field(default=None)
    """The closing ``]`` token marking the end of an array literal."""

    def __post_init__(self) -> None:
        self.tok_l = self.tok_l or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkLeftSquareBracket)
        self.tok_comma = self.tok_comma or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkComma)
        self.tok_r = self.tok_r or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkRightSquareBracket)

    def __eq__(self, other: ArrayLiteral0ElementAst) -> bool:
        return type(other) is ArrayLiteral0ElementAst

    def __hash__(self) -> int:
        return id(self)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_l.print(printer),
            self.elem_type.print(printer),
            self.tok_comma.print(printer) + " ",
            self.size.print(printer),
            self.tok_r.print(printer)]
        return " ".join(string)

    @property
    def pos_end(self) -> int:
        return self.tok_r.pos_end

    def infer_type(self, sm: ScopeManager, **kwargs) -> Asts.TypeAst:
        """
        The inferred type will always be ``std::array::Arr``, with its generic arguments determined by the element type
        and the size. The type will be ``std::Arr[Element=<self.element_type>, n=<self.size>]``.

        :param sm: The scope manager.
        :param kwargs: Additional keyword arguments.
        :return: The inferred array type.
        """

        # Create the standard "std::array::Arr" type, with generic arguments.
        size = Asts.IntegerLiteralAst(pos=self.size.pos, value=self.size, type=Asts.TypeIdentifierAst.from_identifier(Asts.IdentifierAst(value="uz")))
        array_type = CommonTypes.Arr(self.pos, self.elem_type, size)
        array_type.analyse_semantics(sm, **kwargs)
        return array_type

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        """
        Analyse the element type of the array literal, to make sure it is a valid type. This is done to ensure that the
        array type can be inferred correctly. No value analysis is done as this literal is specifically for defining an
        empty array.

        :param sm: The scope manager.
        :param kwargs: Additional keyword arguments.
        """

        # Analyse the type of the element.
        self.elem_type.analyse_semantics(sm, **kwargs)

        # Ensure there is no convention on the array literal.
        if c := self.elem_type.convention:
            raise SemanticErrors.InvalidConventionLocationError().add(
                c, self.elem_type, "array element type").scopes(sm.current_scope)

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

        # Get the element's symbol and LLVM mapped type.
        elem_sym = sm.current_scope.get_symbol(self.elem_type)
        elem_llvm_type = elem_sym.llvm_info.llvm_type

        # Create the LLVM array type with the element type and size.
        array_llvm_type = ir.ArrayType(elem_llvm_type, int(self.size.token_data))

        # Create the array object on the stack for use in this scope only.
        builder = kwargs["builder"]
        array_ptr: ir.AllocaInstr = builder.alloca(array_llvm_type)
        array_ptr.align = LlvmConfig.LLVM_MEM_ALIGNMENT

        # Return the array object to be used in the expression context.
        return array_ptr


__all__ = [
    "ArrayLiteral0ElementAst"]
