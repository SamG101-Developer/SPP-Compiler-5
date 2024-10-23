__author__ = ["Sam Gardner"]
__license__ = "MIT"
__version__ = "5.0.0"
__maintainer__ = "Sam Gardner"
__email__ = "samuelgardner101@gmail.com"
__status__ = "Development"

from SPPCompiler.LexicalAnalysis.Lexer import Lexer
from SPPCompiler.SyntacticAnalysis.Parser import Parser
from SPPCompiler.Utils.ProgressBar import ProgressBar


def main():
    with open("tst/LexicalAnalysis/code_1.spp", "r") as file:
        tok = Lexer(file.read()).lex()
        bar = ProgressBar("Parsing", len(tok))
        ast = Parser(tok).parse()


if __name__ == "__main__":
    main()
