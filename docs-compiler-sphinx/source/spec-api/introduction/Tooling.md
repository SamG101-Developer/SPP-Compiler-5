# Tooling

## Commands

The `spp` tool allows several commands to be run, to create, manage and run S++ projects. The commands are:
- [`init`](#project-initialization): Create a new S++ project in the current folder. The project structure is created
  with the folders and `main.spp` file.
- [`build`](#project-building): Compile the current project. The compiler will compile all `.spp` files in the `src`
  folder, and output the binary to the `bin` folder. All `vcs/ext/ffi` dependencies will be linked automatically.
- [`run`](#project-running): Compile and run the current project. The steps are the same as `build`, but the binary is
  executed immediately after compilation.
- [`clean`](#project-cleaning): Clean the project. The folder containing the binary is emptied, and the project is
  ready to be built again. The binary folder is not deleted.
- [`vcs`](#project-vcs-updating): Install and update the vcs dependencies of the project. The compiler will check the
  `vcs` folder for newer versions of the dependencies, and will update them. Use fixed versions in the `spp.toml` file
  to prevent automatic updates.
- [`version`](#compiler-version): Display the version of the S++ compiler that is currently installed. This can also be
  used to list versions of the `vcs` and `ext` dependencies.
- [`help`](#compiler-help): Display the help message for the S++ compiler. This message contains a list of all
  commands, and a
  brief description of each command.

## Project Initialization

The `spp init` command creates the folders and files in the current directory to create a new S++ project. This will
enable the project to be built and run without structural errors. See the project structure section for more information
on the folders and files created.

If the folder is not empty, a confirmation prompt will be shown. If there is a `main.spp` file in the current directory,
and the overwrite prompt is confirmed, the `main.spp` file not be overwritten, as it assumed that a non-complete project
is being converted into a valid S++ project.

No arguments can be passed to the `init` command. The `spp.toml` project configuration that is generated holds all the
metadata that can be updated.

## Project Building

The `spp build` command is used to compile the current project. It will recursively search the `src` folder for all
`.spp` code files. The `vcs` and `ext` folders are then searched for code files too, and added to the module tree.
Finally, the stub files inside the `ffi` modules are also linked, for symbol information.

Once all the code has been compiled into llvm code, the `ffi` libraries are linked into the binary, and the binary is
output to the `bin` folder. The binary is placed in a subfolder of the build type (debug or release), and the
dependencies are placed in the same folder.

If the project is already built, and only a subset of the files have been modified, then only those files are
re-compiled. If part of the code changed is exportable (ie function signatures), then files that directly use these
exported symbols are also recompiled. If only a function body is changed, then only that file is recompiled.

Each stage of the compiler can be parallelized, as the order of files does not matter. However, a stage of the compiler
cannot begin until all modules have completed the previous stage. If a module contains an error, the build process
stops, and the error is displayed.

| Flag           | Description                                      |
|----------------|--------------------------------------------------|
| `--debug`      | Compiles the project in debug mode (default).    |
| `--release`    | Compiles the project in release mode.            |
| `--clean`      | Cleans the project before building.              |
| `--executable` | Compiles the project as an executable (default). |
| `--shared`     | Compiles the project as a shared library.        |
| `--static`     | Compiles the project as a static library.        |

The default command is `spp build --debug --executable --no-vcs-update`.

## Project Running

The `spp run` command can only be used if the `--executable` flag was used in the `build` step. It runs the built binary
from the `bin` folder. The binary is recompiled if there are any changes to the code, and is run immediately after
compilation. The build mode flag is required, to rebuild/run the correct binary.

| Flag        | Description                                   |
|-------------|-----------------------------------------------|
| `--debug`   | Compiles the project in debug mode (default). |
| `--release` | Compiles the project in release mode.         |
| `--clean`   | Cleans the project before building.           |

The default command is `spp run --debug`.

## Project Cleaning

The `spp clean` command is used to delete the build mode folder if a flag is passed, or all build mode folders if no
flag is passed. This will force the entire project to be re-built, as the binary is deleted. The `bin` folder is not
deleted, as it is part of the project structure; only emptied.

| Flag        | Description              |
|-------------|--------------------------|
| `--debug`   | Cleans the debug build.  |
| `--release` | Cleans the release build |

## Project VCS Updating

The `spp vcs` command is used to manage the vcs dependencies of the project. The compiler will check the `vcs` folder
for all the dependencies. If the dependencies are not present, they will be cloned from the repository. If the
dependencies are present, the compiler will try to `git pull` the repository to update the dependencies.

To prevent the automatic update of the dependencies, fixed versions can be specified in the `spp.toml` file. This will
prevent the compiler from updating the dependencies, and will only use the specified version. The `git pull` command is
skipped for fixed versions (matching a hash format).

The `spp build` command will run the `spp vcs` command every time. This is to ensure that the dependencies are up to
date, and that the project is built with the latest code.

## Compiler Version

The `spp version` command is used to display the version of the S++ compiler that is currently installed. This will
output the version number, and nothing else. The `--libraries` flag can be used to list the versions of the `vcs` and
`ext` libraries. This information is pulled from their respective `spp.toml` files, but is included as a convenience
tool.

| Flag          | Description                                          |
|---------------|------------------------------------------------------|
| `--libraries` | Lists the versions of the `vcs` and `ext` libraries. |

## Compiler Help

The `spp help` command is used to display a list of all commands and flags that can be passed to the commands.
