from __future__ import annotations

from typing import Callable


class CodeInjection:
    @staticmethod
    def inject_code[T](code: str, parsing_function: Callable[..., T], *, pos_adjust: int) -> T:
        """!
        The code injection function is a utility function to generate extra code during semantic analysis to simplify
        AST construction. This is seen in preprocessing, and a range of argument manipulation and type generation.

        @param code The s++ code in string format to inject.
        @param parsing_function The parsing rule to apply to the injected code.
        @param pos_adjust An position adjustment for all ASTs parsed (so errors can print the injected code).

        @return The AST generated from the parser rule being applied over the code. All "pos" attributes will reflect
        the "pos_adjust" value.
        """

        # Import the Lexer and Parser here to prevent circular imports.
        from SPPCompiler.LexicalAnalysis.Lexer import SppLexer
        from SPPCompiler.SyntacticAnalysis.Parser import SppParser

        # Parse the code with the parser function and position adjustment. Because "parse_once" will always be used, use
        # the shortcut version by just applying the rule over the parser (which is how parse_once behaves anyway).
        parser = SppParser(SppLexer(code).lex(), injection_adjust_pos=pos_adjust)
        result = parsing_function(parser)

        # Check the result is not None (just for internal testing), and then return the resulting AST.
        assert result is not None
        return result


__all__ = [
    "CodeInjection"]
