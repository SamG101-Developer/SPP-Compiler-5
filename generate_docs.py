import glob
import os
import shutil

shutil.rmtree(".\\docs-compiler-sphinx\\source\\api", ignore_errors=True)
os.system("sphinx-apidoc -o .\\docs-compiler-sphinx\\source\\api .\\src\\SPPCompiler --separate")

api_directory = ".\\docs-compiler-sphinx\\source\\api"
for file in glob.glob(os.path.join(api_directory, "*.rst")):
    with open(file, "r") as f:
        contents = f.read()
    contents = contents.replace(":maxdepth: 4", ":maxdepth: 1")
    with open(file, "w") as f:
        f.write(contents)

os.chdir(".\\docs-compiler-sphinx")
os.system("make html")
os.chdir("..")
