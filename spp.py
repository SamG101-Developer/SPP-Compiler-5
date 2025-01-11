__author__ = ["Sam Gardner"]
__license__ = "MIT"
__version__ = "5.0.0"
__maintainer__ = "Sam Gardner"
__email__ = "samuelgardner101@gmail.com"
__status__ = "Development"

from argparse import ArgumentParser
from pathlib import Path
import json_fix, os, sys, tomllib
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from SPPCompiler.Compiler.Compiler import Compiler


def create_argument_parser() -> ArgumentParser:
    # Commands for "init", "build", "run", "clean", "version", "help".

    parser = ArgumentParser(description="SPP Compiler")
    subparsers = parser.add_subparsers(help="command", required=True, dest="command")

    # init
    init_parser = subparsers.add_parser("init", help="initialize a new project")

    # vcs
    vcs_parser = subparsers.add_parser("vcs", help="initialize the VCS")

    # build
    build_parser = subparsers.add_parser("build", help="build the project")
    build_parser.add_argument("--mode", choices=["release", "debug"], default="debug")

    # run
    run_parser = subparsers.add_parser("run", help="run the project")
    run_parser.add_argument("--mode", choices=["release", "debug"], default="debug")

    # clean
    clean_parser = subparsers.add_parser("clean", help="clean the project")
    clean_parser.add_argument("--mode", choices=["release", "debug", "all"], default="all")

    # version
    version_parser = subparsers.add_parser("version", help="show the version")

    # help
    help_parser = subparsers.add_parser("help", help="show help")

    return parser


def handle_init(args):
    # Check the directory is empty.
    cwd = Path.cwd()
    if any(cwd.iterdir()):
        print("Directory is not empty")
        return

    # Create the directory structure.
    (cwd / "src").mkdir()
    (cwd / "src" / cwd.name).mkdir()
    (cwd / "bin").mkdir()

    # Create the main file and config file.
    with open(cwd / "src" / "main.spp", "w") as f:
        f.write(
            "fun main(args: std::Vec[std::Str]) -> std::Void {\n"
            "    ret\n"
            "}\n")

    with open(cwd / "spp.toml", "w") as f:
        f.write(
            f"[project]\n"
            f"name = \"{cwd.name}\"\n"
            f"version = \"0.1.0\"\n"
            f"\n"
            f"[vcs]\n"
            f"std = {{ git = \"https://github.com/SamG101-Developer/SPP-STL\", branch = \"master\" }}")


def handle_vcs(args):
    # If there is a [vcs] section in the TOML file, then create a "vcs" folder.
    toml = {}
    with open("spp.toml", "rb") as f:
        toml = tomllib.load(f)

    if "vcs" in toml:
        (Path.cwd() / "vcs").mkdir(exist_ok=True)
    else:
        return

    # For each "vcs" entry, clone the repository into the "vcs" folder.
    os.chdir("vcs")
    for repo_name, repo_info in toml.get("vcs").items():
        repo_url = repo_info.get("git")
        repo_branch = repo_info.get("branch", "master")

        if not Path(repo_name).exists():
            (Path.cwd() / repo_name).mkdir()
            os.system(f"git clone --branch {repo_branch} {repo_url} {repo_name}")

        else:
            # Todo: check for updates in the repository.
            ...

    os.chdir("..")


def handle_build(args):
    # Handle VCS
    handle_vcs(args)

    # Compile the project.
    mode = Compiler.Mode.Debug if args.mode == "debug" else Compiler.Mode.Release
    c = Compiler(mode)


def handle_run(args):
    handle_build(args)
    ...


def handle_clean(args):
    # Clean the release and debug "bin" folders.
    if args.mode == "all":
        (Path.cwd() / "bin/debug").rmdir()
        (Path.cwd() / "bin/release").rmdir()

    # Clean the release or debug "bin" folder.
    else:
        (Path.cwd() / "bin" / args.mode).rmdir()


def handle_version(args):
    print(__version__)


def handle_help(args):
    print("Help")


def main():
    parser = create_argument_parser()
    args = parser.parse_args(sys.argv[1:])
    getattr(sys.modules[__name__], f"handle_{args.command}")(args)


if __name__ == "__main__":
    main()
