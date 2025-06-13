__author__ = ["Sam Gardner"]
__license__ = "MIT"
__version__ = "5.0.0"
__maintainer__ = "Sam Gardner"
__email__ = "samuelgardner101@gmail.com"
__status__ = "Development"

import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

import tomllib
import shutil
from argparse import ArgumentParser, Namespace
from pathlib import Path

from SPPCompiler.Compiler.Compiler import Compiler

# Constants
NULL_STDOUT = " > /dev/null 2>&1" if os.name == "posix" else " > NUL 2>&1"
OUT_FOLDER = "out"
SRC_FOLDER = "src"
FFI_FOLDER = "ffi"
VCS_FOLDER = "vcs"
MAIN_FILE = "main.spp"
TOML_FILE = "spp.toml"


def _shared_library_extension() -> str:
    # Get the shared library extension for the current platform.
    if os.name == "nt":
        return "dll"
    elif os.name == "darwin":
        return "dylib"
    else:
        return "so"


def cli() -> ArgumentParser:
    # Create the parser and add the subcommands holder.
    parser = ArgumentParser(description="S++ Programming Language Compiler")
    subcommands = parser.add_subparsers(help="command", required=True, dest="command")

    # Register the subcommands and their arguments.
    subcommands.add_parser("init", help="Initialize a new project")
    subcommands.add_parser("vcs", help="Manage the version control system")
    subcommands.add_parser("build", help="Build the S++ project").add_argument("--mode", "-m", choices=["dev", "rel"], default="dev", help="Choose the build mode")
    subcommands.add_parser("run", help="Run the S++ project").add_argument("--mode", "-m", choices=["dev", "rel"], default="dev", help="Choose the run mode")
    subcommands.add_parser("clean", help="Clean the S++ project").add_argument("--mode", "-m", choices=["dev", "rel", "all"], default="all", help="Choose the clean mode")
    subcommands.add_parser("test", help="Test the S++ project").add_argument("--mode", "-m", choices=["dev", "rel"], default="dev", help="Choose the test mode")
    subcommands.add_parser("validate", help="Validate the S++ project structure")
    subcommands.add_parser("version", help="Show the version")
    subcommands.add_parser("help", help="Show help")

    # Return the parser.
    return parser


def handle_init() -> None:
    # Check if the current directory is empty or not.
    cwd = Path.cwd()
    if any(cwd.iterdir()):
        print("Directory is not empty")
        return

    # Determine the directory structure (src and bin folders).
    bin_directory = cwd / OUT_FOLDER
    src_directory = cwd / SRC_FOLDER
    ffi_directory = cwd / FFI_FOLDER
    src_folder = src_directory / cwd.name
    main_file = src_folder / MAIN_FILE
    toml_file = cwd / TOML_FILE

    # Create the directory structure.
    bin_directory.mkdir()
    src_directory.mkdir()
    ffi_directory.mkdir()
    src_folder.mkdir()

    # Create src/main.spp and spp.toml files.
    with open(main_file, "w") as fo:
        fo.write("fun main(args: std::vector::Vec[std::string::Str]) -> std::void::Void {\n    ret\n}\n")
    with open(toml_file, "w") as fo:
        fo.write(f"[project]\nname = \"{cwd.name}\"\nversion = \"0.1.0\"\n\n[vcs]\nstd = {{ git = \"https://github.com/SamG101-Developer/SPP-STL\", branch = \"master\" }}")


