__author__ = ["Sam Gardner"]
__license__ = "MIT"
__version__ = "5.0.0"
__maintainer__ = "Sam Gardner"
__email__ = "samuelgardner101@gmail.com"
__status__ = "Development"

from argparse import Namespace
import os, cProfile

from spp import handle_build


def main():
    project_dir = "project"
    os.chdir(project_dir)

    p = cProfile.Profile()
    p.enable()
    handle_build(Namespace(mode="release"))
    p.disable()
    p.dump_stats("profile.prof")


if __name__ == "__main__":
    main()
