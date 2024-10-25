__author__ = ["Sam Gardner"]
__license__ = "MIT"
__version__ = "5.0.0"
__maintainer__ = "Sam Gardner"
__email__ = "samuelgardner101@gmail.com"
__status__ = "Development"

import json_fix
from SPPCompiler.Compiler.Compiler import Compiler


def main():
    c = Compiler("project\\src", mode=Compiler.Mode.Debug)


if __name__ == "__main__":
    main()
