__author__ = ["Sam Gardner"]
__license__ = "MIT"
__version__ = "5.0.0"
__maintainer__ = "Sam Gardner"
__email__ = "samuelgardner101@gmail.com"
__status__ = "Development"


from SPPCompiler.LexicalAnalysis.Lexer import Lexer


with open("tst/LexicalAnalysis/code_1.spp", "r") as file:
    lexer = Lexer(file.read())
    tokens = lexer.lex()
    print("DONE")

