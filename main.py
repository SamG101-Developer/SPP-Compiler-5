__author__ = ["Sam Gardner"]
__license__ = "MIT"
__version__ = "5.0.0"
__maintainer__ = "Sam Gardner"
__email__ = "samuelgardner101@gmail.com"
__status__ = "Development"

from argparse import Namespace
import graphviz, gprof2dot
import os, cProfile
import std

from spp import handle_build


def main() -> None:
    # std.enable_type_checking(std.ErrorLevel.WARNING)/
    project_dir = "project"
    os.chdir(project_dir)

    # p = cProfile.Profile()
    # p.enable()
    handle_build(Namespace(mode="release"))
    # p.disable()
    # p.dump_stats("profile.prof")

    # convert profile.prof into a dot file
    # gprof2dot.main(["-f", "pstats", "profile.prof", "-o", "profile.dot"])
    #
    # # render the dot file into a png
    # graph = graphviz.Source.from_file("profile.dot")
    # graph.render("profile", format="svg")


if __name__ == "__main__":
    main()
