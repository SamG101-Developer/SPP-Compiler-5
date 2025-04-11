# Installation

## Installation Process

The Git repository of the compiler contains the source code of the compiler. Under the "releases" tab, you can find the
latest release of the compiler. The release contains the compiler binary, with releases for Windows, Linux and macOS,
with Windows and Linux binaries for both amd64 and arm64 architectures.

Once the compiler is downloaded, unzip the folder, and run the installer. This will automatically unzip the inner
folder (compiler) into the `program files` directory on Windows, and the `usr/local` directory on Linux and macOS. The
`spp` command will be added to the system path, so the compiler can be run from any directory.

The binary is a standalone executable, and does not require any dependencies to be installed on the system. Logging
files may be created in the compiler's folder, but no other files are created on the system.

The only folder created is the `spp` folder inside the `program files` or `usr/local` directory. The standard library is
included separately per project, similar to a module being installed in a Python venv.

## Updating the Compiler

The compiler can be updated from the command line to any version that has been released. Note that the standard library
is separate from the compiler, and is treated as any other installable 3rd party library, so is updated separately.

## Uninstalling the Compiler

To uninstall the compiler, run the uninstaller binary that is located in the same directory as the compiler binary. This
will remove the compiler from the system path, and delete the compiler folder and binary from the system. The compiler
folder can be deleted on its own, but the filepath will remain in the system path.
