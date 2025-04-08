from pygments.style import Style
from pygments.token import Keyword, Name, String, Number, Operator, Punctuation


class SppSphinxStyle(Style):
    default_style = ""
    background_color = "#1c1c1c"
    highlight_color = "#3c3c3c"
    styles = {
        Keyword: "#ff6000",
        Number: "#ff6000",
        String: "#00ff00",
        Operator: "#ffff00",
        Punctuation: "#ffff00",
        Name: "#c0c0c0",
    }


__all__ = [
    "SppSphinxStyle"]
