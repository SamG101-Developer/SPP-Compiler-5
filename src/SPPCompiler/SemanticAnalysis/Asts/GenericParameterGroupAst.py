from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstOrderingUtils import AstOrderingUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors
from SPPCompiler.Utils.FastDeepcopy import fast_deepcopy
from SPPCompiler.Utils.FunctionCache import FunctionCache
from SPPCompiler.Utils.Sequence import SequenceUtils


@dataclass(slots=True, repr=False)
class GenericParameterGroupAst(Asts.Ast):
    tok_l: Asts.TokenAst = field(default=None)
    parameters: list[Asts.GenericParameterAst] = field(default_factory=list)
    tok_r: Asts.TokenAst = field(default=None)

    def __post_init__(self) -> None:
        self.tok_l = self.tok_l or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkLeftSquareBracket)
        self.tok_r = self.tok_r or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkRightSquareBracket)

    def __copy__(self) -> GenericParameterGroupAst:
        return GenericParameterGroupAst(parameters=self.parameters.copy())

    def __deepcopy__(self, memodict=None) -> GenericParameterGroupAst:
        return GenericParameterGroupAst(parameters=fast_deepcopy(self.parameters))

    def __eq__(self, other: GenericParameterGroupAst) -> bool:
        # Check both ASTs are the same type and have the same parameters.
        return self.parameters == other.parameters

    def __hash__(self) -> int:
        # Use the id of the object as the hash.
        return id(self)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        if self.parameters:
            string = [
                self.tok_l.print(printer),
                SequenceUtils.print(printer, self.parameters, sep=", "),
                self.tok_r.print(printer) + " "]
        else:
            string = []
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.tok_r.pos_end

    @FunctionCache.cache
    def get_required_params(self) -> list[Asts.GenericParameterRequiredAst]:
        # Get all the required generic parameters.
        return [p for p in self.parameters if isinstance(p, Asts.GenericParameterRequiredAst)]

    @FunctionCache.cache
    def get_optional_params(self) -> list[Asts.GenericParameterOptionalAst]:
        # Get all the optional generic parameters.
        return [p for p in self.parameters if isinstance(p, Asts.GenericParameterOptionalAst)]

    @FunctionCache.cache
    def get_variadic_params(self) -> list[Asts.GenericParameterVariadicAst]:
        # Get all the variadic generic parameters.
        return [p for p in self.parameters if isinstance(p, Asts.GenericParameterVariadicAst)]

    @FunctionCache.cache
    def get_comp_params(self) -> list[Asts.GenericCompParameterAst]:
        # Get all the computation generic parameters.
        return [p for p in self.parameters if isinstance(p, Asts.GenericCompParameterAst)]

    @FunctionCache.cache
    def get_type_params(self) -> list[Asts.GenericTypeParameterAst]:
        # Get all the type generic parameters.
        return [p for p in self.parameters if isinstance(p, Asts.GenericTypeParameterAst)]

    def opt_to_req(self) -> GenericParameterGroupAst:
        # Create a new group where optional parameters become required.
        new_params = []
        for p in self.parameters:
            if type(p) is Asts.GenericTypeParameterOptionalAst:
                new_params.append(Asts.GenericTypeParameterRequiredAst(p.pos, name=p.name, constraints=p.constraints))
            elif type(p) is Asts.GenericCompParameterOptionalAst:
                new_params.append(Asts.GenericCompParameterRequiredAst(p.pos, name=p.name, type=p.type))
            else:
                new_params.append(p)
        return GenericParameterGroupAst(self.pos, self.tok_l, new_params, self.tok_r)

    def qualify_types(self, sm: ScopeManager, **kwargs) -> None:
        # Qualify the types of the generic parameters.
        for p in self.parameters:
            p.qualify_types(sm, **kwargs)

            if isinstance(p, Asts.GenericCompParameterAst):
                sm.current_scope.get_symbol(p.name).type = p.type

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # Check there are no duplicate generic parameter names.
        generic_parameter_names = [p.name for p in self.parameters]
        if duplicates := SequenceUtils.duplicates(generic_parameter_names):
            raise SemanticErrors.IdentifierDuplicationError().add(duplicates[0], duplicates[1], "generic parameter")

        # Check the generic parameters are in the correct order.
        if dif := AstOrderingUtils.order_params(self.parameters):
            raise SemanticErrors.OrderInvalidError().add(dif[0][0], dif[0][1], dif[1][0], dif[1][1], "generic parameter")

        # Analyse the parameters.
        for p in self.parameters:
            p.analyse_semantics(sm, **kwargs)

    def check_memory(self, sm: ScopeManager, **kwargs) -> None:
        # Check the memory of the parameters.
        for p in self.parameters:
            p.check_memory(sm, **kwargs)


__all__ = [
    "GenericParameterGroupAst"]
