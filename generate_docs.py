import os
import shutil
import subprocess
from pathlib import Path

root = Path(__file__).parent.resolve()
docs_dir = root / "docs-compiler-sphinx"
source_dir = docs_dir / "source"
build_dir = docs_dir / "build"
api_dir = source_dir / "compiler-api"
src_dir = root / "src" / "SPPCompiler"

# Clear old build files.
shutil.rmtree(api_dir, ignore_errors=True)
shutil.rmtree(build_dir, ignore_errors=True)

# Generate the new module files for "compiler-api".
subprocess.run(["sphinx-apidoc", "-o", str(api_dir), str(src_dir), "--separate"], check=True)

# Adjust the max depth of displayed information.
for rst_file in api_dir.glob("*.rst"):
    contents = rst_file.read_text()
    contents = contents.replace(":maxdepth: 4", ":maxdepth: 1")
    rst_file.write_text(contents)

# Build the HTML documentation.
os.chdir(docs_dir)
subprocess.run(["make", "html"], check=True)
