from __future__ import annotations

from dataclasses import dataclass, field

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class TypeUnaryOperatorNamespaceAst(Ast, TypeInferrable):
    name: Asts.IdentifierAst = field(default_factory=lambda: Asts.IdentifierAst())
    tok_dbl_colon: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.TkDblColon))

    def __eq__(self, other: TypeUnaryOperatorNamespaceAst) -> bool:
        return self.name == other.name

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        return f"{self.name}{self.tok_dbl_colon}"

    def fq_type_parts(self) -> Seq[Asts.IdentifierAst | Asts.GenericIdentifierAst | Asts.TokenAst]:
        return Seq([self.name])

    def type_parts(self) -> Seq[Asts.GenericIdentifierAst]:
        return Seq()


__all__ = ["TypeUnaryOperatorNamespaceAst"]
