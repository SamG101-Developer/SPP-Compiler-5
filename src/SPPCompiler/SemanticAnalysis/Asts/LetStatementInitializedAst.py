from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstTypeUtils import AstTypeUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors


# from llvmlite import ir as llvm


@dataclass(slots=True, repr=False)
class LetStatementInitializedAst(Asts.Ast, Asts.Mixins.TypeInferrable):
    kw_let: Asts.TokenAst = field(default=None)
    assign_to: Asts.LocalVariableAst = field(default=None)
    explicit_type: Optional[Asts.TypeAst] = field(default=None)
    tok_assign: Asts.TokenAst = field(default=None)
    value: Asts.ExpressionAst = field(default=None)

    def __post_init__(self) -> None:
        self.kw_let = self.kw_let or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.KwLet)
        self.tok_assign = self.tok_assign or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkAssign)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.kw_let.print(printer) + " ",
            self.assign_to.print(printer) + " ",
            self.tok_assign.print(printer) + " ",
            self.value.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.value.pos_end

    def infer_type(self, sm: ScopeManager, **kwargs) -> Asts.TypeAst:
        # All statements are inferred as "void".
        return CommonTypes.Void(self.pos)

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # The ".." TokenAst, or TypeAst, cannot be used as an expression for the value.
        if isinstance(self.value, (Asts.TokenAst, Asts.TypeAst)):
            raise SemanticErrors.ExpressionTypeInvalidError().add(
                self.value).scopes(sm.current_scope)

        # An explicit type can only be applied if the LHS is a single identifier.
        if self.explicit_type is not None and type(self.assign_to) is not Asts.LocalVariableSingleIdentifierAst:
            raise SemanticErrors.InvalidTypeAnnotationError().add(
                self.explicit_type, self.assign_to).scopes(sm.current_scope)

        # Analyse the explicit type if it exists.
        if self.explicit_type is not None:
            self.explicit_type.analyse_semantics(sm, **kwargs)

        # Analyse the value to ensure its valid before any destructuring takes place.
        if type(self.value) is Asts.PostfixExpressionAst and type(self.value.op) is Asts.PostfixExpressionOperatorFunctionCallAst:
            kwargs |= {"inferred_return_type": self.explicit_type}

        # If an explicit type has been given, analyse it before value analysis.
        if self.explicit_type is not None:
            self.explicit_type.analyse_semantics(sm, **kwargs)

        self.value.analyse_semantics(sm, **(kwargs | {"assignment": self.assign_to.extract_names}))

        # This allows a variant type as the annotation with a composite-type value.
        if self.explicit_type is not None:
            if not AstTypeUtils.symbolic_eq(self.explicit_type, val_type := self.value.infer_type(sm, **(kwargs | {"assignment_type": self.explicit_type})), sm.current_scope, sm.current_scope):
                raise SemanticErrors.TypeMismatchError().add(
                    self.explicit_type, self.explicit_type, self.value, val_type).scopes(sm.current_scope)

        # Ensure each destructuring part is valid.
        kwargs.pop("explicit_type", None)
        self.assign_to.analyse_semantics(sm, value=self.value, explicit_type=self.explicit_type, **(kwargs | {"assignment_type": self.explicit_type}))

    def check_memory(self, sm: ScopeManager, **kwargs) -> None:
        kwargs.pop("value", None)
        self.assign_to.check_memory(sm, value=self.value, **(kwargs | {"assignment": self.assign_to.extract_names}))

    # def generate_llvm_definitions(
    #         self, sm: ScopeManager, llvm_module: llvm.Module = None, builder: llvm.IRBuilder = None,
    #         block: llvm.Block = None, **kwargs) -> Any:
    #
    #     for var, val in self.assign_to._new_asts:
    #         # Get the type of the variable and allocate memory for it.
    #         var_type = sm.current_scope.get_symbol(var.name).type
    #         llvm_type = sm.current_scope.get_symbol(var_type).llvm_info.llvm_type
    #         llvm_alloc = builder.alloca(llvm_type, name=str(var.name))
    #
    #         # Convert the value to an LLVM constant and store it in the allocated memory.
    #         llvm_value = val.generate_llvm_definitions(sm, llvm_module, None, None, **kwargs)
    #         llvm_var = llvm.Constant(llvm_type, llvm_value)
    #         builder.store(llvm_var, llvm_alloc)


__all__ = [
    "LetStatementInitializedAst"]
