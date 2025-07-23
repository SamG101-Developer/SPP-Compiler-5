import os
import sys

from pygments.lexer import RegexLexer
from pygments.token import Keyword, Name, String, Number, Operator, Punctuation, Text, Comment
from sphinx.application import Sphinx

sys.path.insert(0, os.path.abspath("../../src"))
sys.path.insert(0, os.path.abspath("_static/style"))

# -- Project information -----------------------------------------------------
project = "spp-compiler"
copyright = "2025, Sam Gardner"
author = "Sam Gardner"

# -- General configuration ---------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.todo",
    "sphinx_autodoc_typehints",
    "myst_parser"
]

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

autosummary_generate = True
autodoc_member_order = "bysource"
templates_path = ["_templates"]
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
html_theme = "furo"
html_theme_options = {
    "dark_css_variables": {
        "color-api-name": "#ffff00",
        "color-api-pre-name": "#00e626",
        "color-brand-primary": "#4dff6a",
        "color-brand-content": "#4dff6a",
        "color-brand-visited": "#4dff6a",
    }
}
html_static_path = ["_static"]


# -- Custom lexer class ------------------------------------------------------

class SppSphinxLexer(RegexLexer):
    name = "S++"
    aliases = ["spp", "s++"]
    filenames = ["*.spp"]

    tokens = {
        "root": [
            (r"\b(cls|fun|cor|sup|ext|mut|use|cmp|let|type|where|self|Self|case|of|loop|iter|in|else|gen|with|ret|exit|skip|is|as|or|and|not|async|true|false|res|caps)\b", Keyword),
            (r"\b\d+\b", Number),
            (r"\"[^\"]*\"", String),
            (r"[\+\-\*/%=\?<>&!]", Operator),
            (r"[\(\)\{\}\[\]:,@\.(->)]", Punctuation),
            (r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", Name),
            (r"\s+", Text),
            (r"#.*$", Comment.Singleline),
            (r"(##).*?(##)", Comment.Multiline),
        ],
    }


pygments_dark_style = "custom.SppSphinxStyle"


# -- Modify the setup --------------------------------------------------------
def setup(app: Sphinx) -> None:
    app.add_css_file("css/custom.css")
    app.add_lexer("S++", SppSphinxLexer)