def handle_vcs() -> None:
    # Check if the spp.toml file exists.
    cwd = Path.cwd()
    toml_file = cwd / TOML_FILE
    if not toml_file.exists():
        print("spp.toml file does not exist")
        return

    # Parse the spp.toml file and check if the vcs section exists.
    with open(toml_file, "rb") as fo:
        toml = tomllib.load(fo)
    vcs = toml.get("vcs")
    if not vcs: return

    # Ensure the "ffi" folder exists, as vcs repositories may have their own "ffi" folders.
    ffi_folder = cwd / FFI_FOLDER
    if not ffi_folder.exists(): ffi_folder.mkdir()

    # Check if the "vcs" folder exists, create it if it doesn't.
    vcs_folder = cwd / VCS_FOLDER
    if not vcs_folder.exists(): vcs_folder.mkdir()
    os.chdir(vcs_folder)

    # Iterate over the vcs section and clone/update the repositories.
    for key, info in vcs.items():
        repo_name, repo_url, repo_branch = key, info.get("git"), info.get("branch", "master")
        repo_folder = vcs_folder / repo_name
        if not repo_folder.exists():
            os.system(f"git clone {repo_url} {repo_folder}")
            os.system(f"git -C {repo_folder} checkout {repo_branch} {NULL_STDOUT}")
            print(f"Cloned '{repo_name}' repository")
        else:
            os.system(f"git -C {repo_folder} pull origin {repo_branch}")
            os.system(f"git -C {repo_folder} checkout {repo_branch} {NULL_STDOUT}")
            print(f"Updated '{repo_name}' repository")

        # Copy all DLLs from the vcs's ffi folder into this project's ffi folder.
        # Todo: something about conflicting DLLs.
        ffi_repo_folder = repo_folder / FFI_FOLDER
        if ffi_repo_folder.exists():
            for lib in ffi_repo_folder.iterdir():
                print(f"Linking ffi library '{lib.name}' from '{repo_name}'")
                shutil.copytree(lib, ffi_folder / lib.name, dirs_exist_ok=True)

    # Reset the working directory.
    os.chdir(cwd)


def handle_build(args: Namespace, skip_vcs: bool = False) -> None:
    # Check if the bin directory exists, create it if it doesn't.
    cwd = Path.cwd()
    bin_directory = cwd / "out"
    if not bin_directory.exists(): bin_directory.mkdir()

    inner_bin_directory = bin_directory  / args.mode
    if not inner_bin_directory.exists(): inner_bin_directory.mkdir()

    # Validate the project structure.
    if not handle_validate():
        return

    # Handle vcs operations.
    if not skip_vcs:
        handle_vcs()

    # Validate the project structure (including vcs).
    if not handle_validate():
        return

    # Compile the code.
    try:
        Compiler(Compiler.Mode.Dev if args.mode == "dev" else Compiler.Mode.Rel)
        os.chdir(cwd.parent)
    except BaseException as e:
        os.chdir(cwd.parent)
        raise e


def handle_run(args: Namespace) -> None:
    handle_build(args)
    # Todo


def handle_test(args: Namespace) -> None:
    handle_build(args)
    # Todo


def handle_version() -> None:
    print(__version__)


def handle_help() -> None:
    print(cli().format_help())


def handle_validate() -> bool:
    # Check there is a spp.toml, src, and src/main.spp file.
    cwd = Path.cwd()
    toml_file = cwd / TOML_FILE
    src_directory = cwd / SRC_FOLDER
    main_file = src_directory / MAIN_FILE

    if not toml_file.exists():
        print("spp.toml file does not exist")
        return False

    if not src_directory.exists():
        print("src directory does not exist")
        return False

    if not main_file.exists():
        print("main.spp file does not exist")
        return False

    # If there is a VCS folder, run the validation steps inside each repository.
    vcs_folder = cwd / VCS_FOLDER
    if vcs_folder.exists():
        for repo in vcs_folder.iterdir():
            os.chdir(repo)
            handle_validate()
            os.chdir(cwd)

    # If there is an FFI folder, check each subfolder is structured properly.
    ffi_folder = cwd / FFI_FOLDER
    if ffi_folder.exists():
        ext = _shared_library_extension()

        for lib_folder in ffi_folder.iterdir():
            if not lib_folder.is_dir():
                print(f"{lib_folder.name} is not a directory")
                return False

            # Check for "library_name/lib/library_name.{ext}" and "library_name/stub.spp" files.
            lib_name = lib_folder.name
            lib_file = lib_folder / "lib" / f"{lib_name}.{ext}"
            stub_file = lib_folder / "stub.spp"

            if not lib_file.exists():
                print(f"{lib_name}.{ext} file does not exist")
                return False

            if not stub_file.exists():
                print("stub.spp file does not exist")
                return False

    # Return True if all checks pass.
    return True


def main() -> None:
    # Parse the arguments and handle the subcommands.
    args = cli().parse_args()
    match args.command:
        case "init": handle_init()
        case "vcs": handle_vcs()
        case "build": handle_build(args)
        case "run": handle_run(args)
        case "test": handle_test(args)
        case "version": handle_version()
        case "help": handle_help()


if __name__ == "__main__":
    main()
