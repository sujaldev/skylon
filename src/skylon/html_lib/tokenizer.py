"""
THE TOKENIZER BREAKS DOWN A SOURCE STREAM OF CHARACTERS INTO TOKENS. A TOKEN CAN BE A GROUP OF CHARACTERS,
THAT TOGETHER HAVE A SPECIAL MEANING IN THAT LANGUAGE.
FOR EXAMPLE THE SENTENCE "A BROWN CAT" COULD BE TOKENIZED AS:
[<A, ARTICLE>, <BROWN, ADJECTIVE>, <CAT, NOUN>]

IF A LANGUAGE'S VOCABULARY CAN BE DEFINED WITH REGULAR EXPRESSIONS, IT IS A CONTEXT FREE GRAMMAR.
PARSING SUCH LANGUAGES IS EASIER. HTML IS NOT SUCH A LANGUAGE AND HAS TO PARSED BY WHAT'S CALLED
A STATE MACHINE. THE STATE MACHINE TO TOKENIZE HTML IS DESCRIBE HERE:
https://html.spec.whatwg.org/multipage/parsing.html#tokenization
"""
from src.browser_engine.html_lib.structures.TOKENS import *

from src.browser_engine.helpers.preprocessor import preprocess_html
from src.browser_engine.helpers.stream import CharStream
from src.browser_engine.helpers.funcs import inside
from src.browser_engine.helpers.CONSTANTS import *


