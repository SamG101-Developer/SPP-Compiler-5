from __future__ import annotations

from typing import Callable


class AstMutation:
    @staticmethod
    def inject_code[T](code: str, parsing_function: Callable[..., T], pos_adjust: int = 0) -> T:
        """!
        The code injection function is a utility function to generate extra code during semantic analysis to simplify
        AST construction. This is seen in preprocessing, and a range of argument manipulation and type generation.

        Args:
            code: The s++ code in string format to inject.
            parsing_function: The parsing rule to apply to the injected code.
            pos_adjust: An position adjustment for all ASTs parsed (so errors can print the injected code).

        Returns:
            The AST generated from the parser rule being applied over the code. All "pos" attributes will reflect the
            "pos_adjust" value.
        """

        # Import the Lexer and Parser here to prevent circular imports.
        from SPPCompiler.LexicalAnalysis.Lexer import SppLexer
        from SPPCompiler.SyntacticAnalysis.Parser import SppParser

        # Parse the code with the parser function and position adjustment. Because "parse_once" will always be used, use
        # the shortcut version by just applying the rule over the parser (which is how parse_once behaves anyway).
        parser = SppParser(SppLexer(code + "\n").lex(), injection_adjust_pos=pos_adjust)
        return parsing_function(parser)
