EOF = ""
NULL = "\u0000"

NEWLINE = "\u000A"
FORM_FEED = "\u000C"
CARRIAGE_RETURN = "\u000D"
TAB = "\u0009"
SPACE = "\u0020"

REPLACEMENT_CHARACTER = "\uFFFD"

WHITESPACE = (TAB, NEWLINE, FORM_FEED, CARRIAGE_RETURN, SPACE)

ASCII_DIGIT = "0123456789"
ASCII_UPPER_HEX_DIGIT = ASCII_DIGIT + "ABCDEF"
ASCII_LOWER_HEX_DIGIT = ASCII_DIGIT + "abcdef"
ASCII_HEX_DIGIT = ASCII_UPPER_HEX_DIGIT + ASCII_LOWER_HEX_DIGIT
ASCII_UPPER_ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ASCII_LOWER_ALPHA = "abcdefghijklmnopqrstuvwxyz"
ASCII_ALPHA = ASCII_LOWER_ALPHA + ASCII_UPPER_ALPHA
ASCII_ALPHANUMERIC = ASCII_ALPHA + ASCII_DIGIT

# NAMESPACES
HTML_NAMESPACE = "http://www.w3.org/1999/xhtml"
MATH_ML_NAMESPACE = "http://www.w3.org/1998/Math/MathML"
SVG_NAMESPACE = "http://www.w3.org/2000/svg"
XLINK_NAMESPACE = "http://www.w3.org/1999/xlink"
XML_NAMESPACE = "http://www.w3.org/XML/1998/namespace"
XMLNS_NAMESPACE = "http://www.w3.org/2000/xmlns/"

UNACCEPTED_TAGS_IN_FOREIGN_CONTENT = [
    "b", "big", "blockquote", "body", "br", "center", "code", "dd", "div", "dl", "dt", "em", "embed", "h1", "h2", "h3",
    "h4", "h5", "h6", "head", "hr", "i", "img", "li", "listing", "menu", "meta", "nobr", "ol", "p", "pre", "ruby", "s",
    "small", "span", "strong", "strike", "sub", "sup", "table", "tt", "u", "ul", "var"
]

MATH_ML_TEXT_INTEGRATION_POINTS = [
    "mi",
    "mo",
    "mn",
    "ms",
    "mtext"
]


def is_html_integration_point(element):
    if element.type == "annotation-xml":
        return element.attributes["encoding"].lower() in ["text/html", "application/xhtml+xml"]

    return element.type in ["foreignObject", "desc", "title"]  # POSSIBLE BUG DUE TO TITLE (title is also an html tag)


SPECIAL_NODES = [
    "address", "applet", "area", "article", "aside", "base", "basefont", "bgsound", "blockquote", "body", "br",
    "button", "caption", "center", "col", "colgroup", "dd", "details", "dir", "div", "dl", "dt", "embed", "fieldset",
    "figcaption", "figure", "footer", "form", "frame", "frameset", "h1", "h2", "h3", "h4", "h5", "h6", "head", "header",
    "hgroup", "hr", "html", "iframe", "img", "input", "keygen", "li", "link", "listing", "main", "marquee", "menu",
    "meta", "nav", "noembed", "noframes", "noscript", "object", "ol", "p", "param", "plaintext", "pre", "script",
    "section", "select", "source", "style", "summary", "table", "tbody", "td", "template", "textarea", "tfoot",
    "th", "thead", "title", "tr", "track", "ul", "wbr", "xmp", "mi", "mo", "mn", "ms", "mtext", "annotation-xml",
    "foreignObject", "desc", "title"
]
VOID_ELEMENTS = ["area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track",
                 "wbr"]

MAXIMUM_ALLOWED_CODE_POINT = 1114111
