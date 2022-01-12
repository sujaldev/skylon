class DOCTYPEToken:
    def __init__(self):
        self.type = "DOCTYPE"

        self.name = "missing"
        self.public_identifier = "missing"
        self.system_identifier = "missing"
        self.force_quirks_flag = False
        self.attributes = {}

    def emit_to(self, tokenizer_instance):
        output_buffer = tokenizer_instance.output

        output_buffer.append(self)
        return self

    def __repr__(self):
        token_repr = f'<!DOCTYPE {self.name} PUBLIC "{self.public_identifier}" "{self.system_identifier}">'
        return token_repr


class StartTagToken:
    def __init__(self, tag_name=""):
        self.type = "start tag"

        self.tag_name = tag_name
        self.self_closing_flag = False
        self.attributes = []

        self.errors = []

    def new_attr(self, attr_name="", attr_val=""):
        self.attributes.append([attr_name, attr_val])

    def append_to_current_attr_name(self, char):
        self.attributes[-1][0] += char

    def append_to_current_attr_value(self, char):
        self.attributes[-1][1] += char

    def emit_to(self, tokenizer_instance):
        output_buffer = tokenizer_instance.output
        err_buffer = tokenizer_instance.errors
        tokenizer_instance.last_emitted_start_tag_name = self.tag_name

        self.remove_duplicate_attrs()
        output_buffer.append(self)
        for err in self.errors:
            err_buffer.append(err)

        self.convert_attrs_to_dict()
        return self

    def remove_duplicate_attrs(self):
        unique_attrs, unique_attr_names = [], []
        for attr in self.attributes:
            attr_name = attr[0]
            if attr_name not in unique_attrs:
                unique_attr_names.append(attr_name)
                unique_attrs.append(attr)

    def convert_attrs_to_dict(self):
        attr_dict = {}
        for attr_name, attr_value in self.attributes:
            attr_exists_already = attr_name in attr_dict.keys()
            if not attr_exists_already:
                attr_dict[attr_name] = attr_value
        self.attributes = attr_dict

    def __getitem__(self, item):
        for attr in self.attributes:
            attribute_name = attr[0]
            if attribute_name == item:
                value = attr[1]
                return value
        else:
            raise KeyError

    def __setitem__(self, key, value):
        self.attributes.append([key, value])
        self.remove_duplicate_attrs()

    def __repr__(self):
        attributes = ""
        for attr in self.attributes:
            attr_name, attr_val = attr[0], attr[1]
            attributes += f' {attr_name}="{attr_val}"'

        self_ending = "/" if self.self_closing_flag else ""

        token_repr = "<" + self.tag_name + attributes + self_ending + ">"
        return token_repr


class EndTagToken:
    def __init__(self, tag_name=""):
        self.type = "end tag"

        self.tag_name = tag_name
        self.self_closing_flag = False
        self.attributes = []

        self.errors = []

    def new_attr(self, attr_name="", attr_val=""):
        self.attributes.append([attr_name, attr_val])

    def append_to_current_attr_name(self, char):
        self.attributes[-1][0] += char

    def append_to_current_attr_val(self, char):
        self.attributes[-1][1] += char

    def emit_to(self, tokenizer_instance):
        output_buffer = tokenizer_instance.output
        err_buffer = tokenizer_instance.errors

        has_attributes = len(self.attributes) != 0
        has_trailing_solidus = self.self_closing_flag

        if has_attributes:
            self.errors.append("END TAG WITH ATTRIBUTES")
        if has_trailing_solidus:
            self.errors.append("END TAG WITH TRAILING SOLIDUS")

        output_buffer.append(self)
        for err in self.errors:
            err_buffer.append(err)
        return self

    def __repr__(self):
        attributes = ""
        for attr in self.attributes:
            attr_name, attr_val = attr[0], attr[1]
            attributes += f' {attr_name}="{attr_val}"'

        self_ending = "/" if self.self_closing_flag else ""

        token_repr = "</" + self.tag_name + attributes + self_ending + ">"
        return token_repr


class CommentToken:
    def __init__(self, data=""):
        self.type = "comment"
        self.tag_name = ""

        self.data = data

    def emit_to(self, tokenizer_instance):
        output_buffer = tokenizer_instance.output
        output_buffer.append(self)
        return self

    def __repr__(self):
        return f"<!--{self.data}-->"


class CharacterToken:
    def __init__(self, data=""):
        self.type = "character"
        self.tag_name = ""
        self.attributes = {}

        self.data = data

    def emit_to(self, tokenizer_instance):
        output_buffer = tokenizer_instance.output

        try:
            last_token = output_buffer[-1]
            if last_token.type == "character":
                output_buffer[-1].data += self.data
            else:
                output_buffer.append(self)
        except IndexError:
            output_buffer.append(self)
        return self

    def __repr__(self):
        return f"{self.data}"


class EOFToken:
    def __init__(self):
        self.type = "EOF"
        self.tag_name = ""
        self.attributes = {}

    def emit_to(self, tokenizer_instance):
        output_buffer = tokenizer_instance.output
        output_buffer.append(self)
        return self

    def __repr__(self):
        return "<EOF>"
