__author__ = ["Sam Gardner"]
__license__ = "MIT"
__version__ = "5.0.0"
__maintainer__ = "Sam Gardner"
__email__ = "samuelgardner101@gmail.com"
__status__ = "Development"

# import cProfile
# import datetime
import os
from argparse import Namespace

# import gprof2dot
# import graphviz
import json_fix

from spp_cli import handle_build


def main() -> None:
    project_dir = "project"
    os.chdir(project_dir)

    # p = cProfile.Profile()
    # p.enable()
    handle_build(Namespace(mode="rel"))
    # p.disable()

    # if not os.path.exists("profiles"):
    #     os.mkdir("profiles")
    # profile_path = f"profiles/{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
    # os.mkdir(profile_path)
    # p.dump_stats(f"{profile_path}/profile.prof")

    # Convert the profile.prof into a dot file & render it into a svg
    # gprof2dot.main(["-f", "pstats", f"{profile_path}/profile.prof", "-o", f"{profile_path}/profile.dot"])
    # graph = graphviz.Source.from_file(f"{profile_path}/profile.dot")
    # graph.render(f"{profile_path}/profile", format="svg")


if __name__ == "__main__":
    main()
