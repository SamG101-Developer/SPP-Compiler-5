import glob
import os
import shutil

# Remove all API generated files.
shutil.rmtree(".\\docs-compiler-sphinx\\source\\compiler-api", ignore_errors=True)

# Auto generate a rst module per compiler file, and make the specs folder.
os.system("sphinx-apidoc -o .\\docs-compiler-sphinx\\source\\compiler-api .\\src\\SPPCompiler --separate")

api_directory = ".\\docs-compiler-sphinx\\source\\compiler-api"
for file in glob.glob(os.path.join(api_directory, "*.rst")):
    with open(file, "r") as f:
        contents = f.read()
    contents = contents.replace(":maxdepth: 4", ":maxdepth: 1")
    with open(file, "w") as f:
        f.write(contents)

os.chdir(".\\docs-compiler-sphinx")
os.system("make html")
os.chdir("..")