class HTMLTokenizer:
    def __init__(self, source):
        # INITIALIZE STREAM
        preprocessed_stream = preprocess_html(source)
        self.stream = CharStream(preprocessed_stream)

        # TOKENIZER STATE
        self.state = self.data_state  # DATA STATE IS THE DEFAULT STATE AS MENTIONED IN THE SPECIFICATION
        self.new_token_emitted = False

        # TOKENIZER OUTPUT
        self.output = []  # CALLING A TOKEN'S EMIT METHOD APPENDS THE TOKEN IN THIS LIST
        self.errors = []

        # BUFFERS
        self.temp_buffer = ""
        self.token_buffer = None
        self.return_state = None
        self.last_emitted_start_tag_name = None

        # TOKENIZE RIGHT AWAY
        self.tokenize()

    ########################################################
    # ALGORITHMS
    def emit(self, new_token=None):
        if new_token is None:
            token = self.token_buffer
        else:
            token = new_token

        token.emit_to(self)

        self.new_token_emitted = True
        self.token_buffer = None
        self.temp_buffer = ""

    def generate_parse_error(self, err_message):
        self.errors.append(err_message)

    ########################################################
    # STATES
    def data_state(self):
        current_char, next_char = self.stream.consume()

        if current_char == "&":
            raise NotImplementedError

        elif current_char == "<":
            self.state = self.tag_open_state

        elif current_char == NULL:
            self.generate_parse_error("UNEXPECTED NULL CHARACTER")
            self.emit(CharacterToken(current_char))

        elif current_char == EOF:
            self.emit(EOFToken())

        else:
            self.emit(CharacterToken(current_char))

    ########################################################
    def tag_open_state(self):
        current_char, next_char = self.stream.consume()

        if current_char == "!":
            raise NotImplementedError

        elif current_char == "/":
            self.state = self.end_tag_open_state

        elif inside(ASCII_ALPHA, current_char):
            self.token_buffer = StartTagToken()
            self.stream.reconsuming = True
            self.state = self.tag_name_state

        elif current_char == "?":
            raise NotImplementedError

        elif current_char == EOF:
            self.generate_parse_error("EOF BEFORE TAG NAME")
            self.emit(CharacterToken("<"))
            self.emit(EOFToken())

        else:
            self.generate_parse_error("INVALID FIRST CHARACTER OF TAG NAME")
            self.emit(CharacterToken("<"))
            self.stream.reconsuming = True
            self.state = self.data_state

    def end_tag_open_state(self):
        current_char, next_char = self.stream.consume()

        if inside(ASCII_ALPHA, current_char):
            self.token_buffer = EndTagToken()
            self.stream.reconsuming = True
            self.state = self.tag_name_state

        elif current_char == ">":
            self.generate_parse_error("MISSING END TAG NAME")
            self.state = self.data_state

        elif current_char == EOF:
            self.generate_parse_error("EOF BEFORE TAGE NAME")
            self.emit(CharacterToken("</"))
            self.emit(EOFToken())

        else:
            raise NotImplementedError

    def tag_name_state(self):
        current_char, next_char = self.stream.consume()

        if current_char in [TAB, NEWLINE, FORM_FEED, SPACE]:
            self.state = self.before_attr_name_state

        elif current_char == "/":
            self.state = self.self_closing_start_tag_state

        elif current_char == ">":
            self.state = self.data_state
            self.emit()

        elif inside(ASCII_UPPER_ALPHA, current_char):
            self.token_buffer.tag_name = current_char.lower()

        elif current_char == NULL:
            self.generate_parse_error("UNEXPECTED NULL CHARACTER")
            self.token_buffer.tag_name += REPLACEMENT_CHARACTER

        elif current_char == EOF:
            self.generate_parse_error("EOF IN TAG")
            self.emit(EOFToken())

        else:
            self.token_buffer.tag_name += current_char

    ########################################################
    def before_attr_name_state(self):
        current_char, next_char = self.stream.consume()

        if current_char in [TAB, NEWLINE, FORM_FEED, SPACE]:
            return  # IGNORE SUCH CHARACTERS

        elif current_char in ["/", ">", EOF]:
            self.stream.reconsuming = True
            self.state = self.after_attr_name_state

        elif current_char == "=":
            self.generate_parse_error("UNEXPECTED EQUALS SIGN BEFORE ATTRIBUTE NAME")
            self.token_buffer.new_attr(attr_name=current_char)
            self.state = self.attr_name_state

        else:
            self.token_buffer.new_attr()
            self.stream.reconsuming = True
            self.state = self.attr_name_state

    def attr_name_state(self):
        current_char, next_char = self.stream.consume()

        if current_char in [TAB, NEWLINE, FORM_FEED, SPACE, "/", ">", EOF]:
            self.stream.reconsuming = True
            self.state = self.after_attr_name_state

        elif current_char == "=":
            self.state = self.before_attr_value_state

        elif inside(ASCII_UPPER_ALPHA, current_char):
            self.token_buffer.append_to_current_attr_name(current_char)

        elif current_char == NULL:
            self.generate_parse_error("UNEXPECTED NULL CHARACTER")
            self.token_buffer.append_to_current_attr_name(REPLACEMENT_CHARACTER)

        elif current_char in ['"', "'", "<"]:
            self.generate_parse_error("UNEXPECTED CHARACTER IN ATTRIBUTE NAME")
            self.token_buffer.append_to_current_attr_name(current_char)

        else:
            self.token_buffer.append_to_current_attr_name(current_char)

    def after_attr_name_state(self):
        current_char, next_char = self.stream.consume()

        if current_char in [TAB, NEWLINE, FORM_FEED, SPACE]:
            return  # IGNORE SUCH CHARACTERS

        elif current_char == "/":
            self.state = self.self_closing_start_tag_state

        elif current_char == "=":
            self.state = self.before_attr_value_state

        elif current_char == ">":
            self.state = self.data_state
            self.emit()

        elif current_char == EOF:
            self.generate_parse_error("EOF IN TAG")
            self.emit(EOFToken())

        else:
            self.token_buffer.new_attr()
            self.stream.reconsuming = True
            self.state = self.attr_name_state

    def before_attr_value_state(self):
        current_char, next_char = self.stream.consume()

        if current_char in [TAB, NEWLINE, FORM_FEED, SPACE]:
            return  # IGNORE SUCH CHARACTERS

        elif current_char == '"':
            self.state = self.attr_value_double_quoted_state

        elif current_char == "'":
            self.state = self.attr_value_single_quoted_state

        elif current_char == ">":
            self.generate_parse_error("MISSING ATTRIBUTE VALUE")
            self.state = self.data_state
            self.emit()

        else:
            self.stream.reconsuming = True
            self.state = self.attr_value_unquoted_state

    def attr_value_double_quoted_state(self):
        current_char, next_char = self.stream.consume()

        if current_char == '"':
            self.state = self.after_attr_value_quoted_state

        elif current_char == "&":
            raise NotImplementedError

        elif current_char == NULL:
            self.generate_parse_error("UNEXPECTED NULL CHARACTER")
            self.token_buffer.append_to_current_attr_value(REPLACEMENT_CHARACTER)

        elif current_char == EOF:
            self.generate_parse_error("EOF IN TAG")
            self.emit(EOFToken())

        else:
            self.token_buffer.append_to_current_attr_value(current_char)

    def attr_value_single_quoted_state(self):
        current_char, next_char = self.stream.consume()

        if current_char == "'":
            self.state = self.after_attr_value_quoted_state

        elif current_char == "&":
            raise NotImplementedError

        elif current_char == NULL:
            self.generate_parse_error("UNEXPECTED NULL CHARACTER")
            self.token_buffer.append_to_current_attr_value(REPLACEMENT_CHARACTER)

        elif current_char == EOF:
            self.generate_parse_error("EOF IN TAG")
            self.emit(EOFToken())

        else:
            self.token_buffer.append_to_current_attr_value(current_char)

    def attr_value_unquoted_state(self):
        current_char, next_char = self.stream.consume()

        if current_char in [TAB, NEWLINE, FORM_FEED, SPACE]:
            self.state = self.before_attr_name_state

        elif current_char == "&":
            raise NotImplementedError

        elif current_char == ">":
            self.state = self.data_state
            self.emit()

        elif current_char == NULL:
            self.generate_parse_error("UNEXPECTED NULL CHARACTER")
            self.token_buffer.append_to_current_attr_value(REPLACEMENT_CHARACTER)

        elif current_char in ['"', "'", "<", "=", "`"]:
            self.generate_parse_error("UNEXPECTED CHARACTER IN UNQUOTED ATTRIBUTE VALUE")
            self.token_buffer.append_to_current_attr_value(current_char)

        elif current_char == EOF:
            self.generate_parse_error("EOF IN TAG")
            self.emit(EOFToken())

        else:
            self.token_buffer.append_to_current_attr_value(current_char)

    def after_attr_value_quoted_state(self):
        current_char, next_char = self.stream.consume()

        if current_char in [TAB, NEWLINE, FORM_FEED, SPACE]:
            self.state = self.before_attr_name_state

        elif current_char == "/":
            self.state = self.self_closing_start_tag_state

        elif current_char == ">":
            self.state = self.data_state
            self.emit()

        elif current_char == EOF:
            self.generate_parse_error("EOF IN TAG")
            self.emit(EOFToken())

        else:
            self.generate_parse_error("MISSING WHITESPACE BETWEEN ATTRIBUTES")
            self.stream.reconsuming = True
            self.state = self.before_attr_name_state

    def self_closing_start_tag_state(self):
        current_char, next_char = self.stream.consume()

        if current_char == ">":
            self.token_buffer.self_closing_flag = True
            self.state = self.data_state
            self.emit()

        elif current_char == EOF:
            self.generate_parse_error("EOF IN TAG")

        else:
            self.generate_parse_error("UNEXPECTED SOLIDUS IN TAG")
            self.stream.reconsuming = True
            self.state = self.before_attr_name_state

    ########################################################
    # STATES CONTROLLED BY TREE CONSTRUCTION STAGE
    def rcdata_state(self):
        current_char, next_char = self.stream.consume()

        if current_char == "&":
            raise NotImplementedError

        elif current_char == "<":
            self.state = self.rcdata_less_than_sign_state

        elif current_char == NULL:
            self.generate_parse_error("UNEXPECTED NULL CHARACTER")
            self.emit(CharacterToken(current_char))

        elif current_char == EOF:
            self.emit(EOFToken())

        else:
            self.emit(CharacterToken(current_char))

    def rcdata_less_than_sign_state(self):
        current_char, next_char = self.stream.consume()

        if current_char == "/":
            self.temp_buffer = ""
            self.state = self.rcdata_end_tag_open_state
        else:
            self.emit(CharacterToken("<"))
            self.stream.reconsuming = True
            self.state = self.rcdata_state

    def rcdata_end_tag_open_state(self):
        current_char, next_char = self.stream.consume()

        if inside(ASCII_ALPHA, current_char):
            self.token_buffer = EndTagToken()
            self.stream.reconsuming = True
            self.state = self.rcdata_end_tag_name_state
        else:
            self.emit(CharacterToken("</"))
            self.stream.reconsuming = True
            self.state = self.rcdata_state

    def rcdata_end_tag_name_state(self):
        current_char, next_char = self.stream.consume()

        is_appropriate_end_tag = self.token_buffer.tag_name == self.last_emitted_start_tag_name
        if inside(WHITESPACE, current_char) and is_appropriate_end_tag:
            self.state = self.before_attr_name_state

        elif current_char == "/" and is_appropriate_end_tag:
            self.state = self.self_closing_start_tag_state

        elif current_char == ">" and is_appropriate_end_tag:
            self.state = self.data_state
            self.emit(self.token_buffer)

        elif inside(ASCII_ALPHA, current_char):
            self.token_buffer.tag_name += current_char.lower()
            self.temp_buffer += current_char

        else:
            self.emit(CharacterToken("</" + self.temp_buffer))
            self.stream.reconsuming = True
            self.state = self.rcdata_state

    ########################################################
    def raw_text_state(self):
        current_char, next_char = self.stream.consume()

        if current_char == "&":
            raise NotImplementedError

        elif current_char == "<":
            self.state = self.raw_text_less_than_sign_state

        elif current_char == NULL:
            self.generate_parse_error("UNEXPECTED NULL CHARACTER")
            self.emit(CharacterToken(current_char))

        elif current_char == EOF:
            self.emit(EOFToken())

        else:
            self.emit(CharacterToken(current_char))

    def raw_text_less_than_sign_state(self):
        current_char, next_char = self.stream.consume()

        if current_char == "/":
            self.temp_buffer = ""
            self.state = self.raw_text_end_tag_open_state
        else:
            self.emit(CharacterToken("<"))
            self.stream.reconsuming = True
            self.state = self.raw_text_state

    def raw_text_end_tag_open_state(self):
        current_char, next_char = self.stream.consume()

        if inside(ASCII_ALPHA, current_char):
            self.token_buffer = EndTagToken()
            self.stream.reconsuming = True
            self.state = self.raw_text_end_tag_name_state
        else:
            self.emit(CharacterToken("</"))
            self.stream.reconsuming = True
            self.state = self.raw_text_state

    def raw_text_end_tag_name_state(self):
        current_char, next_char = self.stream.consume()

        is_appropriate_end_tag = self.token_buffer.tag_name == self.last_emitted_start_tag_name
        if inside(WHITESPACE, current_char) and is_appropriate_end_tag:
            self.state = self.before_attr_name_state

        elif current_char == "/" and is_appropriate_end_tag:
            self.state = self.self_closing_start_tag_state

        elif current_char == ">" and is_appropriate_end_tag:
            self.state = self.data_state
            self.emit(self.token_buffer)

        elif inside(ASCII_ALPHA, current_char):
            self.token_buffer.tag_name += current_char.lower()
            self.temp_buffer += current_char

        else:
            self.emit(CharacterToken("</" + self.temp_buffer))
            self.stream.reconsuming = True
            self.state = self.raw_text_state

    ########################################################
    def plaintext_state(self):
        current_char, next_char = self.stream.consume()

        if current_char == NULL:
            self.generate_parse_error("UNEXPECTED NULL CHARACTER")
            self.emit(CharacterToken(REPLACEMENT_CHARACTER))

        elif current_char == EOF:
            self.emit(EOFToken())

        else:
            self.emit(CharacterToken(current_char))

    ########################################################
    def tokenize(self):
        while not self.stream.is_truly_out_of_index():
            self.state()  # process stream according to rules in current state

            # TOKEN GENERATOR
            if self.new_token_emitted:
                emitted_token_is_character = self.output[-1].type == "character"
                next_char_is_character = self.stream.next_char not in ["&", "<", NULL, EOF]
                char_token_merge_required_before_emitting = emitted_token_is_character and next_char_is_character
                if char_token_merge_required_before_emitting:
                    # THIS CLAUSE MERGES CONSECUTIVE CHARACTER TOKENS INTO ONE
                    continue

                self.new_token_emitted = False
                yield self.output.pop()
