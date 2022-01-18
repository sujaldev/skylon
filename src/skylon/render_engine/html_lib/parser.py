"""
THIS IS THE TREE CONSTRUCTION STAGE AS SPECIFIED IN THE SPECIFICATION HERE:
https://html.spec.whatwg.org/multipage/parsing.html#tree-construction
"""
from render_engine.html_lib.structures.DOM import *
from render_engine.html_lib.structures.TOKENS import *
from render_engine.html_lib.tokenizer import HTMLTokenizer
from render_engine.helpers.CONSTANTS import VOID_ELEMENTS


class TokenStream:
    def __init__(self, source):
        self.tokenizer = HTMLTokenizer(source)
        self.token_generator = self.tokenizer.tokenize()
        self.current_token = None

        self.reprocessing = False
        self.out_of_tokens = False

    def next(self):
        if self.reprocessing:
            return self.reprocess()
        try:
            self.current_token = next(self.token_generator)
        except StopIteration:
            self.out_of_tokens = True
            self.current_token = EOFToken()

        return self.current_token

    def reprocess(self):
        self.reprocessing = False
        return self.current_token

    def is_truly_out_of_index(self):
        return self.out_of_tokens and not self.reprocessing


class HTMLParser:
    def __init__(self, source):
        self.token_stream = TokenStream(source)
        self.tokenizer = self.token_stream.tokenizer

        self.state = self.initial_state
        self.open_elements = []

        self.document = None

    def initial_state(self):
        token = self.token_stream.next()
        self.token_stream.reprocessing = True

        if token.type == "start tag":
            self.state = self.start_tag_state

        elif token.type == "end tag":
            self.state = self.end_tag_state

        elif token.type == "character":
            self.state = self.character_state

        else:
            print(f"Unimplemented Token: {token} -> {token.type} | SKIPPING...")

    def start_tag_state(self):
        token = self.token_stream.next()
        if token.type == "start tag":
            parent = self.open_elements[-1] if self.open_elements else None
            elem = Element(token, parent)
            if token.tag_name not in VOID_ELEMENTS:
                self.open_elements.append(elem)
            elif parent:
                parent.children.append(elem)
            if not self.document:
                self.document = elem

        elif token.type == "end tag":
            self.token_stream.reprocessing = True
            self.state = self.end_tag_state

        elif token.type == "character":
            self.token_stream.reprocessing = True
            self.state = self.character_state

        else:
            print(f"Unimplemented Token: {token} | SKIPPING...")

    def end_tag_state(self):
        token = self.token_stream.next()
        if token.type == "end tag":
            elem = self.open_elements.pop()
            if self.open_elements:
                parent = self.open_elements[-1]
                parent.children.append(elem)

        elif token.type == "start tag":
            self.token_stream.reprocessing = True
            self.state = self.start_tag_state

        elif token.type == "character":
            self.token_stream.reprocessing = True
            self.state = self.character_state

        else:
            print(f"Unimplemented Token: {token} | SKIPPING...")

    def character_state(self):
        token = self.token_stream.next()
        if token.type == "character":
            parent = self.open_elements[-1] if self.open_elements else None
            if token.data.isspace():
                return
            elem = TextNode(token, parent)
            if parent:
                parent.children.append(elem)

        elif token.type == "start tag":
            self.token_stream.reprocessing = True
            self.state = self.start_tag_state

        elif token.type == "end tag":
            self.token_stream.reprocessing = True
            self.state = self.end_tag_state

        else:
            print(f"Unimplemented Token: {token} | SKIPPING...")

    def parse(self):
        while not self.token_stream.is_truly_out_of_index():
            self.state()
