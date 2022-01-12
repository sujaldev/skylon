"""
THIS IS THE TOKENIZATION STAGE FOR CSS AS DESCRIBE HERE:
https://www.w3.org/TR/css-syntax-3/#tokenizer-algorithms
"""
from src.browser_engine.css_lib.structures.TOKENS import create_token

from src.browser_engine.helpers.preprocessor import preprocess_css
from src.browser_engine.helpers.stream import CharStream
from src.browser_engine.helpers.funcs import *
from src.browser_engine.helpers.CONSTANTS import *


# noinspection PyMethodMayBeStatic
class CSSTokenizer:
    def __init__(self, source):
        # INITIALIZE STREAM
        preprocessed_stream = preprocess_css(source)
        self.stream = CharStream(preprocessed_stream)

        # BUFFERS
        self.current_token = None
        self.errors = 0

        self.output = []
        self.tokenize()
        self.append_eof_token_if_not_exists()

    def append_eof_token_if_not_exists(self):
        try:
            if self.output[-1].token_type() != "EOF-token":
                self.output.append(create_token("EOF-token"))
        except IndexError:
            self.output.append(create_token("EOF-token"))

    def consume(self, step=1):
        return self.stream.consume(step)

    def parse_error(self):
        self.errors += 1

    def consume_a_token(self):
        # RETURNS A TOKEN OF ANY TYPE

        self.consume_comments()
        current_char, next_char = self.consume()

        if inside(WHITESPACE, current_char):
            while inside(WHITESPACE, next_char):
                current_char, next_char = self.consume()

            self.current_token = create_token("whitespace-token")
            return self.current_token

        elif current_char == '"':
            self.current_token = self.consume_a_string_token()
            return self.current_token

        elif current_char == "#":
            second_next_char = self.stream.nth_next_char()
            if is_name_code_point(next_char) or self.two_code_points_are_valid_escape(next_char, second_next_char):
                self.current_token = create_token("hash-token")
                third_next_char = self.stream.nth_next_char(2)
                if self.three_code_points_start_an_identifier(next_char, second_next_char, third_next_char):
                    self.current_token.type = "id"

                self.current_token.value = self.consume_a_name()
                return self.current_token
            else:
                self.current_token = create_token("delim-token")
                self.current_token.value = current_char
                return self.current_token

        elif current_char == "'":
            self.current_token = self.consume_a_string_token()
            return self.current_token

        elif current_char == "(":
            self.current_token = create_token("(-token")
            return self.current_token

        elif current_char == ")":
            self.current_token = create_token(")-token")
            return self.current_token

        elif current_char == "+":
            if self.three_code_points_start_a_number():
                self.stream.reconsuming = True
                self.current_token = self.consume_a_numeric_token()
                return self.current_token
            else:
                self.current_token = create_token("delim-token")
                self.current_token.value = current_char
                return self.current_token

        elif current_char == ",":
            self.current_token = create_token("comma-token")
            return self.current_token

        elif current_char == "-":
            # NEGATIVE NUMBER
            if self.three_code_points_start_a_number():
                self.stream.reconsuming = True
                self.current_token = self.consume_a_numeric_token()
                return self.current_token

            # COMMENT DATA CLOSE (CDC) -->
            elif (next_char, self.stream.nth_next_char()) == ("-", ">"):
                self.consume(2)
                self.current_token = create_token("CDC-token")
                return self.current_token

            elif self.three_code_points_start_an_identifier():
                self.stream.reconsuming = True
                self.current_token = self.consume_an_ident_like_token()
                return self.current_token

            else:
                self.current_token = create_token("delim-token")
                self.current_token.value = current_char
                return self.current_token

        elif current_char == ".":
            if self.three_code_points_start_a_number():
                self.stream.reconsuming = True
                self.current_token = self.consume_a_numeric_token()
                return self.current_token

            else:
                self.current_token = create_token("delim-token")
                self.current_token.value = current_char
                return self.current_token

        elif current_char == ":":
            self.current_token = create_token("colon-token")
            return self.current_token

        elif current_char == ";":
            self.current_token = create_token("semicolon-token")
            return self.current_token

        elif current_char == "<":
            second_next_char = self.stream.nth_next_char()
            third_next_char = self.stream.nth_next_char(2)
            is_comment_start = (next_char, second_next_char, third_next_char) == ("!", "-", "-")
            if is_comment_start:
                self.consume(3)
                self.current_token = create_token("CDO-token")
                return self.current_token

            else:
                self.current_token = create_token("delim-token")
                self.current_token.value = current_char
                return self.current_token

        elif current_char == "@":
            second_next_char = self.stream.nth_next_char()
            third_next_char = self.stream.nth_next_char(2)
            if self.three_code_points_start_an_identifier(next_char, second_next_char, third_next_char):
                self.current_token = create_token("at-keyword-token")
                self.current_token.value = self.consume_a_name()
                return self.current_token

            else:
                self.current_token = create_token("delim-token")
                self.current_token.value = current_char
                return self.current_token

        elif current_char == "[":
            self.current_token = create_token("[-token")
            return self.current_token

        elif current_char == "\\":
            if self.two_code_points_are_valid_escape():
                self.stream.reconsuming = True
                self.current_token = self.consume_an_ident_like_token()
                return self.current_token

            else:
                self.parse_error()
                self.current_token = create_token("delim-token")
                self.current_token.value = current_char
                return self.current_token

        elif current_char == "]":
            self.current_token = create_token("]-token")
            return self.current_token

        elif current_char == "{":
            self.current_token = create_token("{-token")
            return self.current_token

        elif current_char == "}":
            self.current_token = create_token("}-token")
            return self.current_token

        elif inside(ASCII_DIGIT, current_char):
            self.stream.reconsuming = True
            self.current_token = self.consume_a_numeric_token()
            return self.current_token

        elif is_name_code_point(current_char):
            self.stream.reconsuming = True
            self.current_token = self.consume_an_ident_like_token()
            return self.current_token

        elif current_char == EOF:
            self.current_token = create_token("EOF-token")
            return self.current_token

        else:
            self.current_token = create_token("delim-token")
            self.current_token.value = current_char
            return self.current_token

    def consume_comments(self):
        next_char, next_next_char = self.stream.next_char, self.stream.nth_next_char()
        is_comment_start = (next_char, next_next_char) == ("/", "*")
        if is_comment_start:
            self.consume(2)
            while True:
                next_char, next_next_char = self.stream.next_char, self.stream.nth_next_char()
                is_comment_end = (next_char, next_next_char) == ("*", "/")
                eof_reached = self.stream.is_truly_out_of_index()
                if is_comment_end:
                    self.consume(2)
                    if not eof_reached:
                        self.consume_comments()
                    return
                elif eof_reached:
                    self.parse_error()
                    self.consume(2)
                    return
                self.consume()

    def consume_a_numeric_token(self):
        current_char, next_char = self.stream.current_char, self.stream.next_char
        number_value, number_type = self.consume_a_number()
        second_next_char = self.stream.nth_next_char()
        third_next_char = self.stream.nth_next_char()
        if self.three_code_points_start_an_identifier(next_char, second_next_char, third_next_char):
            current_token = create_token("dimension-token")
            current_token.value = number_value
            current_token.type = number_type
            current_token.unit = self.consume_a_name()
            return current_token

        elif next_char == "%":
            self.consume()
            current_token = create_token("percentage-token")
            current_token.value = number_value
            return current_token

        else:
            current_token = create_token("number-token")
            current_token.value = number_value
            current_token.type = number_type
            return current_token

    def consume_an_ident_like_token(self):
        string = self.consume_a_name()
        is_url_function_start = string.lower() == "url" and self.stream.next_char == "("
        if is_url_function_start:
            self.consume(2)
            while self.stream.next_char in WHITESPACE:
                self.consume()

            next_char, next_next_char = self.stream.next_char, self.stream.nth_next_char()
            next_two_chars = (next_char, next_next_char)
            next_chars_form_string = True in [
                next_two_chars in [("'", "'"), ('"', '"')],
                next_char in ["'", '"'],
                next_char in WHITESPACE and next_next_char in ["'", '"']
            ]
            if next_chars_form_string:
                current_token = create_token("function-token")
                current_token.value = string
                return current_token
            else:
                current_token = self.consume_a_url_token()
                return current_token

        elif self.stream.next_char == "(":
            self.consume()
            current_token = create_token("function-token")
            current_token.value = string
            return current_token

        else:
            current_token = create_token("ident-token")
            current_token.value = string
            return current_token

    def consume_a_string_token(self, ending_char=None):
        if ending_char is None:
            ending_char = self.stream.current_char

        current_token = create_token("string-token")
        while True:
            current_char, next_char = self.consume()

            if current_char == ending_char:
                return current_token

            elif current_char == EOF:
                self.parse_error()
                return current_token

            elif current_char == NEWLINE:
                self.parse_error()
                self.stream.reconsuming = True
                current_token = create_token("bad-string-token")
                return current_token

            elif current_char == "\\":
                if next_char == EOF:
                    pass
                elif next_char == NEWLINE:
                    self.consume()
                else:
                    current_token.value += self.consume_an_escaped_code_point()

            else:
                current_token.value += current_char

    def consume_a_url_token(self):
        current_token = create_token("url-token")

        while self.stream.next_char in WHITESPACE:
            self.consume()

        while True:
            current_char, next_char = self.consume()

            if current_char == ")":
                return current_token

            elif current_char == EOF:
                self.parse_error()
                return current_token

            elif current_char in WHITESPACE:
                while self.stream.next_char in WHITESPACE:
                    current_char, next_char = self.consume()

                    if next_char in WHITESPACE + [EOF]:
                        if next_char == EOF:
                            self.parse_error()
                        self.consume()
                        return current_token
                    else:
                        self.consume_remnants_of_a_bad_url()
                        current_token = create_token("bad-url-token")
                        return current_token

            elif current_char in ["'", '"', "("] or is_non_printable_code_point(current_char):
                self.parse_error()
                self.consume_remnants_of_a_bad_url()
                current_token = create_token("bad-url-token")
                return current_token

            elif current_char == "\\":
                if self.two_code_points_are_valid_escape():
                    current_token.value += self.consume_an_escaped_code_point()
                else:
                    self.parse_error()
                    self.consume_remnants_of_a_bad_url()
                    current_token = create_token("bad-url-token")
                    return current_token

            else:
                current_token.value += current_char

    def consume_an_escaped_code_point(self):
        current_char, next_char = self.consume()

        if inside(ASCII_HEX_DIGIT, current_char):
            buffer = current_char
            for i in range(5):
                if inside(ASCII_HEX_DIGIT, next_char):
                    buffer += next_char
                    current_char, next_char = self.consume()
                else:
                    break

            if next_char in WHITESPACE:
                self.consume()
            code_point = int(buffer, base=16)
            if code_point == 0 or code_point > MAXIMUM_ALLOWED_CODE_POINT:
                return REPLACEMENT_CHARACTER
            else:
                return chr(code_point)

        elif current_char == EOF:
            self.parse_error()
            return REPLACEMENT_CHARACTER

        else:
            return current_char

    def two_code_points_are_valid_escape(self, char1=None, char2=None):
        if char1 is None:
            char1 = self.stream.current_char
        if char2 is None:
            char2 = self.stream.next_char

        if char1 != "\\":
            return False

        elif char2 == NEWLINE:
            return False

        else:  # yes i know this can be made better, but this way the readability matches the specs.
            return True

    def three_code_points_start_an_identifier(self, char1=None, char2=None, char3=None):
        if char1 is None:
            char1 = self.stream.current_char
        if char2 is None:
            char2 = self.stream.next_char
        if char3 is None:
            char3 = self.stream.nth_next_char()

        if char1 == "-":
            is_valid = True in [
                is_name_start_code_point(char2),
                char2 == "-",
                self.two_code_points_are_valid_escape(char2, char3)
            ]
            return is_valid

        elif is_name_start_code_point(char1):
            return True

        elif char1 == "\\":
            return self.two_code_points_are_valid_escape(char1, char2)

        else:
            return False

    def three_code_points_start_a_number(self, char1=None, char2=None, char3=None):
        if char1 is None:
            char1 = self.stream.current_char
        if char2 is None:
            char2 = self.stream.next_char
        if char3 is None:
            char3 = self.stream.nth_next_char()

        if char1 in ["+", "-"]:
            if inside(ASCII_DIGIT, char1):
                return True
            elif char2 == "." and inside(ASCII_DIGIT, char3):
                return True
            return False

        elif char1 == ".":
            return inside(ASCII_DIGIT, char2)

        elif inside(ASCII_DIGIT, char1):
            return True

        else:
            return False

    def consume_a_name(self):
        result = ""

        while True:
            current_char, next_char = self.consume()

            if is_name_code_point(current_char):
                result += current_char

            elif self.two_code_points_are_valid_escape():
                result += self.consume_an_escaped_code_point()

            else:
                self.stream.reconsuming = True
                return result

    def consume_a_number(self):
        num_repr, num_type = "", "integer"

        current_char, next_char = self.stream.current_char, self.stream.next_char

        if next_char in ["+", "-"]:
            current_char, next_char = self.consume()
            num_repr += current_char

        while inside(ASCII_DIGIT, next_char):
            current_char, next_char = self.consume()
            num_repr += current_char

        second_next_char = self.stream.nth_next_char()
        if next_char == "." and inside(ASCII_DIGIT, second_next_char):
            current_char, next_char = self.consume(2)
            num_repr += current_char + next_char
            num_type = "number"
            while inside(ASCII_DIGIT, next_char):
                current_char, next_char = self.consume()
                num_repr += current_char

        second_next_char = self.stream.nth_next_char()
        third_next_char = self.stream.nth_next_char()
        if next_char.lower() == "e" and \
                ((second_next_char in ["+", "-"] and inside(ASCII_DIGIT, third_next_char)) or
                 inside(ASCII_DIGIT, second_next_char)):
            current_char, next_char = self.consume()
            num_repr += current_char + next_char
            current_char, next_char = self.consume()  # to compensate for the used but still unconsumed next_char above
            num_type = "number"
            while inside(ASCII_DIGIT, next_char):
                current_char, next_char = self.consume()
                num_repr += current_char

        num_value = self.convert_string_to_a_number(num_repr)
        return num_value, num_type

    def convert_string_to_a_number(self, string):
        # TODO: IMPLEMENT THR REAL ALGORITHM FOR CONVERT STRING TO A NUMBER
        try:
            return int(string)
        except ValueError:
            try:
                return float(string)
            except ValueError:
                return 0

    def consume_remnants_of_a_bad_url(self):
        while True:
            current_char, next_char = self.consume()

            if current_char in [")", EOF]:
                return
            elif self.two_code_points_are_valid_escape():
                self.consume_an_escaped_code_point()

    def tokenize(self):
        while not self.stream.is_truly_out_of_index():
            self.output.append(self.consume_a_token())
