from render_engine.css_lib.parser import CSSParser


def transform_prelude(prelude):
    transformed = []
    for token in prelude:
        if token.token_type() != "whitespace-token":
            transformed.append(token.value)
    return transformed


class StyleRule:
    def __init__(self, prelude, declarations):
        self.prelude = prelude
        self.declarations = declarations

    def __repr__(self):
        prelude = ', '.join(self.prelude)
        declarations = '\n\t'.join([str(declaration) for declaration in self.declarations])
        return f"{prelude} {{\n\t{declarations}\n}}"


class UglyParser:
    def __init__(self, source):
        self.parser = CSSParser(source)
        self.parsed = self.parser.parse_a_stylesheet()

    def ugly_parse(self):
        stylesheet = []
        for i in range(len(self.parsed)):
            style_rule = self.parsed[i]
            prelude = transform_prelude(style_rule.prelude)
            declarations = CSSParser(style_rule.block.value, from_tokens=True).consume_a_style_blocks_contents()

            stylesheet.append(StyleRule(prelude, declarations))

        return stylesheet
