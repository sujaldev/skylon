"""
THIS STAGE PRODUCES A STYLESHEET OBJECT AS DESCRIBE HERE:
https://www.w3.org/TR/css-syntax-3/#parsing
"""

from src.browser_engine.css_lib.structures.TOKENS import *
from src.browser_engine.css_lib.tokenizer import CSSTokenizer
from src.browser_engine.css_lib.structures.CSSOM import *


class InfiniteList(list):
    def __getitem__(self, item):
        try:
            return super().__getitem__(item)
        except IndexError:
            return create_token("EOF-token")


class CSSTokenStream:
    def __init__(self, stream):
        self.stream = InfiniteList(stream)

        self.index = 0
        self.current_token = None
        self.next_token = self.stream[self.index]

        self.reconsuming = False

    def consume(self, step=1):
        if self.reconsuming:
            return self.reconsume()

        self.current_token = self.next_token
        self.index += step
        self.next_token = self.stream[self.index]

        return self.current_token, self.next_token

    def reconsume(self):
        self.reconsuming = False
        return self.current_token, self.next_token

    def is_truly_out_of_index(self):
        # The index could be out of range but processing should continue until no reconsumption is required.
        is_out_of_index = self.index >= len(self.stream) or len(self.stream) == 0
        return is_out_of_index and not self.reconsuming


class CSSParser:
    def __init__(self, source):
        self.stream = CSSTokenizer(source).output
        self.stream = CSSTokenStream(self.stream)

        self.errors = 0

    def parse_error(self):
        self.errors += 1

    def consume(self, step=1):
        return self.stream.consume(step)

    # ENTRY POINTS
    def parse_a_stylesheet(self):
        rules = self.consume_a_list_of_rules(top_level_flag=True)
        return rules

    # PARSER ALGORITHMS
    def consume_a_list_of_rules(self, top_level_flag=False):
        rules = []
        while True:
            current_token, next_token = self.consume()
            token_type = current_token.token_type()

            if token_type == "whitespace-token":
                pass  # ignore

            elif token_type == "EOF-token":
                return rules

            elif token_type in ["CDO-token", "CDC-token"]:
                if not top_level_flag:
                    self.stream.reconsuming = True
                    qualified_rule = self.consume_a_qualified_rule()
                    if qualified_rule is not None:
                        rules.append(qualified_rule)

            elif token_type == "at-keyword-token":
                self.stream.reconsuming = True
                at_rule = self.consume_an_at_rule()
                rules.append(at_rule)

            else:
                self.stream.reconsuming = True
                qualified_rule = self.consume_a_qualified_rule()
                if qualified_rule is not None:
                    rules.append(qualified_rule)

    def consume_an_at_rule(self):
        current_token, next_token = self.consume()
        at_rule = AtRule(name=current_token.value)

        while True:
            current_token, next_token = self.consume()
            token_type = current_token.token_type()

            if token_type == "semicolon-token":
                return at_rule

            elif token_type == "EOF-token":
                self.parse_error()
                return at_rule

            elif token_type == "{-token":
                at_rule.block = self.consume_a_simple_block()
                return at_rule

            else:
                self.stream.reconsuming = True
                at_rule.prelude.append(self.consume_a_component_value())

    def consume_a_qualified_rule(self):
        qualified_rule = QualifiedRule()

        while True:
            current_token, next_token = self.consume()
            token_type = current_token.token_type()

            if token_type == "EOF-token":
                self.parse_error()
                return

            elif token_type == "{-token":
                qualified_rule.block = self.consume_a_simple_block()
                return qualified_rule

            else:
                self.stream.reconsuming = True
                qualified_rule.prelude.append(self.consume_a_component_value())

    def consume_a_component_value(self):
        current_token, next_token = self.consume()
        token_type = current_token.token_type()

        if token_type in ["{-token", "[-token", "(-token"]:
            return self.consume_a_simple_block()

        elif token_type == "function-token":
            return self.consume_a_function()

        else:
            return current_token

    def consume_a_simple_block(self):
        current_token = self.stream.current_token
        ending_token_map = {
            "{-token": "}-token",
            "[-token": "]-token",
            "(-token": ")-token"
        }
        ending_token_type = ending_token_map[current_token.token_type()]
        simple_block = SimpleBlock(current_token)

        while True:
            current_token, next_token = self.consume()
            token_type = current_token.token_type()

            if token_type == ending_token_type:
                return simple_block

            elif token_type == "EOF-token":
                self.parse_error()
                return simple_block

            else:
                self.stream.reconsuming = True
                simple_block.value.append(self.consume_a_component_value())

    def consume_a_function(self):
        current_token = self.stream.current_token
        func = CSSFunction(name=current_token.value)

        while True:
            current_token, next_token = self.consume()
            token_type = current_token.token_type()

            if token_type == ")-token":
                return func

            elif token_type == "EOF-token":
                self.parse_error()
                return func

            else:
                self.stream.reconsuming = True
                func.value.append(self.consume_a_component_value())
